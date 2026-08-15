# Compatibility

## Validated matrix (I-019)

| Environment | Result |
|---|---|
| CPython 3.10 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.11 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.12 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.13 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.14 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.9 | ✅ covered by CI matrix (`tests.yml`) |
| abi3 wheel `cp39-abi3` on CPython 3.10 | ✅ installs + all pickle protocols |
| Windows x86_64 / macOS arm64+x86_64 / manylinux x86_64+aarch64 | ✅ cibuildwheel matrix (`wheels.yml`) |
| PyPy | ❌ not supported (v1) |
| Free-threaded CPython 3.13t | ❌ not supported (v1) |

Validated 2026-08-15 on linux x86_64 (CPython 3.10.20, 3.11.15, 3.12.13,
3.13.13, 3.14.4).

## Version-specific notes

- **Pickle**: all protocols (0–5) verified on every tested version; the
  `__reduce__` 5-tuple form is stable across 3.10–3.14.
- **dict subclass internals**: no version-specific behavior differences
  observed across 3.10–3.14 (mapping views, fromkeys, copy, equality,
  unhashable).
- **repr recursion**: `Py_ReprEnter`/`Py_ReprLeave` behave identically
  across the range.
- **GC**: the portable `Py_VISIT`/`Py_CLEAR` pattern works on all tested
  versions (no `PyObject_VisitManagedDict` dependency — R-001 mitigation).

## Unsupported environments (documented, DOC-004)

- **PyPy** and other non-CPython interpreters.
- **Free-threaded CPython 3.13t** — not validated; explicitly unsupported
  in v1 (NFR-001, A-006).

If you need support for these, please open an issue; CI validation would be
required before declaring support.
