# FAQ

## Why does a key named `items`/`keys`/`get` shadow the method?

**Keys win** (FR-006, D-004). `AttributeDict` is designed so that attribute
access reads the mapping first, which makes data-key access predictable:

```python
d = AttributeDict(items=42)
d.items        # 42
dict.items(d)  # dict_items([('items', 42)]) — the mapping view
```

This is a deliberate deviation from plain `dict`, documented in
[attribute-semantics](attribute-semantics.md). The base-dict API remains
reachable via `dict.<method>(d)`.

## Why does `del d.missing` raise `AttributeError` but `del d["missing"]` raises `KeyError`?

The attribute form mirrors attribute semantics (`AttributeError` for a
missing attribute); the mapping form mirrors mapping semantics (`KeyError`
for a missing key). This deviation is documented in
[errors](errors.md) (FR-015, spec 08).

## Are non-identifier keys accessible as attributes?

No. Keys like `"with-space"`, `"123"`, `"foo-bar"`, or `""` are usable via
mapping syntax only (`d["with-space"]`); attribute syntax raises
`AttributeError` (FR-014).

## Is `AttributeDict` a real `dict`?

Yes — it is a C subclass of `dict`, so `isinstance(d, dict)` is `True`
(C-002) and it inherits the full mapping protocol and dict methods.

## Is `AttributeDict` hashable?

No. Like `dict`, it is unhashable (FR-012).

## Which Python versions are supported?

CPython 3.9–3.14 via a single `cp39-abi3` wheel per platform. PyPy and
free-threaded CPython 3.13t are not supported in v1 (NFR-001, DOC-004).
