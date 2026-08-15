# API Reference

`attributedict` exposes a single public type:

```python
from attributedict import AttributeDict
```

`__all__ == ["AttributeDict"]`. The C extension module
`attributedict._attributedict` is an implementation detail and is not part of
the public API.

> **Reference oracle:** `attributedict._reference` contains a pure-Python
> implementation of the same contract. It is used by the test suite and
> benchmarks as the cross-check baseline; it is **not** the public import
> path.

## Construction (FR-002)

```python
AttributeDict()                 # empty
AttributeDict(mapping)          # from a mapping
AttributeDict(iterable_of_pairs)
AttributeDict(**kwargs)
AttributeDict(mapping, **kwargs)
```

All forms match `dict`. Nested mappings are recursively converted (FR-007).

## Attribute / Mapping semantics (FR-003..006)

| Operation | Behavior |
|---|---|
| `d[key]` | dict getitem |
| `d[key] = v` | dict setitem |
| `del d[key]` | dict delitem |
| `d.name` | real type attribute first; else `d["name"]` if key; else AttributeError |
| `d.name = v` | `d["name"] = v` |
| `del d.name` | delete key `"name"`; `AttributeError` if absent |
| `d.items` (key `"items"` exists) | the **dict method** (type attribute wins, I-024) |
| `dict.items(d)` | the mapping view |

## repr / str (FR-010)

```python
repr(AttributeDict({'a': 1}))   # "AttributeDict({'a': 1})"
```

Nested values use their own repr; recursive structures render with `...`.

## Equality / hash (FR-011/012)

`==`/`!=` follow dict semantics. `AttributeDict` is **unhashable** like dict.

## Copy / pickle (FR-013)

`copy.copy`, `copy.deepcopy`, `pickle.dumps/loads` are supported. Nested
`AttributeDict` instances remain `AttributeDict`; self-references and cycles
work.

## Errors (FR-015)

- Missing key → `KeyError`
- Missing attribute → `AttributeError`
- Unhashable key → `TypeError`
- `del d.missing` → `AttributeError` (documented deviation from
  `del d["missing"]` → `KeyError`)

## Typing

`py.typed` is shipped. Attribute access cannot be fully represented
statically; typing is best-effort and documented as such.
