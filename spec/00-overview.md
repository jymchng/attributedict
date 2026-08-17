# 00 — Overview

## Purpose

This specification defines the **`attributedict`** Python package: a
production-quality CPython C extension implementing an `AttributeDict` type
that combines dict-style mapping semantics with attribute access
(`d["host"] == d.host`). It is the source of truth for the project's
architecture, API, behavior, packaging, testing, CI, and documentation.

## Scope

In scope: the `AttributeDict` type, its C implementation (a C subclass of
`dict` with custom `tp_getattro`/`tp_setattro`), recursive nested conversion,
pickling/copying, benchmarks, abi3 wheels via cibuildwheel, CI matrix,
docs, and the engineering process (spec → issues → graph → implementation →
test → package → CI → audit).

Out of scope: YAML/dataclass/pydantic interop, free-threaded 3.13t support,
PyPy/other interpreters, publishing automation.

## Terminology

| Term | Definition |
|---|---|
| AttributeDict | The public type; a C subclass of `dict` with attribute access. |
| Mapping syntax | `d[key]`, `d[key]=v`, `del d[key]`, `len(d)`, `iter(d)`. |
| Attribute syntax | `d.name`, `d.name=v`, `del d.name`. |
| Key/attribute collision | A mapping key whose name matches a real type attribute or method. |
| Nested conversion | Recursively converting contained mappings/lists/tuples into AttributeDict at construction. |
| abi3 / Stable ABI | The CPython Limited API; one wheel per platform across 3.9–3.14. |

## Requirements

- FR-001 … FR-015, NFR-001 … NFR-010 (see 03 and 04).
- SEC-001 … SEC-006 (see 12).
- Acceptance criteria AC-001 … AC-009.

## Constraints

- C-001 genuine C extension; C-002 isinstance(d, dict) true; C-003 abi3;
  C-004 no third-party runtime deps; C-005 private GitHub repo via MCP;
  C-006 no publishing credentials.

## Decisions

- D-001 C subclass of dict + custom `tp_getattro`/`tp_setattro`.
- D-002 Limited API / Stable ABI (abi3).
- D-003 Recursive nested conversion.
- D-004 Keys win over methods on collision.
- D-005 All dict construction forms.
- D-006 Pickle/copy/deepcopy incl. cycles.
- D-007 Unhashable.
- D-008 Benchmarks documented.
- D-009 cibuildwheel abi3 manylinux+macOS+Windows.
- D-010 Python 3.9–3.14.
- D-011 Private repo `OWNER/attributedict` via github-tools MCP.

## Acceptance Criteria

- AC-001 … AC-009 (see 03/04 and the final audit).

## Cross-references

- [01-product-requirements.md](01-product-requirements.md)
- [02-personas-and-use-cases.md](02-personas-and-use-cases.md)
- [03-functional-requirements.md](03-functional-requirements.md)
- [04-non-functional-requirements.md](04-non-functional-requirements.md)
- [05-system-architecture.md](05-system-architecture.md)
- [08-api-specification.md](08-api-specification.md)
- [10-testing.md](10-testing.md)
- [14-documentation.md](14-documentation.md)
- [topological_graph.md](topological_graph.md)
