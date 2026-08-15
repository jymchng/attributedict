# 02 — Personas and Use Cases

## Purpose

Concrete personas and the primary use cases driving the AttributeDict design.

## Scope

Who uses the package and the scenarios that shape the API decisions.

## Personas

### P1 — Application Developer (primary)
Writes Python services and wants config objects readable as attributes:
```python
cfg = AttributeDict(host="localhost", port=8080)
connect(cfg.host, cfg.port)
```
Needs dict compatibility (pass to `dict` APIs, serialize to JSON via
`dict(cfg)`), intuitive attribute access, and predictable error behavior.

### P2 — Library Author
Wraps nested data (API responses, YAML-like configs) and wants recursive
attribute access:
```python
r = AttributeDict({"user": {"name": "Ada", "roles": ["admin"]}})
r.user.name, r.user.roles
```
Needs recursive conversion, deterministic repr, pickle/copy support.

### P3 — Maintainer / C Extension Engineer
Extends the C implementation. Needs a clean C layout, documented refcount and
GC contract, sanitizer validation, and a fast test loop.

### P4 — Release / Packaging Engineer
Builds abi3 wheels across platforms. Needs reproducible packaging and CI.

## Use Cases

- UC-1 Construct from kwargs/mapping/iterable (FR-002).
- UC-2 Attribute get/set/delete on keys (FR-003..005).
- UC-3 Resolve key/method collisions deterministically (FR-006).
- UC-4 Recursive nested conversion (FR-007).
- UC-5 Full mapping protocol + dict methods (FR-008..009).
- UC-6 repr/equality/hash (FR-010..012).
- UC-7 Pickle/copy/deepcopy incl. cycles (FR-013).
- UC-8 Edge-case keys and error semantics (FR-014..015).
- UC-9 Benchmark and compare (NFR-006).
- UC-10 Build abi3 wheels and run CI matrix (NFR-007..008).
- UC-11 Write user/developer/performance docs (NFR-010).

## Cross-references

- 01-product-requirements, 03-functional-requirements, 04-non-functional-requirements.
