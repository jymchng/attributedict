# Mapping semantics

## Mapping protocol (FR-008)

`AttributeDict` is a C subclass of `dict`, so the full mapping protocol is
inherited: `len(d)`, `iter(d)`, `d[key]`, `d[key] = v`, `del d[key]`,
`key in d`. `isinstance(d, dict)` and `isinstance(d, MutableMapping)` are
both true.

## dict methods (FR-009)

All standard dict methods are inherited and behave like `dict`:

- `get`, `setdefault`, `update`, `pop`, `popitem`, `clear`
- `keys()`, `items()`, `values()` (dict views)
- `fromkeys` — returns an `AttributeDict`
- `copy()` — returns an **`AttributeDict`** (shallow; overridden so the
  result keeps the attribute-access type, unlike plain `dict.copy` which
  would return a subclass-typed copy but is overridden here for clarity)

## Keys win interplay (FR-006)

Because attribute lookup checks the mapping first, a key named `items`,
`keys`, `values`, `get`, `update`, or `copy` shadows the method:

```python
d = AttributeDict(items=42)
d.items        # 42
dict.items(d)  # dict_items([('items', 42)]) — the mapping view
```

The mapping view and base methods remain reachable via `dict.<method>(d)`.

## Deviation from `dict`

- `copy()` returns `AttributeDict` (dict's C `copy` for subclasses also
  returns the subclass; this is documented and tested).
- Keys win over methods (see [attribute-semantics](attribute-semantics.md)).
