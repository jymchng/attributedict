# Development

## Building from source

```bash
uv venv.venv
uv pip install --python.venv/bin/python -e.[dev]
.venv/bin/python -m pytest
```

(Dev extras aren't wired up yet; until then install `pytest` explicitly.)

## C object layout 

`AttributeDict` is a C type that **subclasses `dict`**. It therefore
uses the base `PyDictObject` storage: keys and values are owned by the dict
base. **No extra per-instance C struct is needed**.

```c
typedef struct {
 PyDictObject base; /* all storage lives in the dict base */
} AttributeDictObject;
```

### Slot plan

| Slot | Implementation | Notes |
|---|---|---|
| `tp_base` | `&PyDict_Type` | `isinstance(d, dict)` True |
| `tp_getattro` | keys-win lookup | |
| `tp_setattro` | mapping set/delete | |
| `tp_new` / `tp_init` | construction + recursive conversion | |
| `tp_repr` | `AttributeDict({...})` | |
| `tp_traverse` / `tp_clear` | portable GC pattern | below |
| `tp_dealloc` | delegate to dict base dealloc | no double-free |

### GC contract 

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
 Py_VISIT(PyList_GET_ITEM(items, i)); /* key+value tuple */
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
are NOT public in 3.13 (verified in ); do not use them.

### Weakrefs

`dict` supports weakrefs; the subclass inherits that. Verify at that a
weakref to an AttributeDict works and that `tp_weaklistoffset` is inherited.
No custom weakref code expected.

## Refcount rules 

1. `tp_new` must return a **new reference** (caller owns it).
2. `tp_init` must not leak on failure: if recursive conversion fails
 mid-way, clear partial state before returning -1.
3. **Borrowed vs new**: never `Py_DECREF` a borrowed reference; incref
 before storing in a container; after `PyDict_SetItem`, decref the value
 if it was freshly created.
4. **Error paths**: every C function that can fail must not leave a stale
 exception on success; `PyErr_Occurred` must be false after success.
 `PyErr_Clear` only where a swallowed exception is intentional and
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

- `nox -s tests` — full suite.
- `nox -s coverage` — coverage report.
- Memory/sanitizer tests land in the sanitizers CI job.

## Sanitizers 

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
Any leak, use-after-free, or undefined behavior fails the job ( gate).

## Weakrefs 

`dict` does not support weak references; `AttributeDict` matches dict — do
not expect `weakref.ref(AttributeDict)` to work.

## Development tooling 

Reproducible sessions via `nox`:

```bash
nox -s tests # pytest across 3.9-3.13
nox -s lint # ruff check
nox -s format # ruff format --check
nox -s typecheck # mypy (strict)
nox -s coverage # pytest --cov (gate: 80%)
nox -s build # sdist + abi3 wheel
nox -s benchmarks # benchmarks/bench.py
```

pre-commit hooks (ruff, ruff-format, mypy, end-of-file, trailing-whitespace):

```bash
pre-commit install
pre-commit run --all-files
```

Quality gates (all must pass): `ruff check` clean, `ruff format --check`
clean, `mypy` clean, `pytest` green, coverage >= 80%.

Typing honesty : the C extension has no stubs; mypy is configured
with `ignore_missing_imports` for `attributedict._attributedict`. Attribute
access cannot be fully typed statically; this limitation is documented.

## CI 

GitHub Actions workflows (all least-privilege):

- `tests.yml` — build + pytest matrix: CPython 3.9–3.13 on ubuntu; 3.13 on
 windows; 3.11/3.13 on macos (sensible matrix).
- `lint.yml` — ruff check, ruff format --check, mypy (strict).
- `sanitizers.yml` — ASan/UBSan debug build + full suite + stress.
- `wheels.yml` — cibuildwheel abi3 matrix (manylinux x86_64+aarch64, macOS
 arm64+x86_64, Windows x86_64) + per-wheel smoke validation.
- `docs.yml` — internal link validation + README example check.
- `release.yml` — manual-trigger; builds sdist + wheels, hashes artifacts,
 creates a GitHub Release (draft). No PyPI auto-publish.

Sanitizer and lint jobs gate merges; wheels validate artifacts.

## C-extension coverage 

The C extension `_attributedict.c` is measured with gcov. The CI job builds
with the **test-only** `PY_ATTRIBUTEDICT_TESTING` macro so the deterministic
allocation-failure tests (`tests/test_failinject.py`) can run and cover the
OOM branches:

```bash
# clean instrumented build (IMPORTANT: remove stale.so first)
rm -f src/attributedict/*.so
CFLAGS="-O0 --coverage -fno-omit-frame-pointer -DPY_ATTRIBUTEDICT_TESTING" \
 LDFLAGS="--coverage" \
 python setup.py build_ext --inplace

# run the suite, then generate coverage
python -m pytest tests/ -q
gcov -o build/temp.linux-x86_64-cpython-313/src/attributedict/ \
 src/attributedict/_attributedict.c # -> _attributedict.c.gcov
```

**Measured: 92.34% line coverage of 209 executable lines** (2026-08-15,
CPython 3.13, linux x86_64). CI gates this at **> 90%**
(`.github/workflows/coverage.yml`).

The remaining uncovered lines are a small set of OOM/defensive error paths
that the deterministic fault-injection sweep does not drive (e.g. module
init failures). The test-only macro is never defined in production wheels,
so no fault-injection code ships; it mirrors CPython's own
`_testcapi.set_nomemory` approach.

Fault injection also surfaced and fixed a real NULL-safety bug: `tp_repr`
must not call `Py_ReprLeave` when `Py_ReprEnter` reported recursion or an
error (CPython defaultdict bug python/cpython#145492).

**Lesson learned:** an interrupted `coverage.py`/instrumented build can leave
a corrupt `.so` that segfaults — always remove stale `.so` files before a
coverage rebuild (the CI job does this).
