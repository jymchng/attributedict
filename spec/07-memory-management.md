# 07 — Memory Management

## Purpose

The reference-counting, GC, and memory-safety contract for the C extension.

## Scope

Refcount rules, GC participation, error-path discipline, sanitizer strategy.

## Requirements

- MEM-001 The type is a C subclass of `dict`; all key/value references are
  owned by the dict base. No custom storage that duplicates ownership.
- MEM-002 `tp_new`/`tp_init` follow CPython refcount rules: `tp_new` returns
  a new reference; `tp_init` must not leak on failure (clear partial state).
- MEM-003 GC participation: implement `tp_traverse`/`tp_clear` (delegating to
  the dict base where possible via the Limited API), because contained values
  can reference the AttributeDict (cycles).
- MEM-004 Error paths: every C function that can fail must not leave a stale
  exception; on success, `PyErr_Occurred()` must be false. Use
  `PyErr_Clear()` only where a swallowed exception is intentional and
  documented.
- MEM-005 Borrowed vs new references: never decref borrowed references;
  incref before storing in a container; decref after `PyDict_SetItem` if the
  reference was newly created.
- MEM-006 Deallocation: `tp_dealloc` delegates to the dict base dealloc; no
  double-free.
- MEM-007 Recursive conversion helper: must be cycle-safe and leak-free on
  every branch (including the exception path mid-conversion).
- MEM-008 Sanitizers: CI jobs build with AddressSanitizer and
  UndefinedBehaviorSanitizer (via `-fsanitize=address,undefined` with a
  debug CPython where available) and run the test suite + a stress test that
  constructs/destroys many AttributeDicts and cyclic structures.

## Testing

- Repeated construction/destruction (refcount/leak smoke).
- Cyclic structures (self-reference) garbage-collected without leaks.
- Stress: create/delete thousands of objects; assert refcount stability.
- Sanitizer jobs must be clean.

## Cross-references

- 05-system-architecture, 10-testing, 13-ci, decisions.md.
