# 08 — API Specification

## Purpose

The exact public API and behavior contract.

## Scope

Public names, construction, attribute/mapping semantics, repr/equality/
copy/pickle, error behavior, edge-case keys, and typing.

## Public API

```python
from attributedict import AttributeDict
```

`__all__ = ["AttributeDict"]`. The C extension module is `attributedict._attributedict`
(internal).

## Construction (FR-002)

```python
AttributeDict()
AttributeDict(mapping)
AttributeDict(iterable_of_pairs)
AttributeDict(**kwargs)
AttributeDict(mapping, **kwargs)
```

All forms match `dict`. Recursive conversion (FR-007) applies to contained
dicts and dicts inside lists/tuples.

## Attribute / Mapping Semantics

| Operation | Behavior |
|---|---|
| `d[key]` | dict getitem |
| `d[key] = v` | dict setitem |
| `del d[key]` | dict delitem |
| `d.name` | if `"name"` is a key → `d["name"]`; else GenericGetAttr → AttributeError if missing |
| `d.name = v` | `d["name"] = v` |
| `del d.name` | delete key `"name"`; AttributeError if absent |
| `d.items` (key "items" exists) | **key's value** (keys-win, FR-006) |
| `dict.items(d)` | bound method |

Resolution order documented in 05-system-architecture.

## repr / str (FR-010)

`repr(AttributeDict({'a': 1})) == "AttributeDict({'a': 1})"`. Nested values
use their own repr; recursive structures render with `...`.

## Equality / Hash (FR-011/012)

`==`/`!=` follow dict semantics; unhashable.

## Copy / Pickle (FR-013)

`copy.copy`, `copy.deepcopy`, `pickle.dumps/loads` supported; nested
AttributeDict preserved; cycles work.

## Edge-Case Keys (FR-014)

| Key | Mapping access | Attribute access |
|---|---|---|
| `"normal"` | yes | yes |
| `"with-space"` | yes | no (AttributeError) |
| `"123"` | yes | no |
| `"_private"` | yes | yes* (see note) |
| `"__dunder__"` | yes | yes* (see note) |
| `"items"`/`"keys"`/`"get"` | yes | key wins when present |
| `"foo-bar"` / `""` | yes | no |
| non-str (1, None, object, (1,2)) | yes | no |

*Note: `_private`/dunder keys are addressable via attribute syntax only when
they don't collide with real type internals; behavior is tested and
documented. Default: keys win, so `d._private` returns the key when present.

## Errors (FR-015)

- Missing key → `KeyError`.
- Missing attribute → `AttributeError`.
- Unhashable key → `TypeError`.
- `del d.missing` → `AttributeError` (documented deviation from `del
  d["missing"]` which is KeyError; the attribute form uses AttributeError).
- C layer never leaves a stale exception after success.

## Typing

Ship `py.typed`; provide a `Generic`-style definition for
`AttributeDict[K, V]` where feasible; document that attribute access cannot be
fully typed statically (limitation documented, not faked).

## Cross-references

- 03-functional-requirements, 05-system-architecture, 06-domain-model,
  14-documentation, decisions.md.
