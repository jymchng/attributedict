# Quickstart

`attributedict` gives you a `dict` whose keys are also accessible as
attributes.

```python
from attributedict import AttributeDict

config = AttributeDict(host="localhost", port=8080)

config["host"]       # "localhost"
config.host          # "localhost" (same data)

config.debug = True  # stores config["debug"] = True
config["debug"]      # True
```

## Nested data

Nested mappings become `AttributeDict` automatically at construction:

```python
settings = AttributeDict({
    "database": {
        "host": "localhost",
        "ports": [5432, {"tls": True}],
    }
})

settings.database.host       # "localhost"
settings.database.ports[1].tls  # True
```

## It's a real dict

```python
isinstance(config, dict)          # True
dict(config)                      # {'host': 'localhost', 'port': 8080, ...}
list(config.keys())               # mapping views work
config.get("host")                # dict methods work
```

## Copy, deepcopy, pickle

```python
import copy, pickle

shallow = config.copy()           # AttributeDict (shallow)
deep = copy.deepcopy(config)      # AttributeDict (deep)
loaded = pickle.loads(pickle.dumps(config))  # round-trips
```

## Important: keys win

A key named like a method shadows it:

```python
d = AttributeDict(items=42)
d.items        # 42  (the key's value)
dict.items(d)  # dict_items([('items', 42)]) — the mapping view
```

See [attribute-semantics.md](attribute-semantics.md) and the [FAQ](faq.md).

## Next steps

- [api.md](api.md) — full API reference
- [attribute-semantics.md](attribute-semantics.md) — resolution order
- [mapping-semantics.md](mapping-semantics.md) — dict compatibility
- [nested.md](nested.md) — nested conversion
- [serialization.md](serialization.md) — copy / pickle
- [errors.md](errors.md) — exception contract
