# Attribute Semantics

## Resolution order (FR-003/006)

Attribute access on `AttributeDict` follows a **keys-win** order:

1. If the attribute name is a `str` that is a valid Python identifier **and**
   a key in the mapping, return the key's value.
2. Otherwise fall back to normal attribute lookup (type attributes,
   descriptors, methods, dunders).
3. If neither exists, raise `AttributeError`.

Consequence (FR-006): a key named `items`, `keys`, `values`, `get`, `update`,
or `copy` shadows the corresponding method:

```python
d = AttributeDict(items=42)
d.items        # 42 (the key)
dict.items(d)  # dict_items([('items', 42)]) — the mapping view
```

## Attribute set / delete (FR-004/005)

- `d.name = value` always stores `d["name"] = value`.
- `del d.name` deletes the key `"name"`; if absent it raises `AttributeError`
  (note the deviation from `del d["missing"]`, which raises `KeyError`).

## Edge-case keys (FR-014)

| Key | Mapping access | Attribute access |
|---|---|---|
| `"normal"` | yes | yes |
| `"with-space"` | yes | no (`AttributeError`) |
| `"123"` | yes | no |
| `"_private"` | yes | yes (keys win when present) |
| `"__dunder__"` | yes | yes* (see note) |
| `"items"`/`"keys"`/`"get"` | yes | key wins when present |
| `"foo-bar"` / `""` | yes | no |
| non-str (`1`, `None`, `object()`, `(1, 2)`) | yes | no |

\* `__dunder__` keys are addressable via attribute syntax only when they do
not collide with real type internals; behavior is tested.

## Why "keys win"?

See [decisions](../spec/decisions.md) (D-004) and the [FAQ](faq.md): keys winning over
methods is an intentional deviation from plain `dict` that makes
attribute-style access to data keys predictable. The mapping view remains
reachable via the base `dict` API (`dict.items(d)`, `dict.get(d, ...)`).
