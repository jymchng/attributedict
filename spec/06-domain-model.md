# 06 — Domain and Data Model

## Purpose

The conceptual data model: what AttributeDict stores and how values relate.

## Scope

Key/value storage, nested conversion semantics, and value containment rules.

## Domain Model

- `AttributeDict` is a **mapping** (a dict subclass): it stores an unordered
  (insertion-ordered) set of key → value pairs.
- Keys: any hashable object (int, str, tuple, None, object, …). Attribute
  access is only meaningful for `str` keys that are valid Python identifiers
  and not shadowed by the keys-win rule.
- Values: any Python object. At construction, contained `dict` instances
  (recursively, and within `list`/`tuple`) are converted to `AttributeDict`;
  sets/frozensets are not converted (documented assumption A-008/OQ-004).
- Conversion is **cycle-safe**: a mapping currently being converted is reused
  rather than re-converted, so recursive/self-referential structures convert
  without infinite recursion.

## Data Model Rules

- DM-1 `d[key]` and `d.key` (when key is a valid identifier) refer to the
  same stored value.
- DM-2 Non-identifier and non-string keys are addressable only via mapping
  syntax.
- DM-3 Keys shadow type attributes/methods (FR-006).
- DM-4 Nested dicts inside lists/tuples convert recursively (FR-007).
- DM-5 The object is mutable and unhashable (FR-012).
- DM-6 Equality follows dict semantics (FR-011).

## Example

```python
x = AttributeDict({
    "db": {"host": "localhost", "ports": [5432, {"tls": True}]},
    1: "one",
})
x.db.host      # "localhost"
x.db.ports[1].tls  # True
x[1]           # "one"
```

## Cross-references

- 03-functional-requirements (FR-002, FR-006, FR-007, FR-014),
  05-system-architecture, 08-api-specification.
