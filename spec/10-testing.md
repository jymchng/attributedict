# 10 — Testing Strategy

## Purpose

The test architecture for the package.

## Scope

Unit, integration, C-level, memory, stress, benchmark, and CI test layers.

## Layers

### Unit / Python protocol tests
Construction forms, attribute/mapping get/set/delete, collisions, nested
conversion, repr, equality, hash, iteration, views, `MutableMapping`
compatibility, copy/deepcopy/pickle, edge-case keys, error types.

### C-extension behavior tests
- Actual compiled type: `type(d).__module__`/`__name__`, `isinstance(d,
  dict)`, dict-method inheritance, `dict.items(d)` reachability.
- Recursive conversion cycle safety (self-referencing dict → AttributeDict).
- Refcount smoke: create/destroy many objects; assert no leak via
  `sys.gettotalrefcount()` in debug builds or a documented proxy.

### Memory / sanitizer tests (NFR-004)
- Stress: thousands of constructions + deletions.
- Cyclic structures collected by gc without leaks.
- ASan/UBSan CI jobs run the suite.

### Property-based (hypothesis, justified)
- Random nested structures convert correctly and remain dict-compatible.
- Random key/value operations preserve dict-equivalence.

### Benchmark tests (NFR-006)
- pytest-benchmark or a dedicated `benchmarks/` script comparing
  construction, get/set/delete (key+attr), iteration, nested access, copy
  across dict, pure-Python AttributeDict, C AttributeDict.

## Traceability

`Requirement → Issue → Implementation → Test → Doc` tracked in
`topological_graph.md` and the audit.

## Cross-references

- 03-functional-requirements, 04-non-functional-requirements (NFR-004,
  NFR-006, NFR-008), 07-memory-management, 11-performance, 13-ci.
