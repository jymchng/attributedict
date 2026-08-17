# Decisions

Stable identifiers D-001 … D-011, with rationale. Each decision traces to the
requirements-interrogation answers.

- D-001 **Architecture**: C subclass of `dict` + custom `tp_getattro` /
  `tp_setattro`. Rationale: keeps `isinstance(d, dict)` true (C-002), inherits
  dict mapping internals, minimizes custom code. (User-selected.)
- D-002 **ABI**: Limited API / Stable ABI (abi3). One wheel per platform
  across 3.9–3.14. Rationale: user-selected; smaller wheel matrix. Constraint
  R-001 (Limited API limitations) documented.
- D-003 **Nested conversion**: recursive at construction, incl. lists/tuples.
  (User-selected.)
- D-004 **Collision resolution**: real type attributes win on the attribute
  path; mapping access keeps key values (I-024; supersedes the earlier
  "keys win" decision).
  (User-selected final; supersedes an earlier "methods win" answer.)
- D-005 **Construction**: all dict forms. (User-selected.)
- D-006 **Pickle/copy/deepcopy**: supported incl. cycles. (User-selected.)
- D-007 **Hashability**: unhashable. (User-selected.)
- D-008 **Benchmarks**: required, documented data. (User-selected.)
- D-009 **Wheels**: cibuildwheel abi3, manylinux + macOS + Windows.
  (User-selected.)
- D-010 **Python range**: 3.9–3.14. (User-selected.)
- D-011 **GitHub**: private repo `OWNER/attributedict` via github-tools MCP.
  (User-selected.)
- D-012 **Build backend**: setuptools (PKG-002). Rationale: simple, mature
  abi3 support for one small C extension; scikit-build-core rejected as
  unnecessary.

Each decision is cited in the relevant spec docs and implementation issues.
