<p align="center">
 <a href="https://github.com/jymchng/attributedict">
 <img src="https://raw.githubusercontent.com/jymchng/attributedict/main/docs/assets/logo.png" alt="attributedict" width="120">
 </a>
</p>

<h1 align="center">attributedict</h1>

<p align="center">
 <b>dict semantics with attribute access.</b><br>
 A production-quality <b>CPython C extension</b> implementing an <code>AttributeDict</code> —<br>
 a real <code>dict</code> whose keys you can also reach with dot notation.
</p>

<p align="center">
 <a href="https://github.com/jymchng/attributedict/actions/workflows/tests.yml"><img src="https://github.com/jymchng/attributedict/actions/workflows/tests.yml/badge.svg" alt="CI"></a>
 <a href="https://github.com/jymchng/attributedict/actions/workflows/lint.yml"><img src="https://github.com/jymchng/attributedict/actions/workflows/lint.yml/badge.svg" alt="Lint"></a>
 <a href="https://github.com/jymchng/attributedict/actions/workflows/wheels.yml"><img src="https://github.com/jymchng/attributedict/actions/workflows/wheels.yml/badge.svg" alt="Wheels"></a>
 <a href="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue"><img src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg" alt="Python 3.9–3.14"></a>
 <a href="https://img.shields.io/badge/coverage-92%25-brightgreen"><img src="https://img.shields.io/badge/coverage-92%25-brightgreen.svg" alt="Coverage 92%"></a>
 <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
</p>

---

**Documentation:** [https://jymchng.github.io/attributedict/](https://jymchng.github.io/attributedict/) ·
**Repository:** [https://github.com/jymchng/attributedict](https://github.com/jymchng/attributedict)

---

## Example

Here's what it feels like to use:

```python
from attributedict import AttributeDict

config = AttributeDict(host="localhost", port=8080)

config["host"] # "localhost"
config.host # "localhost" — attribute access, same data

config.debug = True # stores config["debug"] = True
config["debug"] # True
```

Nested mappings become `AttributeDict` automatically:

```python
settings = AttributeDict({
 "database": {"host": "localhost", "ports": [5432, {"tls": True}]},
})

settings.database.host # "localhost"
settings.database.ports[1].tls # True
```

## Features

- ✅ **Genuine C extension** — a C subclass of `dict` with custom
 `tp_getattro`/`tp_setattro`; `isinstance(d, dict)` is `True`.
- ✅ **Type attributes win on the attribute path** — `d.items` reads the real
 `dict` method even when a key `"items"` exists; `d["items"]` keeps the
 key's value.
- ✅ **Recursive nested conversion** — cycle-safe at construction; dicts inside
 lists/tuples become `AttributeDict`.
- ✅ **Full dict compatibility** — mapping protocol, dict methods, views,
 `MutableMapping`; `copy`/`fromkeys` return `AttributeDict`.
- ✅ **Copy & pickle** — `copy.copy`, `copy.deepcopy`, and `pickle` across all
 protocols (0–5), cycles preserved.
- ✅ **Stable ABI** — `cp39-abi3` wheels cover CPython **3.9–3.14**.
- ✅ **Zero runtime dependencies.**

## Requirements

- **CPython 3.9 – 3.14** (Linux, macOS, Windows).
- PyPy and free-threaded CPython 3.13t are **not** supported in v1.

## Installation

```bash
pip install py-attributedict
```

This installs the `cp39-abi3` wheel for your platform (or builds from source).
Quick note on naming: you import `attributedict`, but the package on PyPI is
`py-attributedict` — the plain names `attributedict` / `attrdict` were
already taken on PyPI by unrelated projects.

## Key highlights

- **It's a real dict.** `isinstance(config, dict)`, `dict(config)`, views,
 and all `dict` methods just work.
- **Attribute access mirrors mapping access.** `config.host` and
 `config["host"]` read the same value; assignment and deletion work too.
- **Nested data, attribute style.** `settings.database.host` instead of
 `settings["database"]["host"]`.
- **Predictable collisions.** Keys never shadow methods on the attribute
 path: `d.items` is the method, `d["items"]` is the key's value.

## Documentation

Full documentation is published at
**[https://jymchng.github.io/attributedict/](https://jymchng.github.io/attributedict/)**
(MkDocs + Material).

| Topic | Doc |
|---|---|
| Installation | [docs/installation.md](docs/installation.md) |
| Quickstart | [docs/quickstart.md](docs/quickstart.md) |
| API reference | [docs/api.md](docs/api.md) |
| Attribute semantics | [docs/attribute-semantics.md](docs/attribute-semantics.md) |
| Mapping semantics | [docs/mapping-semantics.md](docs/mapping-semantics.md) |
| Nested conversion | [docs/nested.md](docs/nested.md) |
| Serialization | [docs/serialization.md](docs/serialization.md) |
| Errors | [docs/errors.md](docs/errors.md) |
| FAQ | [docs/faq.md](docs/faq.md) |
| Performance | [docs/performance.md](docs/performance.md) |
| Release | [docs/release.md](docs/release.md) |

## Development

```bash
nox -s tests # pytest
nox -s lint # ruff
nox -s typecheck # mypy (strict)
nox -s coverage # coverage (>= 80%)
nox -s build # sdist + abi3 wheel
```

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/development.md](docs/development.md).

## Security

Found something? See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
