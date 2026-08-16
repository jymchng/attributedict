# Errors

## Exception contract 

| Operation | Exception |
|---|---|
| `d[missing_key]` | `KeyError` |
| `d.missing_attr` | `AttributeError` |
| `del d.missing_attr` | `AttributeError` (documented deviation) |
| `del d["missing_key"]` | `KeyError` |
| `d[unhashable_key]` | `TypeError` |
| `hash(d)` | `TypeError` (unhashable, like dict) |

### Example messages

```python
AttributeDict["missing"]
# KeyError: 'missing'

AttributeDict.missing
# AttributeError: 'attributedict._attributedict.AttributeDict' object has no attribute 'missing'
```

The C implementation never leaves a stale exception after a successful
operation; `PyErr_Clear` is used only where an exception is
intentionally swallowed and re-raised with a different type (e.g. the
`del d.missing` → `AttributeError` deviation).

## Unhashable

`AttributeDict` is unhashable, like `dict` :

```python
hash(AttributeDict) # TypeError: unhashable type: '...AttributeDict'
```
