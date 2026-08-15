# Implementation Topological Graph

## Graph Semantics

`A -> B` means **B depends on A**.

## Root Issues

- I-001 Repository initialization (repo, README, .gitignore, LICENSE, pyproject skeleton)
- I-002 Define public API + attribute-resolution semantics (spec 01/03/08)
- I-003 Define mapping compatibility + C API strategy (spec 03/05/09)

## Intermediate Issues

- I-004 Design native object representation + GC contract (spec 05/07)
- I-005 Implement module initialization + type registration
- I-006 Implement construction + recursive conversion (FR-002/FR-007)
- I-007 Implement mapping protocol (FR-008/009)
- I-008 Implement attribute get/set/delete + keys-win resolution (FR-003..006)
- I-009 Implement repr/equality/hash (FR-010..012)
- I-010 Implement copy/pickle (FR-013)
- I-011 Implement error semantics + edge-case keys (FR-014/015)
- I-012 Memory-management tests + sanitizer jobs (07, 13)
- I-013 Python test suite (10)
- I-014 Benchmarks (11)
- I-015 Packaging: pyproject, abi3, cibuildwheel (09)
- I-016 Dev tooling: ruff, mypy, nox, pre-commit (04)
- I-017 CI workflows (13)
- I-018 Documentation (14)

## Leaf Issues

- I-019 Compatibility validation (3.9–3.14, platforms)
- I-020 Final audit (traceability + security + reproducibility)

## Topological Order

### Wave 0
- I-001, I-002, I-003

### Wave 1
- I-004, I-005 (I-005 depends on I-004)

### Wave 2
- I-006, I-007, I-008 (each depends on I-005)

### Wave 3
- I-009, I-010, I-011 (depend on I-006/007/008)

### Wave 4
- I-012, I-013, I-014 (depend on I-009/010/011)

### Wave 5
- I-015, I-016, I-017 (depend on I-012/013/014)

### Wave 6
- I-018 (docs; depends on I-015/016)

### Wave 7
- I-019 (compat validation; depends on I-017/018)

### Wave 8
- I-020 (final audit; depends on I-019)

## Critical Path

I-001 → I-002 → I-004 → I-005 → I-006/007/008 → I-009 → I-012 → I-015 → I-017 → I-018 → I-019 → I-020

## Dependency Graph

```text
I-001 ──┐
I-002 ──┼──► I-004 ─► I-005 ─► I-006 ─┐
I-003 ──┘                │             ├─► I-009 ─► I-012 ─► I-015 ─► I-017 ─► I-018 ─► I-019 ─► I-020
                         ├─► I-007 ────┤
                         └─► I-008 ─────┘
                                             I-013 (after I-009/010/011)
                                             I-014 (after I-009/010/011)
                                             I-016 (after I-012/013/014)
```

## Parallelizable Groups

- Wave 0: I-001, I-002, I-003 in parallel.
- Wave 2: I-006, I-007, I-008 in parallel (after I-005).
- Wave 4: I-012, I-013, I-014 in parallel (after I-009/010/011).
- Wave 5: I-015, I-016, I-017 in parallel.

## Rationale

- API/ABI/architecture specs must precede any C implementation.
- Module init + type registration gates all behavioral implementation.
- Mapping, attribute, and conversion are independent implementations after
  the type exists.
- Tests/benchmarks/sanitizers need the behavior implemented.
- Packaging/CI/docs follow the working implementation.
- Compatibility validation and the final audit close the loop.

## Cycles

None detected. Recursive conversion (I-006) is specified cycle-safe; no
dependency cycle exists between issues.
