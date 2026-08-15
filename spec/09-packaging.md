# 09 — Packaging

## Purpose

Packaging, build system, wheels, and distribution strategy.

## Scope

pyproject.toml, build backend, abi3 wheels, sdist, cibuildwheel, publishing.

## Requirements

- PKG-001 Modern `pyproject.toml` with `[build-system]`, `[project]` metadata,
  and build config.
- PKG-002 Build backend: **setuptools** (chosen for simplicity and mature
  abi3 support for a single small C extension; scikit-build-core evaluated
  and rejected as unnecessary). Document this decision.
- PKG-003 Limited API / Stable ABI: set `py_limited_api` and build the
  extension with `Py_LIMITED_API` targeting 3.9; wheel tag `cp39-abi3`.
- PKG-004 `[project]` metadata: name `attributedict`, version, description,
  readme, license (MIT), authors, classifiers, requires-python `>=3.9`,
  no runtime dependencies.
- PKG-005 `py.typed` + typing markers included in wheels.
- PKG-006 cibuildwheel: manylinux x86_64 + aarch64, macOS arm64 + x86_64,
  Windows x86_64, all building abi3 wheels.
- PKG-007 sdist builds from source on all supported platforms.
- PKG-008 No publishing credentials in CI; release is a manual, explicitly
  configured step (e.g. trusted-publisher workflow, not auto-run).
- PKG-009 Wheel validation: install each wheel into a clean venv on the
  matching platform and run the smoke test.

## Verified C API availability (I-003)

Static analysis of CPython 3.13 headers (Limited API, 3.9 target):

- Public and used: `PyDict_Type`, `PyDict_GetItemWithError`, `PyDict_SetItem`,
  `PyDict_DelItem`, `PyDict_Contains`, `PyObject_GenericGetAttr`,
  `PyObject_GenericSetAttr`, `PyObject_GenericGetDict`, `PyUnicode_IsIdentifier`,
  `Py_ReprEnter`/`Py_ReprLeave`, `Py_VISIT`/`Py_CLEAR`,
  `Py_TPFLAGS_BASETYPE`/`Py_TPFLAGS_HAVE_GC`.
- NOT public in 3.13: `PyObject_VisitManagedDict`/`PyObject_ClearManagedDict`,
  `PyObject_GC_Visit`/`PyObject_GC_Clear` — use the portable
  `Py_VISIT`/`Py_CLEAR` pattern for GC (see docs/architecture.md and spec 05).

## Source Layout

```text
src/attributedict/
├── __init__.py
├── py.typed
└── _attributedict.c
pyproject.toml
noxfile.py
```

## Cross-references

- 04-non-functional-requirements (NFR-003, NFR-007), 11-performance,
  13-ci, decisions.md, docs/architecture.md.
