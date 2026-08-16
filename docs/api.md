# API Reference

`attributedict` exposes a single public type:

```python
from attributedict import AttributeDict
```

`__all__ == ["AttributeDict"]`. The C extension module
`attributedict._attributedict` is an implementation detail and isn't part of
the public API.

> **Reference oracle:** `attributedict._reference` contains a pure-Python
> implementation of the same contract. The test suite and benchmarks use it
> as the cross-check baseline; it is **not** the public import path.

## Construction 

```python
AttributeDict # empty
AttributeDict(mapping) # from a mapping
AttributeDict(iterable_of_pairs)
AttributeDict(**kwargs)
AttributeDict(mapping, **kwargs)
```

All forms match `dict`. Nested mappings are recursively converted.

## Attribute / Mapping semantics 

| Operation | Behavior |
|---|---|
| `d[key]` | dict getitem |
| `d[key] = v` | dict setitem |
| `del d[key]` | dict delitem |
| `d.name` | real type attribute first; else `d["name"]` if key; else AttributeError |
| `d.name = v` | `d["name"] = v` |
| `del d.name` | delete key `"name"`; `AttributeError` if absent |
| `d.items` (key `"items"` exists) | the **dict method** (type attribute wins) |
| `dict.items(d)` | the mapping view |

## repr / str 

```python
repr(AttributeDict({'a': 1})) # "AttributeDict({'a': 1})"
```

Nested values use their own repr; recursive structures render with `...`.

## Equality / hash 

`==`/`!=` follow dict semantics. `AttributeDict` is **unhashable** like dict.

## Copy / pickle 

`copy.copy`, `copy.deepcopy`, `pickle.dumps/loads` are supported. Nested
`AttributeDict` instances stay `AttributeDict`; self-references and cycles
work.

## Errors 

- Missing key → `KeyError`
- Missing attribute → `AttributeError`
- Unhashable key → `TypeError`
- `del d.missing` → `AttributeError` (documented deviation from
 `del d["missing"]` → `KeyError`)

## Typing

`py.typed` is shipped. Attribute access can't be fully represented
statically, so typing is best-effort — and honestly documented as such.
