# Installation

## Requirements

- Python **3.9–3.14** (CPython only; see [compatibility](#compatibility)).
- No third-party runtime dependencies.

## From PyPI (when published)

```bash
pip install py-attributedict
```

That's the whole install story — one command and you're set. Just so you
know: the import name is `attributedict`, even though the package on PyPI is
called `py-attributedict`. Why the difference? The plain names
`attributedict` / `attrdict` were already taken on PyPI by unrelated
projects, so this distribution uses `py-attributedict` instead.

## From source

```bash
git clone https://github.com/OWNER/attributedict.git
cd attributedict
pip install.
```

Or, if you're planning to hack on the code, install in editable mode:

```bash
pip install -e.
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

If your setup isn't on this list, don't worry — just check
[packaging.md](packaging.md) for the full story, or skim the [FAQ](faq.md)
for quick answers.
