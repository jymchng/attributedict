# Changelog

All notable changes to `attributedict` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-15

Initial release.

### Added

- `AttributeDict`: a CPython C extension `dict` subclass with attribute
  access (`d["host"] == d.host`), keys-win collision resolution, recursive
  cycle-safe nested conversion, `AttributeDict({...})` repr, dict-semantics
  equality, unhashable, copy/deepcopy/pickle (all protocols) with cycles.
- `cp39-abi3` wheels for manylinux x86_64/aarch64, macOS arm64/x86_64,
  Windows x86_64; sdist builds from source.
- Full test suite (191 tests), benchmarks vs dict + pure-Python reference,
  sanitizer (ASan/UBSan) CI, ruff/mypy/nox/pre-commit tooling, GitHub
  Actions CI/CD.
- Documentation: user, developer, packaging, performance, FAQ.

### Fixed

- Subclass instantiation recursion (tp_new/tp_init/tp_dealloc used
  `Py_TYPE(self)->tp_base` indirection; now call `PyDict_Type.*` directly).
- Pickle protocols 0–1 (`__reduce__` added; 5-tuple iteritems form).

### Security

- Zero runtime dependencies; least-privilege CI; protected manual release.
