# Mapping semantics

## Mapping protocol (FR-008)

`AttributeDict` is a C subclass of `dict`, so the full mapping protocol is
inherited: `len(d)`, `iter(d)`, `d[key]`, `d[key] = v`, `del d[key]`,
`key in d`. Both `isinstance(d, dict)` and `isinstance(d, MutableMapping)`
are true — no surprises there.

## dict methods (FR-009)

All standard dict methods are inherited and behave like `dict`:

- `get`, `setdefault`, `update`, `pop`, `popitem`, `clear`
- `keys()`, `items()`, `values()` (dict views)
- `fromkeys` — returns an `AttributeDict`
- `copy()` — returns an **`AttributeDict`** (shallow; overridden so the
  result keeps the attribute-access type, unlike plain `dict.copy` which
  would return a subclass-typed copy but is overridden here for clarity)

## Type-attribute / key interplay (FR-006, I-024)

Attribute lookup checks the **type's real attributes first**; a key named
`items`, `keys`, `values`, `get`, `update`, or `copy` does **not** shadow the
method on the attribute path:

```python
d = AttributeDict(items=42)
d.items        # <built-in method items ...> — the real dict method
list(d.items())  # [('items', 42)]
d["items"]     # 42 — mapping access keeps the key's value
dict.items(d)  # dict_items([('items', 42)]) — the mapping view
```

Mapping access (`d[name]`, `d[name] = v`) always operates on keys. The
mapping view and base methods stay reachable via `dict.<method>(d)`.

## Deviation from `dict`

- `copy()` returns `AttributeDict` (dict's C `copy` for subclasses also
  returns the subclass; this is documented and tested).
- Keys win over methods on the *mapping* path — well, more precisely, the
  type's real attributes win on the *attribute* path (see
  [attribute-semantics](attribute-semantics.md)).
