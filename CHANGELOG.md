# Changelog

All notable changes to `attributedict` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.6] - 2026-08-17

### Fixed

- **Crash on Pyodide (WebAssembly): any positional-argument construction
  (`AttributeDict({...})`, `AttributeDict(())`, `AttributeDict([...])`) and
  nested-tuple values fatally crashed pyodide 314.0.3 with
  `RuntimeError: memory access out of bounds`.** Root cause: the extension's
  inline `PyTuple_GET_SIZE`/`PyTuple_GET_ITEM`/`PyTuple_SET_ITEM` macros are
  compiled against a `PyTupleObject` layout that no longer matches CPython
  3.14 (the pyodide 314.0.3 runtime) on Emscripten/wasm32, so they read/write
  `ob_item` at a stale offset, producing garbage pointers that trap the wasm
  runtime. The fix replaces those macros with the libpython **function** forms
  (`PyTuple_Size`/`PyTuple_GetItem`/`PyTuple_SetItem`) and parses the `tp_init`
  source mapping with `PyArg_ParseTuple` — functions implemented in libpython
  with the runtime's own layout (the same reason `conditional-method._c`
  works on pyodide). Verified on pyodide 314.0.3: positional map/list/tuple
  construction, nested tuples, kwargs, and the self-referential cycle case
  (`d.self.back is d`) all work.

## [0.2.5] - 2026-08-16

### Fixed

- **Pyodide wheel is now actually installable in Pyodide 314.0.3** (the
  AsyncMove playground). The release pipeline re-tags the wheel from
  `pyemscripten_2025_0_wasm32` to `emscripten_5_0_3_wasm32` (filename,
  `WHEEL` metadata, and recomputed `RECORD` hashes — the binary is
  unchanged) before uploading, because micropip 0.11.1's
  `platform_to_version()` only strips the `emscripten_` prefix and rejected
  the `pyemscripten_*` tag with `ValueError: Wheel was built with Emscripten
  vpyemscripten.2025.0 but Pyodide was built with Emscripten v5.0.3`.
  Resolves the caveat noted in 0.2.4.

## [0.2.4] - 2026-08-16

### Changed

- **Pyodide wheel now targets Emscripten 5.0.3** (pyodide 314.0.3): the
  release workflow pins `pyodide-version: 314.0.3`, so the `*.whl` built
  for the browser runs on the AsyncMove playground's Pyodide runtime.
  Previously the wheel was tagged `pyemscripten_2025_0_wasm32` and micropip
  rejected it with `ValueError: Wheel was built with Emscripten
  vpyemscripten.2025.0 but Pyodide was built with Emscripten v5.0.3`.

## [0.2.3] - 2026-08-16

### Changed

- Removed all traceability codes (issue/requirement references) from the
  documentation and README — the docs now read as plain, self-contained
  prose with the same technical content.
- Documented non-string (e.g. class) key behavior: mapping access reads any
  hashable key, attribute syntax reads string-identifier keys only.

## [0.2.2] - 2026-08-16

### Changed

- User-facing documentation rewritten in a friendly, conversational tone
  (README + installation/quickstart/api/attribute-semantics/mapping-semantics/
  nested/serialization/faq/troubleshooting/index) — same technical content,
  structure, and code examples, just more approachable prose.

### Fixed

- `docs/quickstart.md` had a stale "keys win" example; corrected to the
  I-024 behavior (`d.items` returns the real `dict` method, `d["items"]`
  keeps the key's value).

## [0.2.1] - 2026-08-15

### Fixed

- README logo now uses an absolute `raw.githubusercontent.com` URL so the
  image renders on the PyPI project page (Warehouse does not resolve
  relative README image paths).
- README now prominently links the documentation site
  (`https://OWNER.github.io/attributedict/`) and the repository
  (`https://github.com/OWNER/attributedict`) near the top.

## [0.2.0] - 2026-08-15

### Added

- `py-attributedict` distribution on PyPI (import stays `attributedict`);
  published via trusted publishing (OIDC), no stored credentials.
- Dynamic versioning via `setuptools-scm` (version derived from git tags;
  `__version__` read at runtime through `importlib.metadata`).
- Many-arch `cp39-abi3` wheel matrix: Linux manylinux
  x86_64/aarch64/i686/ppc64le/s390x/armv7l (QEMU), macOS arm64/x86_64,
  Windows AMD64/ARM64/x86; full matrix built on tag/release, cheap subset
  on PRs.
- MkDocs + Material documentation site deployed to GitHub Pages
  (`https://OWNER.github.io/attributedict/`), project logo, and a
  FastAPI-style README.

### Changed

- Attribute access now prefers real dict attributes on the attribute path
  (`d.items` is the bound method) while mapping access keeps key values
  (`d["items"] == 42`) — I-024 resolution-order change.
- C-extension gcov coverage raised above 90% (test-only allocation-failure
  injection behind `PY_ATTRIBUTEDICT_TESTING`); production wheels ship no
  test hooks.
- CI workflows hardened: coverage/sanitizers import path, modern-gcc gcov
  parsing, libasan preload for ASan on non-instrumented CPython,
  cibuildwheel v4.2.0 + AMD64/ARM64 Windows arch names.

### Fixed

- Real NULL-safety bug in `tp_repr` (`Py_ReprEnter`/`Py_ReprLeave` contract
  on recursion-detected and error paths).

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
