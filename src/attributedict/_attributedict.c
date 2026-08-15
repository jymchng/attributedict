/* attributedict._attributedict -- C implementation of AttributeDict (I-005).

 * The AttributeDict type is a C subclass of dict (PyDict_Type) with:
 *   - custom tp_getattro/tp_setattro  (keys-win resolution; lands in I-008)
 *   - custom tp_new/tp_init           (recursive conversion; lands in I-006)
 *   - custom tp_repr                  (AttributeDict({...}); lands in I-009)
 *   - GC slots (tp_traverse/tp_clear) (portable Py_VISIT/Py_CLEAR pattern)
 *
 * This file implements the module skeleton + type registration + GC slots.
 * Behavior slots are wired but minimally functional until their issues land.
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

/* Construction: for I-005 this is the plain dict new (subclass-aware).
 * Recursive conversion semantics land in I-006. */
static PyObject *
AttributeDict_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return type->tp_base->tp_new(type, args, kwds);
}

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
    .tp_getattro = (getattrofunc)AttributeDict_getattro,
    .tp_setattro = (setattrofunc)AttributeDict_setattro,
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
