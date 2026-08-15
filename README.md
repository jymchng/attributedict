# attributedict

[![CI](https://github.com/jymchng/attributedict/actions/workflows/tests.yml/badge.svg)](https://github.com/jymchng/attributedict/actions/workflows/tests.yml)
[![Lint](https://github.com/jymchng/attributedict/actions/workflows/lint.yml/badge.svg)](https://github.com/jymchng/attributedict/actions/workflows/lint.yml)
[![Wheels](https://github.com/jymchng/attributedict/actions/workflows/wheels.yml/badge.svg)](https://github.com/jymchng/attributedict/actions/workflows/wheels.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](docs/installation.md)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](docs/compatibility.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-quality **CPython C extension** implementing an `AttributeDict`:
a `dict` subclass whose keys are also accessible through attribute syntax
(`d["host"] == d.host`).

```python
from attributedict import AttributeDict

config = AttributeDict(host="localhost", port=8080)
assert config["host"] == "localhost"
assert config.host == "localhost"

config.debug = True
assert config["debug"] is True
```

## Features

- **Genuine C extension** — a C subclass of `dict` with custom
  `tp_getattro`/`tp_setattro`; `isinstance(d, dict)` is `True`.
- **Keys win** — a key named `items`/`keys`/`get`/... shadows the method;
  the mapping view stays reachable via `dict.items(d)` (FR-006).
- **Recursive nested conversion** at construction, cycle-safe: nested dicts
  (and dicts inside lists/tuples) become `AttributeDict` (FR-007).
- **Full dict compatibility** — mapping protocol, dict methods, views,
  `MutableMapping`; `copy()`/`fromkeys` return `AttributeDict` (FR-008/009).
- **repr/equality/unhashable** — `AttributeDict({...})`, dict semantics,
  unhashable like dict (FR-010/011/012).
- **Copy / pickle** — `copy.copy`, `copy.deepcopy`, `pickle` across all
  protocols (0–5), cycles preserved (FR-013).
- **Stable ABI** — `cp39-abi3` wheels cover CPython **3.9–3.14**.
- **Zero runtime dependencies.**

## Installation

```bash
pip install attributedict          # wheels / sdist
```

Requires CPython 3.9–3.14. PyPy and free-threaded 3.13t are not supported
in v1. See [docs/installation.md](docs/installation.md).

## Documentation

| Topic | Doc |
|---|---|
| Quickstart | [docs/quickstart.md](docs/quickstart.md) |
| API reference | [docs/api.md](docs/api.md) |
| Attribute semantics (keys win) | [docs/attribute-semantics.md](docs/attribute-semantics.md) |
| Mapping semantics | [docs/mapping-semantics.md](docs/mapping-semantics.md) |
| Nested conversion | [docs/nested.md](docs/nested.md) |
| Serialization | [docs/serialization.md](docs/serialization.md) |
| Errors | [docs/errors.md](docs/errors.md) |
| FAQ | [docs/faq.md](docs/faq.md) |
| Architecture (C) | [docs/architecture.md](docs/architecture.md) |
| Development | [docs/development.md](docs/development.md) |
| Performance | [docs/performance.md](docs/performance.md) |
| Packaging | [docs/packaging.md](docs/packaging.md) |
| Release | [docs/release.md](docs/release.md) |

## Development

```bash
nox -s tests       # pytest
nox -s lint        # ruff
nox -s typecheck   # mypy (strict)
nox -s coverage    # coverage (>= 80%)
nox -s build       # sdist + abi3 wheel
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/development.md](docs/development.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
