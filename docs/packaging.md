# Packaging

## Build system

`attributedict` uses **setuptools** with a `src/` layout (D-012, PKG-002).
The build backend is declared in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"
```

The distribution name on PyPI is **`py-attributedict`**; the import name
remains `attributedict`.

## Versioning (dynamic)

The version is derived from git tags by **setuptools-scm**
(`dynamic = ["version"]`, D-005) — the setuptools equivalent of the
`hatch-vcs` approach used by sibling projects. Tag `v0.1.0` → `0.1.0`;
no tag → `0.1.0.dev0` (fallback). `src/attributedict/__init__.py` reads it at
runtime via `importlib.metadata.version("py-attributedict")`.

## ABI strategy

The extension targets the **Limited API / Stable ABI** (`Py_LIMITED_API`
target 3.9), producing a `cp39-abi3` wheel per platform (D-002, PKG-003).
One wheel covers CPython 3.9–3.14 on a given platform.

The one exception is the **pyodide wheel**: the emscripten/WebAssembly
build (`cp313-emscripten_*_wasm32`) does not use the stable ABI, so
`setup.py` skips `py_limited_api`/abi3 tagging when `sys.platform ==
'emscripten'`.

## Wheels

`cibuildwheel` builds abi3 wheels for (PKG-006):

- manylinux x86_64, aarch64, i686, ppc64le, s390x, armv7l
  (non-x86_64 via QEMU)
- macOS arm64 + x86_64
- Windows AMD64, ARM64, x86

Plus a **pyodide wheel** (`cp313-pyodide_wasm32` → `cp313-emscripten_*_wasm32`)
built by cibuildwheel's pyodide platform for browser/WebAssembly use
(`CIBW_PLATFORM=pyodide`); it is published as an asset of the GitHub
Release and uploaded to PyPI alongside the native wheels.

Source distribution (sdist) builds from source on all supported platforms
(PKG-007).

## Build requirements

- Compiler: any C11-capable toolchain (gcc/clang/MSVC).
- Python: 3.9+ with development headers.
- Build backend: setuptools >= 68, wheel, setuptools-scm >= 8.

## Release

Releases are a manual, protected step (PKG-008, SEC-006). No publishing
credentials are configured in CI; see `docs/release.md`.
