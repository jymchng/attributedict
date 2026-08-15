# Development

## Building from source

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e .[dev]
.venv/bin/python -m pytest
```

(Dev extras land in I-016; until then install `pytest` explicitly.)

## C object layout (I-004)

`AttributeDict` is a C type that **subclasses `dict`** (D-001). It therefore
uses the base `PyDictObject` storage: keys and values are owned by the dict
base. **No extra per-instance C struct is needed** (MEM-001).

```c
typedef struct {
    PyDictObject base;   /* all storage lives in the dict base */
} AttributeDictObject;
```

### Slot plan

| Slot | Implementation | Notes |
|---|---|---|
| `tp_base` | `&PyDict_Type` | `isinstance(d, dict)` True (C-002) |
| `tp_getattro` | keys-win lookup (FR-006) | I-008 |
| `tp_setattro` | mapping set/delete (FR-004/005) | I-008 |
| `tp_new` / `tp_init` | construction + recursive conversion (FR-002/007) | I-006 |
| `tp_repr` | `AttributeDict({...})` (FR-010) | I-009 |
| `tp_traverse` / `tp_clear` | portable GC pattern (MEM-003) | below |
| `tp_dealloc` | delegate to dict base dealloc (MEM-006) | no double-free |

### GC contract (MEM-003)

Because values can reference the AttributeDict (cycles), the type must
participate in cyclic GC. The portable Limited-API pattern:

```c
static int
AttributeDict_traverse(AttributeDictObject *self, visitproc visit, void *arg)
{
    PyObject *items = PyDict_Items((PyObject *)self);
    if (items == NULL) {
        return -1;
    }
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(items); i++) {
        Py_VISIT(PyList_GET_ITEM(items, i));  /* key+value tuple */
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

`tp_clear` empties the dict contents (no decref of borrowed refs — the dict
base owns them). This is correct for cycles and available in the Limited API
3.9–3.14. **Note:** `PyObject_VisitManagedDict`/`PyObject_ClearManagedDict`
are NOT public in 3.13 (verified in I-003); do not use them.

### Weakrefs

`dict` supports weakrefs; the subclass inherits that. Verify at I-005 that a
weakref to an AttributeDict works and that `tp_weaklistoffset` is inherited.
No custom weakref code expected.

## Refcount rules (MEM-002, MEM-004, MEM-005)

1. `tp_new` must return a **new reference** (caller owns it).
2. `tp_init` must not leak on failure: if recursive conversion fails
   mid-way, clear partial state before returning -1.
3. **Borrowed vs new**: never `Py_DECREF` a borrowed reference; incref
   before storing in a container; after `PyDict_SetItem`, decref the value
   if it was freshly created.
4. **Error paths**: every C function that can fail must not leave a stale
   exception on success; `PyErr_Occurred()` must be false after success.
   `PyErr_Clear()` only where a swallowed exception is intentional and
   documented.
5. **Dealloc**: delegate to the dict base dealloc (call
   `PyDict_Type.tp_dealloc`); never double-free.

## Code-review checklist (from spec 07)

- [ ] No `Py_DECREF` on borrowed references.
- [ ] `tp_new` returns a new reference; `tp_init` clears partial state on
      failure.
- [ ] `PyDict_SetItem` callers decref freshly-created values.
- [ ] `tp_traverse` visits keys AND values (via items tuples or equivalent).
- [ ] `tp_clear` clears the dict contents; no stale refs.
- [ ] `tp_dealloc` delegates to dict base; no double-free.
- [ ] No stale exception after successful operations.
- [ ] Recursive conversion is cycle-safe and leak-free on error paths.
- [ ] All used APIs are in the Limited API (see spec 05 table).
- [ ] Sanitizer (ASan/UBSan) jobs clean; stress tests pass.

## Testing

- `nox -s tests` — full suite (I-013).
- `nox -s coverage` — coverage report.
- Memory/sanitizer tests land in I-012.

## Sanitizers (I-012, MEM-008)

Build and run the suite under AddressSanitizer + UndefinedBehaviorSanitizer:

```bash
CFLAGS="-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer" \
LDFLAGS="-fsanitize=address,undefined" \
PYTHONMALLOC=malloc \
python setup.py build_ext --inplace

ASAN_OPTIONS="detect_leaks=1:abort_on_error=1" \
UBSAN_OPTIONS="halt_on_error=1" \
PYTHONMALLOC=malloc \
python -m pytest tests/
```

The CI job `.github/workflows/sanitizers.yml` runs this on every push/PR.
Any leak, use-after-free, or undefined behavior fails the job (R-003 gate).

## Weakrefs (MEM-009)

`dict` does not support weak references; `AttributeDict` matches dict — do
not expect `weakref.ref(AttributeDict())` to work.
