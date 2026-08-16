# FAQ

## Why does `d.items` read as a method even when a key `"items"` exists?

**Real dict attributes win on the attribute path**.
`AttributeDict` is designed so attribute access behaves like a plain `dict`
for type attributes, while mapping access still returns key values:

```python
d = AttributeDict(items=42)
d.items # <built-in method items...> — the real dict method
list(d.items) # [('items', 42)]
d["items"] # 42 — mapping access keeps the key's value
dict.items(d) # dict_items([('items', 42)]) — the mapping view
```

This is documented in [attribute-semantics](attribute-semantics.md). The
attribute path and the mapping path are intentionally asymmetric: attributes
read type members; `d[...]` reads keys.

## Why does `del d.missing` raise `AttributeError` but `del d["missing"]` raises `KeyError`?

The attribute form mirrors attribute semantics (`AttributeError` for a
missing attribute); the mapping form mirrors mapping semantics (`KeyError`
for a missing key). This deviation is documented in
[errors](errors.md) (spec 08).

## Are non-identifier keys accessible as attributes?

No. Keys like `"with-space"`, `"123"`, `"foo-bar"`, or `""` are usable via
mapping syntax only (`d["with-space"]`); attribute syntax raises
`AttributeError`.

## Is `AttributeDict` a real `dict`?

Yes — it's a C subclass of `dict`, so `isinstance(d, dict)` is `True`
 and it inherits the full mapping protocol and dict methods.

## Is `AttributeDict` hashable?

No. Like `dict`, it's unhashable.

## Which Python versions are supported?

CPython 3.9–3.14 via a single `cp39-abi3` wheel per platform. PyPy and
free-threaded CPython 3.13t aren't supported in v1.
