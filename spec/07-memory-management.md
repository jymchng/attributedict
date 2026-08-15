# 07 — Memory Management

## Purpose

The reference-counting, GC, and memory-safety contract for the C extension.

## Scope

Refcount rules, GC participation, error-path discipline, sanitizer strategy.

## C object layout (I-004)

`AttributeDict` is a C type that subclasses `dict` (D-001):

```c
typedef struct {
    PyDictObject base;   /* all storage lives in the dict base */
} AttributeDictObject;
```

No extra per-instance C struct; keys/values are owned by the dict base
(MEM-001).

## Requirements

- MEM-001 The type is a C subclass of `dict`; all key/value references are
  owned by the dict base. No custom storage that duplicates ownership.
- MEM-002 `tp_new`/`tp_init` follow CPython refcount rules: `tp_new` returns
  a new reference; `tp_init` must not leak on failure (clear partial state).
- MEM-003 GC participation: implement `tp_traverse`/`tp_clear` using the
  portable `Py_VISIT`/`Py_CLEAR` pattern over the dict items (the
  `PyObject_VisitManagedDict`/`PyObject_ClearManagedDict` helpers are NOT
  public in the Limited API as of 3.13 — verified in I-003):

  ```c
  static int
  AttributeDict_traverse(AttributeDictObject *self, visitproc visit, void *arg)
  {
      PyObject *items = PyDict_Items((PyObject *)self);
      if (items == NULL) { return -1; }
      for (Py_ssize_t i = 0; i < PyList_GET_SIZE(items); i++) {
          Py_VISIT(PyList_GET_ITEM(items, i));
      }
      Py_DECREF(items);
      return 0;
  }

  static int
  AttributeDict_clear(AttributeDictObject *self)
  {
      PyDict_Clear((PyObject *)self);
      return 0;
  }
  ```

- MEM-004 Error paths: every C function that can fail must not leave a stale
  exception; on success, `PyErr_Occurred()` must be false. Use
  `PyErr_Clear()` only where a swallowed exception is intentional and
  documented.
- MEM-005 Borrowed vs new references: never decref borrowed references;
  incref before storing in a container; decref after `PyDict_SetItem` if the
  reference was newly created.
- MEM-006 Deallocation: `tp_dealloc` delegates to the dict base dealloc
  (`PyDict_Type.tp_dealloc`); no double-free.
- MEM-007 Recursive conversion helper: must be cycle-safe and leak-free on
  every branch (including the exception path mid-conversion).
- MEM-008 Sanitizers: CI jobs build with AddressSanitizer and
  UndefinedBehaviorSanitizer (via `-fsanitize=address,undefined` with a
  debug CPython where available) and run the test suite + a stress test that
  constructs/destroys many AttributeDicts and cyclic structures.

## Weakrefs

`dict` supports weakrefs; the subclass inherits that. Verify at I-005 that a
weakref to an AttributeDict works and `tp_weaklistoffset` is inherited. No
custom weakref code expected.

## Code-review checklist

- [ ] No `Py_DECREF` on borrowed references.
- [ ] `tp_new` returns a new reference; `tp_init` clears partial state on
      failure.
- [ ] `PyDict_SetItem` callers decref freshly-created values.
- [ ] `tp_traverse` visits keys AND values.
- [ ] `tp_clear` clears the dict contents; no stale refs.
- [ ] `tp_dealloc` delegates to dict base; no double-free.
- [ ] No stale exception after successful operations.
- [ ] Recursive conversion cycle-safe and leak-free on error paths.
- [ ] All used APIs in the Limited API (spec 05 table).
- [ ] Sanitizer jobs clean; stress tests pass.

## Testing

- Repeated construction/destruction (refcount/leak smoke).
- Cyclic structures (self-reference) garbage-collected without leaks.
- Stress: create/delete thousands of objects; assert refcount stability.
- Sanitizer jobs must be clean.

## Cross-references

- 05-system-architecture, 10-testing, 13-ci, decisions.md,
  docs/development.md.
