# Risks

Stable identifiers R-001 … R-006, with likelihood/impact and mitigations.

- R-001 **abi3/Limited API limitations** (medium / medium): some optimized
  dict internals may be unavailable under `Py_LIMITED_API`. Mitigation:
  verify every used API is in the Limited API for 3.9+; document any slot
  that must fall back to generic behavior; test across the full range.
- R-002 **"Keys win" deviation surprises users** (medium / high): keys
  shadowing methods is atypical. Mitigation: prominent docs, explicit tests
  for every method-name collision, FAQ entry, changelog note.
- R-003 **Memory/refcount bugs in C** (medium / high): Mitigation:
  sanitizer CI jobs (ASan/UBSan), debug-Python refcount job, stress tests,
  code review checklist in 07-memory-management.
- R-004 **dict-subclass C interactions** (medium / medium): views,
  constructors, `fromkeys`, pickling of subclasses. Mitigation: test each
  dict method and view; validate `isinstance` and `dict.items(d)` paths.
- R-005 **Recursive conversion cost/cycles** (medium / medium): deep or
  self-referential structures. Mitigation: cycle-safe conversion, benchmark
  construction, document that construction is O(n).
- R-006 **Wheel matrix breadth vs CI cost** (low / low): Mitigation: sensible
  matrix; build wheels in a dedicated workflow; source builds covered by
  tests.yml.

Each risk is tracked to an issue or mitigation task in the topological graph.
