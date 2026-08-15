# Installation

## Requirements

- Python **3.9–3.14** (CPython only; see [compatibility](#compatibility)).
- No third-party runtime dependencies (C-004).

## From PyPI (when published)

```bash
pip install attributedict
```

## From source

```bash
git clone https://github.com/jymchng/attributedict.git
cd attributedict
pip install .
```

Or in editable mode for development:

```bash
pip install -e .
```

## Build requirements

Compiling from source requires:

- a C11-capable compiler (gcc/clang/MSVC),
- Python development headers for your interpreter,
- setuptools >= 68 and wheel (pulled in automatically by the build backend).

## Wheels

`cp39-abi3` wheels are provided for:

- manylinux x86_64 + aarch64
- macOS arm64 + x86_64
- Windows x86_64

One abi3 wheel covers CPython 3.9–3.14 on its platform.

## Compatibility

| Environment | Supported |
|---|---|
| CPython 3.9–3.14 | ✅ (abi3 wheel or source build) |
| PyPy | ❌ (not supported in v1) |
| Free-threaded CPython 3.13t | ❌ (not supported in v1) |
| Linux x86_64 / aarch64 | ✅ |
| macOS arm64 / x86_64 | ✅ |
| Windows x86_64 | ✅ |

See also [packaging.md](packaging.md) and the [FAQ](faq.md).
