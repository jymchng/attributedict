# Troubleshooting

## `d.name` raises `AttributeError` even though the key exists

Only keys that are valid Python identifiers are reachable via attribute
syntax. Keys like `"with-space"`, `"123"`, `"foo-bar"`, or `""`
must use mapping syntax:

```python
d = AttributeDict({"with-space": 1})
d["with-space"] # 1
d.with-space # SyntaxError — use d["with-space"]
```

## `d.A` raises `AttributeError` even though `A` is a key

If the key isn't a *string* (for example a class, an int, or a tuple),
attribute syntax can't reach it — only mapping access can:

```python
class A: ...

attr_d = AttributeDict({A: None})
attr_d[A]   # None — mapping access works
attr_d.A    # AttributeError — attribute syntax only reads string keys
```

## `d.items` is a method, but I wanted the key's value

Real dict attributes win on the attribute path. If a key
named `items`/`keys`/`get`/`update`/`copy` exists, `d.items` returns the
dict method; use **mapping access** for the key's value:

```python
d = AttributeDict(items=42)
d.items # <built-in method items...>
d["items"] # 42
dict.items(d) # dict_items([('items', 42)])
```

## `del d.missing` raises `AttributeError` (not `KeyError`)

The attribute form mirrors attribute semantics; the mapping form mirrors
mapping semantics:

```python
del d["missing"] # KeyError
del d.missing # AttributeError (documented deviation)
```

## `hash(d)` raises `TypeError`

`AttributeDict` is unhashable, like `dict`.

## Pickling fails on a C-extension environment

Pickle round-trips are supported across all protocols (0–5). If you see
`AttributeError: can't set attribute` on unpickle, make sure you import
`attributedict` before unpickling (the `__reduce__` helper lives in
`attributedict._pickle_support`).

## A subclass of `AttributeDict` hangs or recurses

That was a real bug in early versions, fixed in. Upgrade to a
version that includes the fix; if you still see recursion, please open an
issue with a minimal repro.

## Not supported in v1

- PyPy and free-threaded CPython 3.13t (see [installation.md](installation.md)).
- YAML/dataclass/pydantic interop (use `dict(d)` to convert).
