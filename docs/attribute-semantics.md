# Attribute Semantics

## Resolution order 

Attribute access on `AttributeDict` prefers **real type attributes** first
, then falls back to the mapping key:

1. Look up the name as a **real type attribute** (methods, descriptors,
 dunders, etc.) via the normal attribute machinery. If found, return it.
2. Otherwise, if the name is a `str` that is a valid Python identifier
 **and** a key in the mapping, return the key's value.
3. If neither exists, raise `AttributeError`.

Here's the practical upshot : a key named `items`, `keys`,
`values`, `get`, `update`, or `copy` does **not** shadow the method on the
*attribute* path:

```python
d = AttributeDict(items=42)
d.items # <built-in method items...> — the real dict method
list(d.items) # [('items', 42)]
d["items"] # 42 — mapping access keeps the key's value
dict.items(d) # dict_items([('items', 42)]) — the mapping view
```

Mapping access (`d[name]`, `d[name] = v`, `del d[name]`) is untouched and
always operates on keys.

## Attribute set / delete 

- `d.name = value` always stores `d["name"] = value`.
- `del d.name` deletes the key `"name"`; if absent it raises `AttributeError`
 (note the deviation from `del d["missing"]`, which raises `KeyError`).

## Edge-case keys 

| Key | Mapping access | Attribute access |
|---|---|---|
| `"normal"` | yes | yes (key value) |
| `"with-space"` | yes | no (`AttributeError`) |
| `"123"` | yes | no |
| `"_private"` | yes | yes (key value, when not a type attribute) |
| `"__dunder__"` | yes | yes* (see note) |
| `"items"`/`"keys"`/`"get"` | yes | the dict **method** |
| `"foo-bar"` / `""` | yes | no |
| non-str (`1`, `None`, `object`, `(1, 2)`) | yes | no |

\* `__dunder__` keys are addressable via attribute syntax only when they don't
collide with real type internals; the behavior is tested.

### Non-string keys: mapping only

Keys don't have to be strings — `AttributeDict` accepts any hashable key,
just like `dict`. But attribute syntax only understands string identifiers,
so non-string keys are reachable **only** through mapping access:

```python
class A: ...

attr_d = AttributeDict({A: None})

attr_d[A]     # None  — mapping access: the class object is a valid key
attr_d.A      # AttributeError: object has no attribute 'A'
```

In other words, `attr_d[A]` reads the key's value, while `attr_d.A` looks
for a *string* attribute named `"A"` — which doesn't exist, so it raises
`AttributeError`. Non-string keys are documented and tested (see the table
above).

## Why "type attributes win"?

See the [decisions](https://github.com/jymchng/attributedict/blob/main/spec/decisions.md)
 and the [FAQ](faq.md). Short version: real `dict` attributes
(methods/descriptors) win on the attribute path, so `d.items` reads as a
method exactly like it does on a plain `dict`, while mapping access still
returns key values. The two paths are intentionally asymmetric — and
documented so you're never surprised.
