# Attribute Semantics

## Resolution order (FR-003/006)

Attribute access on `AttributeDict` prefers **real type attributes** first
(I-024), then falls back to the mapping key:

1. Look up the name as a **real type attribute** (methods, descriptors,
   dunders, etc.) via the normal attribute machinery. If found, return it.
2. Otherwise, if the name is a `str` that is a valid Python identifier
   **and** a key in the mapping, return the key's value.
3. If neither exists, raise `AttributeError`.

Consequence (FR-006, I-024): a key named `items`, `keys`, `values`, `get`,
`update`, or `copy` does **not** shadow the method on the *attribute* path:

```python
d = AttributeDict(items=42)
d.items        # <built-in method items ...> — the real dict method
list(d.items())  # [('items', 42)]
d["items"]     # 42 — mapping access keeps the key's value
dict.items(d)  # dict_items([('items', 42)]) — the mapping view
```

Mapping access (`d[name]`, `d[name] = v`, `del d[name]`) is untouched and
always operates on keys.

## Attribute set / delete (FR-004/005)

- `d.name = value` always stores `d["name"] = value`.
- `del d.name` deletes the key `"name"`; if absent it raises `AttributeError`
  (note the deviation from `del d["missing"]`, which raises `KeyError`).

## Edge-case keys (FR-014)

| Key | Mapping access | Attribute access |
|---|---|---|
| `"normal"` | yes | yes (key value) |
| `"with-space"` | yes | no (`AttributeError`) |
| `"123"` | yes | no |
| `"_private"` | yes | yes (key value, when not a type attribute) |
| `"__dunder__"` | yes | yes* (see note) |
| `"items"`/`"keys"`/`"get"` | yes | the dict **method** (I-024) |
| `"foo-bar"` / `""` | yes | no |
| non-str (`1`, `None`, `object()`, `(1, 2)`) | yes | no |

\* `__dunder__` keys are addressable via attribute syntax only when they do
not collide with real type internals; behavior is tested.

## Why "type attributes win"?

See the [decisions](https://github.com/jymchng/attributedict/blob/main/spec/decisions.md)
(D-004, I-024) and the [FAQ](faq.md):
real `dict` attributes (methods/descriptors) win on the attribute path so
`d.items` reads as a method exactly like a plain `dict`, while mapping access
still returns key values. The two paths are intentionally asymmetric and
documented.
