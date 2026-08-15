# Packaging

## Build system

`attributedict` uses **setuptools** with a `src/` layout (D-012, PKG-002).
The build backend is declared in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
```

## ABI strategy

The extension targets the **Limited API / Stable ABI** (`Py_LIMITED_API`
target 3.9), producing a `cp39-abi3` wheel per platform (D-002, PKG-003).
One wheel covers CPython 3.9–3.14 on a given platform.

## Wheels

`cibuildwheel` builds abi3 wheels for (PKG-006):

- manylinux x86_64 + aarch64
- macOS arm64 + x86_64
- Windows x86_64

Source distribution (sdist) builds from source on all supported platforms
(PKG-007).

## Build requirements

- Compiler: any C11-capable toolchain (gcc/clang/MSVC).
- Python: 3.9+ with development headers.
- Build backend: setuptools >= 68, wheel.

## Release

Releases are a manual, protected step (PKG-008, SEC-006). No publishing
credentials are configured in CI; see `docs/release.md`.
