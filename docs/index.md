# attributedict

**dict semantics with attribute access.**

`attributedict` is a production-quality **CPython C extension** implementing
an `AttributeDict`: a `dict` subclass whose keys are also accessible through
attribute syntax. In plain terms: you get a real dict that's also nice to
read and write with dot notation.

```python
from attributedict import AttributeDict

config = AttributeDict(host="localhost", port=8080)
assert config["host"] == "localhost"
assert config.host == "localhost"

config.debug = True
assert config["debug"] is True
```

## Highlights

- **Genuine C extension** — a C subclass of `dict`; `isinstance(d, dict)` is
 `True`; full mapping protocol and dict methods.
- **Type attributes win on the attribute path** — `d.items` reads the real
 `dict` method; `d["items"]` keeps the key's value.
- **Recursive, cycle-safe nested conversion** at construction.
- **Copy / pickle** across all protocols (0–5), cycles preserved.
- **Stable ABI** — `cp39-abi3` wheels cover CPython 3.9–3.14.
- **Zero runtime dependencies.**

## Documentation

| Topic | Page |
|---|---|
| Installation | [installation.md](installation.md) |
| Quickstart | [quickstart.md](quickstart.md) |
| API Reference | [api.md](api.md) |
| Attribute semantics | [attribute-semantics.md](attribute-semantics.md) |
| Mapping semantics | [mapping-semantics.md](mapping-semantics.md) |
| Nested conversion | [nested.md](nested.md) |
| Serialization | [serialization.md](serialization.md) |
| Errors | [errors.md](errors.md) |
| FAQ | [faq.md](faq.md) |
| Troubleshooting | [troubleshooting.md](troubleshooting.md) |
| Architecture | [architecture.md](architecture.md) |
| Development | [development.md](development.md) |
| Performance | [performance.md](performance.md) |
| Packaging | [packaging.md](packaging.md) |
| Release | [release.md](release.md) |
| Compatibility | [compatibility.md](compatibility.md) |
| Audit | [audit.md](audit.md) |

## License

[MIT](https://github.com/jymchng/attributedict/blob/main/LICENSE)
