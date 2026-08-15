# Architecture

## Overview

```
Python public API: attributedict.AttributeDict (thin wrapper)
        ↓
C extension: attributedict._attributedict (module init)
        ↓
C type: AttributeDict_Type (PyTypeObject)
   - inherits from dict (PyDict_Type)            -> isinstance(d, dict) is True (C-002)
   - custom tp_getattro / tp_setattro            -> keys-win attribute access (FR-006)
   - custom tp_new / tp_init                     -> recursive nested conversion (FR-007)
   - GC slots (tp_traverse / tp_clear)           -> cycle safety (MEM-003)
```

## C API strategy (I-003)

**Decision: Limited API / Stable ABI (abi3), `Py_LIMITED_API` target 3.9,
wheel tag `cp39-abi3`** (D-002). This yields one wheel per platform across
CPython 3.9–3.14 (D-009, D-010).

**Decision: C subclass of `dict`** (D-001) rather than composition or a
reimplementation. The dict base provides the mapping protocol, views,
iteration, equality, pickling, and copy behavior for free; the type only
overrides attribute access and construction.

### Mapping-protocol approach

Because `AttributeDict_Type` subclasses `PyDict_Type`:

- `mp_length`, `mp_subscript`, `mp_ass_subscript`, `sq_contains` are
  **inherited** from dict — no overrides needed (FR-008).
- `tp_richcompare` is **inherited** from dict — equality is dict semantics
  (FR-011).
- `tp_hash` is inherited from dict — **unhashable** (FR-012, D-007).
- dict methods (`get`, `setdefault`, `update`, `pop`, `popitem`, `clear`,
  `copy`, `keys`, `items`, `values`, `fromkeys`) are inherited.
  `copy()` and `fromkeys()` are overridden to return `AttributeDict`
  (FR-009). `copy` returns `AttributeDict` via `tp_copy`-equivalent
  (dict's `copy` returns the same type for subclasses via `PyDict_Copy` —
  verified at implementation time in I-007).

### Overridden slots

| Slot | Purpose | Notes |
|---|---|---|
| `tp_getattro` | keys-win attribute read (FR-003/006) | see resolution order below |
| `tp_setattro` | attribute write/delete → mapping ops (FR-004/005) | |
| `tp_new` / `tp_init` | construction forms + recursive conversion (FR-002/007) | cycle-safe |
| `tp_repr` | `AttributeDict({...})` (FR-010) | |
| `tp_traverse` / `tp_clear` | GC participation (MEM-003) | portable pattern below |
| `tp_dealloc` | delegate to dict base | no double-free |

### GC strategy for a dict subclass under the Limited API

`PyObject_VisitManagedDict`/`PyObject_ClearManagedDict` are **not** public
Limited-API functions in 3.9–3.13. The portable pattern for a C type that
subclasses dict and holds references in the dict:

```c
static int
AttributeDict_traverse(AttributeDict *self, visitproc visit, void *arg)
{
    PyObject *items = PyDict_Items((PyObject *)self);
    if (items == NULL) { return -1; }
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(items); i++) {
        Py_VISIT(PyList_GET_ITEM(items, i));  /* visits key and value tuples */
    }
    Py_DECREF(items);
    return 0;
}
```

`tp_clear` clears the dict contents with `PyDict_Clear` (leaving an empty
AttributeDict). This is safe for cycles and correct across 3.9–3.14.
(At implementation time in I-004/I-005, verify whether the items-tuple
traversal fully covers key+value references; if not, iterate pairs directly.)

### Attribute resolution order (`tp_getattro`) — keys win

1. If the attribute name is a `str` that is a valid identifier
   (`PyUnicode_IsIdentifier`, available 3.9+) **and** a key exists
   (`PyDict_GetItemWithError`, available 3.9+): return the key's value.
2. Otherwise fall back to `PyObject_GenericGetAttr`.
3. If that raises `AttributeError`, propagate it.

This implements FR-006 (keys win) and FR-014 (non-identifier keys are not
reachable via attribute syntax).

### Attribute set/delete (`tp_setattro`)

- `d.name = v` → `PyDict_SetItem(self, name, v)` (FR-004).
- `del d.name` → `PyDict_DelItem(self, name)`; on `KeyError` re-raise as
  `AttributeError` (FR-005, deviation documented in spec 08).
- Names that are not identifiers: `PyDict_SetItem` still works for mapping
  syntax; attribute syntax simply never resolves them.

## Verified Limited-API availability (CPython 3.13 headers, 3.9+ target)

| API | Status |
|---|---|
| `PyDict_Type` (`PyAPI_DATA`) | ✅ public |
| `PyDict_GetItemWithError` | ✅ public |
| `PyDict_SetItem` / `PyDict_DelItem` / `PyDict_Contains` | ✅ public |
| `PyObject_GenericGetAttr` / `PyObject_GenericSetAttr` | ✅ public |
| `PyObject_GenericGetDict` | ✅ public |
| `PyUnicode_IsIdentifier` | ✅ public |
| `Py_ReprEnter` / `Py_ReprLeave` | ✅ public (repr recursion) |
| `Py_VISIT` / `Py_CLEAR` macros | ✅ public |
| `Py_TPFLAGS_BASETYPE`, `Py_TPFLAGS_HAVE_GC` | ✅ public |
| `PyObject_VisitManagedDict` / `PyObject_ClearManagedDict` | ❌ not public in 3.13 (use portable pattern) |
| `PyObject_GC_Visit` / `PyObject_GC_Clear` | ❌ not public (use `Py_VISIT`/`Py_CLEAR`) |

No required API is missing from the Limited API for 3.9+; the GC helpers use
the portable `Py_VISIT`/`Py_CLEAR` pattern instead.

## C source layout

```
src/attributedict/
├── __init__.py        # public re-export
├── py.typed
└── _attributedict.c   # module init + type definition
```

If complexity grows, split into `module.c`, `attributedict.c/.h`,
`conversion.c/.h`, `attributes.c/.h` — only if each file has a coherent
responsibility (D-002 maintainability).

## References

- spec 05 (system architecture), spec 09 (packaging), spec 07 (memory),
  decisions D-001/D-002/D-009/D-010/D-012.
