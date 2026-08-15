/* attributedict._attributedict -- C extension module (stub for I-001).

 * I-001 bootstrap: a minimal, buildable module so the packaging pipeline is
 * validated end-to-end early. The real AttributeDict type (a C subclass of
 * dict with custom tp_getattro/tp_setattro) is implemented in I-005+.
 *
 * This stub intentionally contains NO behavior. Do not extend it here;
 * type registration and abi3 flags land in I-005, mapping/attribute
 * semantics in I-006..I-011.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* Module docstring. */
PyDoc_STRVAR(module_doc,
"attributedict._attributedict: internal C implementation of AttributeDict.\n"
"\n"
"This is an implementation detail. Import the public API from\n"
"``attributedict`` instead.");

/* Module definition. */
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
    return m;
}
