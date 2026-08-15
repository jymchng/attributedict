/* attributedict._attributedict -- C implementation of AttributeDict.

 * The AttributeDict type is a C subclass of dict (PyDict_Type) with:
 *   - custom tp_getattro/tp_setattro  (keys-win resolution; I-008)
 *   - custom tp_init                  (recursive conversion; I-006)
 *   - custom tp_repr                  (AttributeDict({...}); I-009)
 *   - GC slots (tp_traverse/tp_clear) (portable Py_VISIT/Py_CLEAR pattern)
 *
 * ABI strategy (I-003, D-002): the wheel is tagged abi3 via
 * ``py_limited_api=True`` in setup.py (setuptools renames the artifact to
 * ``cp39-abi3``). The code deliberately uses only Stable-ABI functions and
 * the type-definition pattern that is compatible across 3.9-3.14. We do NOT
 * define ``Py_LIMITED_API`` here because that hides the concrete
 * ``PyTypeObject``/``PyDictObject`` layouts needed to define a static type;
 * the abi3 tag is produced by setuptools at build time.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <dictobject.h>

#ifdef PY_ATTRIBUTEDICT_TESTING
/* Test-only allocation-failure injection (I-023).
 *
 * Compiled in ONLY when the build defines PY_ATTRIBUTEDICT_TESTING (test
 * builds). Production wheels never define it, so no fault-injection code is
 * shipped. Mirrors CPython's own _testcapi.set_nomemory approach: setting a
 * non-negative count makes the next N allocation helper calls fail with
 * PyErr_NoMemory so every OOM branch in this file is deterministically
 * coverable by tests.
 */
static Py_ssize_t g_alloc_fail_count = -1;

static int
TestMallocFail(void)
{
    if (g_alloc_fail_count < 0) {
        return 0;
    }
    if (g_alloc_fail_count == 0) {
        PyErr_NoMemory();
        return 1;
    }
    g_alloc_fail_count--;
    return 0;
}

/* set_allocation_fail_count(n): n<0 disables; n>=0 lets n allocations
 * succeed then fails the (n+1)-th (so n=0 fails the first allocation). */
/* Returns 1 (with MemoryError set) if the injected failure fires. */
#define ALLOC_FAIL() (TestMallocFail())

/* Wraps an allocation so the injected failure can fire at every site. */
#define AD_ALLOC(expr) (ALLOC_FAIL() ? NULL : (expr))

static PyObject *
set_allocation_fail_count(PyObject *Py_UNUSED(self), PyObject *arg)
{
    Py_ssize_t n = PyLong_AsSsize_t(arg);
    if (n == -1 && PyErr_Occurred()) {
        return NULL;
    }
    g_alloc_fail_count = n;
    Py_RETURN_NONE;
}
#else   /* !PY_ATTRIBUTEDICT_TESTING: production builds inject nothing. */
#define ALLOC_FAIL() (0)
#define AD_ALLOC(expr) (expr)
#endif  /* PY_ATTRIBUTEDICT_TESTING */

/* Forward declaration (the type is defined near the end of the file but the
 * conversion helpers reference it). */
static PyTypeObject AttributeDict_Type;

/* ------------------------------------------------------------------------ */
/* Type object                                                               */
/* ------------------------------------------------------------------------ */

/* The object layout: subclass of dict, so all storage lives in the dict
 * base (MEM-001). No extra per-instance struct. */
typedef struct {
    PyDictObject base;
} AttributeDictObject;

/* GC: traverse the dict items (keys and values) via the portable pattern
 * (MEM-003). PyObject_VisitManagedDict is NOT public in the Limited API. */
static int
AttributeDict_traverse(AttributeDictObject *self, visitproc visit, void *arg)
{
    PyObject *items = AD_ALLOC(PyDict_Items((PyObject *)self));
    if (items == NULL) {
        return -1;
    }
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(items); i++) {
        Py_VISIT(PyList_GET_ITEM(items, i));
    }
    Py_DECREF(items);
    return 0;
}

/* GC: clear the dict contents (MEM-003). */
static int
AttributeDict_clear(AttributeDictObject *self)
{
    PyDict_Clear((PyObject *)self);
    return 0;
}

/* Dealloc: delegate to the dict base dealloc (MEM-006).
 *
 * NOTE: call PyDict_Type.tp_dealloc directly (not Py_TYPE(self)->tp_base->tp_dealloc)
 * to avoid infinite recursion when self is a subclass instance (subclass
 * tp_base is AttributeDict_Type with tp_dealloc == this function). */
static void
AttributeDict_dealloc(AttributeDictObject *self)
{
    PyDict_Type.tp_dealloc((PyObject *)self);
}

/* ------------------------------------------------------------------------ */
/* Recursive nested conversion (FR-007, MEM-007)                             */
/* ------------------------------------------------------------------------ */

/* Conversion context: a dict mapping id(object) -> converted object. It is
 * seeded with the top-level source before conversion so self-referential
 * structures reuse the in-progress AttributeDict instead of recursing. */

static int
AttributeDict_ctx_put(PyObject *ctx, PyObject *obj, PyObject *converted)
{
    PyObject *key = AD_ALLOC(PyLong_FromVoidPtr(obj));
    if (key == NULL) {
        return -1;
    }
    int rc = PyDict_SetItem(ctx, key, converted);
    Py_DECREF(key);
    return rc;
}

/* Returns a borrowed reference to the converted object, or NULL. On NULL,
 * PyErr_Occurred() distinguishes "not found" (false) from a real error. */
static PyObject *
AttributeDict_ctx_get(PyObject *ctx, PyObject *obj)
{
    PyObject *key = PyLong_FromVoidPtr(obj);
    if (key == NULL) {
        return NULL;
    }
    PyObject *existing = PyDict_GetItemWithError(ctx, key);
    Py_DECREF(key);
    return existing;
}

/* Create an empty AttributeDict without running tp_init (avoids recursion).
 * The caller owns the new reference. */
static PyObject *
AttributeDict_NewEmpty(void)
{
    PyObject *args = AD_ALLOC(PyTuple_New(0));
    if (args == NULL) {
        return NULL;
    }
    PyObject *nd = AttributeDict_Type.tp_new(&AttributeDict_Type, args, NULL);
    Py_DECREF(args);
    return nd;
}

/* Recursively convert *value* per FR-007:
 *   - dict (but NOT an already-converted AttributeDict) -> AttributeDict
 *   - list/tuple -> same container type with converted elements
 *   - set/frozenset -> NOT converted (A-008)
 *   - anything else -> unchanged (incref'd)
 * Cycle-safe: in-progress conversions are tracked in *ctx*.
 * Returns a new reference, or NULL with an exception set. */
static PyObject *
AttributeDict_ConvertValue(PyObject *value, PyObject *ctx)
{
#ifdef PY_ATTRIBUTEDICT_TESTING
    if (ALLOC_FAIL()) {
        return NULL;
    }
#endif
    if (PyObject_TypeCheck(value, &AttributeDict_Type)) {
        /* Already converted: share it (idempotent; shallow-copy semantics). */
        Py_INCREF(value);
        return value;
    }

    if (PyDict_Check(value)) {
        PyObject *existing = AttributeDict_ctx_get(ctx, value);
        if (existing != NULL) {
            Py_INCREF(existing);
            return existing;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }

        PyObject *nd = AttributeDict_NewEmpty();
        if (nd == NULL) {
            return NULL;
        }
        /* Register BEFORE filling so cycles resolve to *nd*. */
        if (AttributeDict_ctx_put(ctx, value, nd) < 0) {
            goto fail;
        }

        /* Iterate key/value pairs directly (PyDict_Next): keys are already
         * hashed in the source dict, so no per-item error is possible and no
         * "key vanished" race guard is needed. Conversion writes only into
         * *nd* (never mutating the source), so iteration stays valid. */
        Py_ssize_t pos = 0;
        PyObject *k, *v;
        while (PyDict_Next(value, &pos, &k, &v)) {
            PyObject *cv = AttributeDict_ConvertValue(v, ctx);
            if (cv == NULL) {
                goto fail;
            }
            int rc = PyDict_SetItem(nd, k, cv);
            Py_DECREF(cv);
            if (rc < 0) {
                goto fail;
            }
        }
        return nd;

fail:
        Py_DECREF(nd);
        return NULL;
    }

    if (PyList_Check(value)) {
        Py_ssize_t n = PyList_GET_SIZE(value);
        PyObject *nl = AD_ALLOC(PyList_New(n));
        if (nl == NULL) {
            return NULL;
        }
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *cv = AttributeDict_ConvertValue(PyList_GET_ITEM(value, i), ctx);
            if (cv == NULL) {
                Py_DECREF(nl);
                return NULL;
            }
            PyList_SET_ITEM(nl, i, cv);  /* steals the reference */
        }
        return nl;
    }

    if (PyTuple_Check(value)) {
        Py_ssize_t n = PyTuple_GET_SIZE(value);
        PyObject *nt = AD_ALLOC(PyTuple_New(n));
        if (nt == NULL) {
            return NULL;
        }
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *cv = AttributeDict_ConvertValue(PyTuple_GET_ITEM(value, i), ctx);
            if (cv == NULL) {
                Py_DECREF(nt);
                return NULL;
            }
            PyTuple_SET_ITEM(nt, i, cv);  /* steals the reference */
        }
        return nt;
    }

    Py_INCREF(value);
    return value;
}

/* ------------------------------------------------------------------------ */
/* Construction (FR-002) + conversion (FR-007)                               */
/* ------------------------------------------------------------------------ */

/* tp_new: delegate to the dict base (PyDict_Type.tp_new), which handles
 * every construction form: (), (mapping), (iterable_of_pairs), (**kwargs),
 * (mapping, **kwargs).
 *
 * NOTE: call PyDict_Type.tp_new directly (not type->tp_base->tp_new) to
 * avoid infinite recursion when *type* is a subclass of AttributeDict
 * (whose tp_base is AttributeDict_Type with tp_new == this function). */
static PyObject *
AttributeDict_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return PyDict_Type.tp_new(type, args, kwds);
}

/* tp_init: run the base init (populates self per FR-002), then convert all
 * contained values recursively in place (FR-007), cycle-safe.
 *
 * NOTE: call PyDict_Type.tp_init directly (not Py_TYPE(self)->tp_base->tp_init)
 * to avoid infinite recursion when self is an instance of a *subclass* of
 * AttributeDict (the subclass's tp_base is AttributeDict_Type, whose tp_init
 * is this function). */
static int
AttributeDict_init(AttributeDictObject *self, PyObject *args, PyObject *kwds)
{
    if (PyDict_Type.tp_init != NULL) {
        if (PyDict_Type.tp_init((PyObject *)self, args, kwds) < 0) {
            return -1;
        }
    }

    PyObject *ctx = AD_ALLOC(PyDict_New());
    if (ctx == NULL) {
        return -1;
    }

    /* Seed the context with the source mapping (if construction is from a
     * single mapping) so a self-referential source resolves to *self*. */
    if (PyTuple_GET_SIZE(args) > 0) {
        PyObject *src = PyTuple_GET_ITEM(args, 0);
        if (PyDict_Check(src) && src != (PyObject *)self) {
            if (AttributeDict_ctx_put(ctx, src, (PyObject *)self) < 0) {
                Py_DECREF(ctx);
                return -1;
            }
        }
    }

    /* Convert each value in place. Iterate key/value pairs directly: only
     * the value slot of an existing key changes (PyDict_SetItem on an
     * already-present key never resizes/reorders), so PyDict_Next stays
     * valid and no "key vanished" guard is needed. */
    Py_ssize_t pos = 0;
    PyObject *k, *v;
    while (PyDict_Next((PyObject *)self, &pos, &k, &v)) {
        PyObject *cv = AttributeDict_ConvertValue(v, ctx);
        if (cv == NULL) {
            goto fail;
        }
        int rc = PyDict_SetItem((PyObject *)self, k, cv);
        Py_DECREF(cv);
        if (rc < 0) {
            goto fail;
        }
    }
    Py_DECREF(ctx);
    return 0;

fail:
    Py_DECREF(ctx);
    return -1;
}

/* ------------------------------------------------------------------------ */
/* Attribute get/set/delete (I-008)                                          */
/* ------------------------------------------------------------------------ */

/* Attribute get (FR-003 / FR-006: keys win).
 *
 * Resolution order (spec 05):
 *   1. If the name is a str that is a valid identifier AND a mapping key,
 *      return the key's value (keys win over type attributes/methods).
 *   2. Otherwise fall back to PyObject_GenericGetAttr (type attributes,
 *      descriptors, methods, dunders).
 *   3. If that raises AttributeError, propagate it.
 *
 * Non-identifier keys are NOT reachable via attribute syntax (FR-014).
 */
static PyObject *
AttributeDict_getattro(AttributeDictObject *self, PyObject *name)
{
    if (PyUnicode_Check(name) && PyUnicode_IsIdentifier(name)) {
        /* A str key is always hashable, so PyDict_GetItem cannot raise:
         * NULL unambiguously means "key absent" -> fall through. */
        PyObject *value = PyDict_GetItem((PyObject *)self, name);
        if (value != NULL) {
            Py_INCREF(value);
            return value;
        }
    }
    return PyObject_GenericGetAttr((PyObject *)self, name);
}

/* Attribute set/delete (FR-004/005).
 *
 *   d.name = v   ->  d["name"] = v           (always mapping assignment)
 *   del d.name   ->  delete key "name"; AttributeError if absent
 *
 * The AttributeError on delete of a missing key is a documented deviation
 * from the mapping form (del d["missing"] -> KeyError) per spec 08.
 */
static int
AttributeDict_setattro(AttributeDictObject *self, PyObject *name,
                       PyObject *value)
{
    if (value != NULL) {
        return PyDict_SetItem((PyObject *)self, name, value);
    }
    /* value == NULL means attribute deletion. */
    if (PyDict_DelItem((PyObject *)self, name) < 0) {
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();  /* intentional: surface as AttributeError (MEM-004) */
            PyErr_Format(PyExc_AttributeError,
                         "%R object has no attribute %R",
                         Py_TYPE(self), name);
        }
        return -1;
    }
    return 0;
}

/* copy() override (FR-009/013): the dict base's copy() returns a plain dict
 * for subclasses; the spec requires AttributeDict-typed shallow copy. */
static PyObject *
AttributeDict_copy(AttributeDictObject *self, PyObject *Py_UNUSED(ignored))
{
    PyObject *nd = AttributeDict_NewEmpty();
    if (nd == NULL) {
        return NULL;
    }
    if (PyDict_Update(nd, (PyObject *)self) < 0) {
        Py_DECREF(nd);
        return NULL;
    }
    return nd;
}

PyDoc_STRVAR(attributedict_copy_doc,
"copy() -> AttributeDict\n"
"\n"
"Return a shallow copy of the mapping as an AttributeDict.");

/* __reduce__ (FR-013): enable pickle across all protocols, cycle-safe.
 *
 * Use the 5-tuple form (reconstructor, args, state, listitems, dictitems):
 * returning iter(self.items()) as the dictitems lets pickle serialize items
 * lazily through its memo, so self-referential structures reduce without
 * recursion (mirrors CPython dict.__reduce_ex__).
 */
static PyObject *
AttributeDict_reduce(AttributeDictObject *self, PyObject *Py_UNUSED(ignored))
{
#ifdef PY_ATTRIBUTEDICT_TESTING
    if (ALLOC_FAIL()) {
        return NULL;
    }
#endif
    PyObject *module = AD_ALLOC(PyImport_ImportModule("attributedict._pickle_support"));
    if (module == NULL) {
        return NULL;
    }
    PyObject *func = AD_ALLOC(PyObject_GetAttrString(module, "reconstruct"));
    Py_DECREF(module);
    if (func == NULL) {
        return NULL;
    }

    PyObject *args = AD_ALLOC(Py_BuildValue("(O)", (PyObject *)Py_TYPE(self)));
    if (args == NULL) {
        Py_DECREF(func);
        return NULL;
    }

    PyObject *items_iter = AD_ALLOC(PyObject_GetIter(PyDict_Items((PyObject *)self)));
    if (items_iter == NULL) {
        Py_DECREF(func);
        Py_DECREF(args);
        return NULL;
    }

    PyObject *tuple = AD_ALLOC(Py_BuildValue("(OOOOO)",
                                    func,     /* callable */
                                    args,     /* args */
                                    Py_None,  /* state */
                                    Py_None,  /* listitems */
                                    items_iter /* dictitems */));
    Py_DECREF(func);
    Py_DECREF(args);
    Py_DECREF(items_iter);
    return tuple;
}

PyDoc_STRVAR(attributedict_reduce_doc,
"__reduce__() -- pickle support (preserves type and cycles).");

static PyMethodDef AttributeDict_methods[] = {
    {"copy", (PyCFunction)AttributeDict_copy, METH_NOARGS,
     attributedict_copy_doc},
    {"__reduce__", (PyCFunction)AttributeDict_reduce, METH_NOARGS,
     attributedict_reduce_doc},
    {NULL, NULL, 0, NULL},
};

/* Repr (FR-010): produce "AttributeDict({...})".
 *
 * Cycle handling mirrors dict: use Py_ReprEnter/Py_ReprLeave so recursive
 * structures render with "..." instead of recursing forever.
 */
static PyObject *
AttributeDict_repr(AttributeDictObject *self)
{
#ifdef PY_ATTRIBUTEDICT_TESTING
    if (ALLOC_FAIL()) {
        return NULL;
    }
#endif
    if (Py_ReprEnter((PyObject *)self) != 0) {
        /* != 0 means recursion detected (1) or error (-1):
         * recursion -> render "..."; error -> propagate.
         * In BOTH cases Py_ReprLeave must NOT be called (nothing entered,
         * or the recursion guard is already held by an outer frame).
         * On injected/OOM failure of the literal, return NULL directly. */
#ifdef PY_ATTRIBUTEDICT_TESTING
        if (ALLOC_FAIL()) {
            return NULL;
        }
#endif
        return PyUnicode_FromString("AttributeDict({...})");
    }

    PyObject *parts = AD_ALLOC(PyList_New(0));
    if (parts == NULL) {
        Py_ReprLeave((PyObject *)self);
        return NULL;
    }

    /* Iterate key/value pairs directly; no per-item error possible. */
    Py_ssize_t pos = 0;
    PyObject *k, *v;
    while (PyDict_Next((PyObject *)self, &pos, &k, &v)) {
        PyObject *kr = AD_ALLOC(PyObject_Repr(k));
        PyObject *vr = AD_ALLOC(PyObject_Repr(v));
        if (kr == NULL || vr == NULL) {
            Py_XDECREF(kr);
            Py_XDECREF(vr);
            Py_DECREF(parts);
            Py_ReprLeave((PyObject *)self);
            return NULL;
        }
        PyObject *item = AD_ALLOC(PyUnicode_FromFormat("%U: %U", kr, vr));
        Py_DECREF(kr);
        Py_DECREF(vr);
        if (item == NULL) {
            Py_DECREF(parts);
            Py_ReprLeave((PyObject *)self);
            return NULL;
        }
        if (PyList_Append(parts, item) < 0) {
            Py_DECREF(item);
            Py_DECREF(parts);
            Py_ReprLeave((PyObject *)self);
            return NULL;
        }
        Py_DECREF(item);
    }

    PyObject *sep = AD_ALLOC(PyUnicode_FromString(", "));
    if (sep == NULL) {
        Py_DECREF(parts);
        Py_ReprLeave((PyObject *)self);
        return NULL;
    }
    PyObject *body = AD_ALLOC(PyUnicode_Join(sep, parts));
    Py_DECREF(sep);
    Py_DECREF(parts);
    if (body == NULL) {
        Py_ReprLeave((PyObject *)self);
        return NULL;
    }

    PyObject *result = AD_ALLOC(PyUnicode_FromFormat("AttributeDict({%U})", body));
    Py_DECREF(body);
    Py_ReprLeave((PyObject *)self);
    return result;
}

PyDoc_STRVAR(attributedict_doc,
"AttributeDict(dict) -- a dict subclass whose keys are also accessible\n"
"as attributes (d['host'] == d.host). Keys win over type attributes.");

static PyTypeObject AttributeDict_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "attributedict._attributedict.AttributeDict",
    .tp_basicsize = sizeof(AttributeDictObject),
    .tp_dealloc = (destructor)AttributeDict_dealloc,
    .tp_repr = (reprfunc)AttributeDict_repr,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = attributedict_doc,
    .tp_traverse = (traverseproc)AttributeDict_traverse,
    .tp_clear = (inquiry)AttributeDict_clear,
    .tp_methods = AttributeDict_methods,
    .tp_getattro = (getattrofunc)AttributeDict_getattro,
    .tp_setattro = (setattrofunc)AttributeDict_setattro,
    .tp_init = (initproc)AttributeDict_init,
    .tp_new = AttributeDict_new,
};

/* ------------------------------------------------------------------------ */
/* Module                                                                    */
/* ------------------------------------------------------------------------ */

PyDoc_STRVAR(module_doc,
"attributedict._attributedict: internal C implementation of AttributeDict.\n"
"\n"
"This is an implementation detail. Import the public API from\n"
"``attributedict`` instead.");

static struct PyModuleDef attributedict_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "attributedict._attributedict",
    .m_doc = module_doc,
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit__attributedict(void)
{
    PyObject *m = AD_ALLOC(PyModule_Create(&attributedict_module));
    if (m == NULL) {
        return NULL;
    }

    AttributeDict_Type.tp_base = &PyDict_Type;
    if (PyType_Ready(&AttributeDict_Type) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&AttributeDict_Type);
    if (PyModule_AddObject(m, "AttributeDict", (PyObject *)&AttributeDict_Type) < 0) {
        Py_DECREF(&AttributeDict_Type);
        Py_DECREF(m);
        return NULL;
    }

#ifdef PY_ATTRIBUTEDICT_TESTING
    {
        static PyMethodDef testing_methods[] = {
            {"set_allocation_fail_count", set_allocation_fail_count,
             METH_O, "Set the allocation-failure counter (test builds only)."},
            {NULL, NULL, 0, NULL},
        };
        if (PyModule_AddFunctions(m, testing_methods) < 0) {
            Py_DECREF(m);
            return NULL;
        }
    }
#endif

    return m;
}
