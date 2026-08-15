# 04 — Non-Functional Requirements

## Purpose

Quality attributes with stable identifiers.

## Scope

NFR-001 … NFR-010.

## Requirements

### NFR-001 — CPython compatibility
Support CPython 3.9, 3.10, 3.11, 3.12, 3.13, 3.14. CI matrix must run tests
on the supported range (where runners allow). No PyPy/free-threaded support
in v1 (documented).

### NFR-002 — Architecture
C type subclassing `dict` with custom `tp_getattro`/`tp_setattro`. Keeps
`isinstance(d, dict)` true and inherits dict's mapping internals.

### NFR-003 — ABI strategy
Limited API / Stable ABI (abi3). `py_limited_api` enabled in build config;
one abi3 wheel per platform across 3.9–3.14. Verified that all used CPython
APIs are in the Limited API for 3.9+.

### NFR-004 — Memory safety
Correct refcounts (incref/decref on all paths incl. error paths); GC
participation (`tp_traverse`, `tp_clear`) since the object holds contained
Python objects; no use-after-free/double-decref/leaks. CI includes
AddressSanitizer + UndefinedBehaviorSanitizer debug builds and a debug-Python
refcount job.

### NFR-005 — Threading
Safe under the GIL (standard CPython semantics). Free-threaded 3.13t
explicitly unsupported unless a future CI job validates it.

### NFR-006 — Performance
Benchmark construction, key/attribute get/set/delete, iteration, nested
access, copy against: plain `dict`, a pure-Python AttributeDict baseline, and
the C implementation. Results reported as data with methodology; no
unsupported speed claims.

### NFR-007 — Packaging
Modern `pyproject.toml`; build backend chosen in spec (setuptools vs
scikit-build-core — decide in 09-packaging). cibuildwheel produces abi3
wheels: manylinux (x86_64 + aarch64), macOS (arm64 + x86_64), Windows
(x86_64). Source distribution must build from source on all supported
platforms.

### NFR-008 — CI matrix
GitHub Actions: format, lint, typecheck, unit tests, C build, multiple Python
versions (3.9–3.14) and OSes, packaging/wheel validation, docs validation,
sanitizer jobs. Sensible matrix (not prohibitively expensive).

### NFR-009 — Dev tooling
pytest, mypy, ruff, nox, coverage, pre-commit; cibuildwheel; hypothesis and
pytest-benchmark only where justified. A `noxfile.py` provides reproducible
sessions: tests, lint, format, typecheck, coverage, build, docs, benchmarks.

### NFR-010 — Documentation
User (install, supported versions, quickstart, API, attribute/mapping/nested/
serialization/copy/error behavior), developer (architecture, C layout,
refcounts, attribute resolution, build, testing, sanitizers, benchmarks,
release), packaging, performance. `py.typed` included; typing limitations
documented.

## Cross-references

- 03-functional-requirements, 05-system-architecture, 09-packaging,
  10-testing, 11-performance, 13-ci, 14-documentation.
