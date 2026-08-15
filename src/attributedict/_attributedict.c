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
    PyObject *items = PyDict_Items((PyObject *)self);
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

/* Dealloc: delegate to the dict base dealloc (MEM-006). */
static void
AttributeDict_dealloc(AttributeDictObject *self)
{
    PyTypeObject *base = Py_TYPE(self)->tp_base;
    if (base != NULL && base->tp_dealloc != NULL) {
        base->tp_dealloc((PyObject *)self);
    }
    else {
        PyObject_Del(self);
    }
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
    PyObject *key = PyLong_FromVoidPtr(obj);
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
    PyObject *args = PyTuple_New(0);
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
            Py_DECREF(nd);
            return NULL;
        }

        PyObject *keys = PyDict_Keys(value);
        if (keys == NULL) {
            Py_DECREF(nd);
            return NULL;
        }
        Py_ssize_t n = PyList_GET_SIZE(keys);
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *k = PyList_GET_ITEM(keys, i);
            PyObject *v = PyDict_GetItemWithError(value, k);
            if (v == NULL) {
                if (!PyErr_Occurred()) {
                    PyErr_SetString(PyExc_RuntimeError,
                                    "key vanished during conversion");
                }
                Py_DECREF(keys);
                Py_DECREF(nd);
                return NULL;
            }
            PyObject *cv = AttributeDict_ConvertValue(v, ctx);
            if (cv == NULL) {
                Py_DECREF(keys);
                Py_DECREF(nd);
                return NULL;
            }
            int rc = PyDict_SetItem(nd, k, cv);
            Py_DECREF(cv);
            if (rc < 0) {
                Py_DECREF(keys);
                Py_DECREF(nd);
                return NULL;
            }
        }
        Py_DECREF(keys);
        return nd;
    }

    if (PyList_Check(value)) {
        Py_ssize_t n = PyList_GET_SIZE(value);
        PyObject *nl = PyList_New(n);
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
        PyObject *nt = PyTuple_New(n);
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

/* tp_new delegates to the dict base, which handles every construction form:
 * (), (mapping), (iterable_of_pairs), (**kwargs), (mapping, **kwargs). */
static PyObject *
AttributeDict_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return type->tp_base->tp_new(type, args, kwds);
}

/* tp_init: run the base init (populates self per FR-002), then convert all
 * contained values recursively in place (FR-007), cycle-safe. */
static int
AttributeDict_init(AttributeDictObject *self, PyObject *args, PyObject *kwds)
{
    PyTypeObject *base = Py_TYPE(self)->tp_base;
    if (base->tp_init != NULL) {
        if (base->tp_init((PyObject *)self, args, kwds) < 0) {
            return -1;
        }
    }

    PyObject *ctx = PyDict_New();
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

    /* Convert each value in place. Iterate over a snapshot of keys because
     * conversion may (in the cycle case) insert into nested objects only,
     * not into self; the snapshot guards against any reentrancy anyway. */
    PyObject *keys = PyDict_Keys((PyObject *)self);
    if (keys == NULL) {
        Py_DECREF(ctx);
        return -1;
    }
    Py_ssize_t n = PyList_GET_SIZE(keys);
    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *k = PyList_GET_ITEM(keys, i);
        PyObject *v = PyDict_GetItemWithError((PyObject *)self, k);
        if (v == NULL) {
            if (!PyErr_Occurred()) {
                PyErr_SetString(PyExc_RuntimeError,
                                "key vanished during construction");
            }
            Py_DECREF(keys);
            Py_DECREF(ctx);
            return -1;
        }
        PyObject *cv = AttributeDict_ConvertValue(v, ctx);
        if (cv == NULL) {
            Py_DECREF(keys);
            Py_DECREF(ctx);
            return -1;
        }
        int rc = PyDict_SetItem((PyObject *)self, k, cv);
        Py_DECREF(cv);
        if (rc < 0) {
            Py_DECREF(keys);
            Py_DECREF(ctx);
            return -1;
        }
    }
    Py_DECREF(keys);
    Py_DECREF(ctx);
    return 0;
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
        PyObject *value = PyDict_GetItemWithError((PyObject *)self, name);
        if (value != NULL) {
            Py_INCREF(value);
            return value;
        }
        if (PyErr_Occurred()) {
            /* e.g. unhashable name -- propagate (MEM-004) */
            return NULL;
        }
        /* Key absent: fall through to generic lookup. */
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

static PyMethodDef AttributeDict_methods[] = {
    {"copy", (PyCFunction)AttributeDict_copy, METH_NOARGS,
     attributedict_copy_doc},
    {NULL, NULL, 0, NULL},
};

/* Repr placeholder until I-009: use dict's repr semantics by delegating to
 * the base tp_repr via the generic path. (Overridden in I-009.) */

PyDoc_STRVAR(attributedict_doc,
"AttributeDict(dict) -- a dict subclass whose keys are also accessible\n"
"as attributes (d['host'] == d.host). Keys win over type attributes.");

static PyTypeObject AttributeDict_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "attributedict._attributedict.AttributeDict",
    .tp_basicsize = sizeof(AttributeDictObject),
    .tp_dealloc = (destructor)AttributeDict_dealloc,
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
    PyObject *m = PyModule_Create(&attributedict_module);
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

    return m;
}
