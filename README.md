# attributedict

A production-quality CPython C extension implementing an **AttributeDict**: a `dict` subclass whose keys are also accessible through attribute syntax (`d["host"] == d.host`).

```python
from attributedict import AttributeDict

config = AttributeDict(host="localhost", port=8080)
assert config["host"] == "localhost"
assert config.host == "localhost"

config.debug = True
assert config["debug"] is True
```

## Features

- Genuine C extension (C subclass of `dict` with custom `tp_getattro`/`tp_setattro`).
- `isinstance(d, dict)` is `True`; full mapping protocol + dict methods.
- Recursive, cycle-safe nested conversion at construction.
- Deterministic keys-win collision resolution.
- Limited API / Stable ABI (abi3) wheels: CPython 3.9–3.14.
- Zero runtime dependencies.

## Documentation

See `docs/` for installation, quickstart, API reference, attribute semantics, mapping semantics, serialization, developer guide, performance, and release documentation.

## Development

```bash
nox -s tests      # run the test suite
nox -s lint       # ruff
nox -s typecheck  # mypy
nox -s build      # build sdist + wheels
```

See `CONTRIBUTING.md` and `docs/development.md`.

## License

MIT
