# 01 — Product Requirements

## Purpose

Product-level intent, actors, goals, and the user journey for the
`attributedict` package.

## Scope

Who uses the package and why; what it must accomplish; what it deliberately
does not do.

## Terminology

See 00-overview.

## Actors

- **End user**: a Python developer who wants attribute-style access to
  configuration/options data without losing dict behavior.
- **Maintainer**: an engineer extending the C extension, reviewing, releasing.
- **CI automation**: GitHub Actions building, testing, and packaging wheels.

## Goals

- G1 Both mapping and attribute syntax address the same data.
- G2 Performance-critical core in a real C extension.
- G3 dict compatibility preserved wherever sensible; deviations explicit.
- G4 Memory-safe (refcounts, GC, no leaks/UAF; sanitizer-validated).
- G5 Comprehensive tests + benchmarks vs dict and pure-Python baseline.
- G6 Modern packaging (pyproject, abi3 wheels), CI, docs, spec, issues.
- G7 Traceability from intent to implementation.

## User Journey

1. Install: `pip install attributedict` (wheel or source).
2. Import: `from attributedict import AttributeDict`.
3. Construct: `config = AttributeDict(host="localhost", port=8080)`.
4. Access: `config.host` == `config["host"]`; mutate via `config.port = 9000`.
5. Nest: `cfg = AttributeDict({"db": {"host": "x"}}); cfg.db.host`.
6. Use as a dict: pass to `dict`-accepting APIs; `isinstance(cfg, dict)` true.
7. Serialize: `pickle` round-trip; `dict(cfg)` to plain dict.
8. Troubleshoot: read docs; report issues with a minimal repro.

## Non-Goals (v1)

- No YAML/dataclass/pydantic interop.
- No free-threaded 3.13t or PyPy support.
- No publishing automation.

## Acceptance Criteria

- AC-001 … AC-009 from 00-overview.

## Cross-references

- 00-overview, 02-personas-and-use-cases, 03-functional-requirements.
