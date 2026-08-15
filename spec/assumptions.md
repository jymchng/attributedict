# Assumptions

Stable identifiers A-001 … A-008. Every assumption is a recorded default taken
during requirements interrogation; each is a low-impact or explicitly chosen
default.

- A-001 Package/import name `attributedict`; repo name `attributedict`.
- A-002 repr format `AttributeDict({...})`.
- A-003 Nested conversion is recursive at construction (user-selected).
- A-004 Keys win over attributes/methods on collision (user-selected final).
- A-005 Unhashable, like dict (user-selected).
- A-006 Free-threaded CPython 3.13t not supported unless CI proves otherwise.
- A-007 Wheels: Windows x86_64 + macOS arm64/x86_64 + manylinux x86_64/aarch64;
  source builds on all.
- A-008 No YAML/dataclass interop in v1; sets/frozensets not converted.

Each assumption is referenced by its identifier in the relevant spec docs and
issues.
