# Release

## Policy (PKG-008, SEC-006)

Releases are a **manual, protected step**. No publishing credentials are
configured in CI, and nothing auto-publishes except when a `v*` tag is
pushed. The `release.yml` workflow is triggered manually (or by a tag push)
and:

1. builds the sdist + the full abi3 wheel matrix (cibuildwheel) + a
   **pyodide (WebAssembly/emscripten) wheel** (`cp313-emscripten_*_wasm32`),
2. verifies artifact integrity (SHA-256) and artifact count,
3. creates a GitHub Release with the artifacts (draft),
4. publishes the artifacts to **PyPI via trusted publishing (OIDC)** as
   `py-attributedict` — no tokens or secrets are stored in the repository.

## Versioning (dynamic, D-005)

The version is **derived from the git tag** by `setuptools-scm`
(`dynamic = ["version"]` in `pyproject.toml`, the setuptools equivalent of
`hatch-vcs` used by sibling projects). Tag `v0.1.0` → package version
`0.1.0`; `v0.2.0rc1` → `0.2.0rc1`. Without any tag, the build falls back to
`0.1.0.dev0`. Do **not** edit a `version =` field in `pyproject.toml` — there
isn't one; bump by tagging.

## PyPI trusted publishing setup (one-time)

1. Register the **`py-attributedict`** project on PyPI (the import name stays
   `attributedict`; the plain `attributedict` and `attrdict` names are taken
   on PyPI by other authors).
2. On PyPI → "Your account" → "Publishing", add a publishing source:
   - **Platform**: GitHub
   - **Owner**: `jymchng`
   - **Repository**: `attributedict`
   - **Workflow**: `release.yml`
   - **Environment**: `release`
3. That's it — the `publish` job in `release.yml` authenticates via OIDC
   with no stored credentials.

## Process

1. Update `CHANGELOG.md`.
2. Build locally and verify:

   ```bash
   python -m build
   # smoke-test the wheel in a clean venv
   ```

3. Run the full validation: `nox -s tests lint typecheck coverage`.
4. Create a Git tag (`vX.Y.Z`) and push it — this also triggers
   `release.yml` on `push: tags: ['v*']`; or trigger it manually and pass
   the tag.
5. The workflow:
   - builds sdist + abi3 wheels for every platform/arch
     (Linux x86_64/aarch64/i686/ppc64le/s390x/armv7l, macOS arm64/x86_64,
     Windows AMD64/ARM64/x86),
   - builds the **pyodide wheel** (`cp313-pyodide_wasm32` →
     `cp313-emscripten_*_wasm32`) for browser/WebAssembly use,
   - verifies artifact integrity (SHA-256, SEC-006),
   - creates a GitHub Release (draft) with the artifacts,
   - publishes to PyPI via trusted publishing (OIDC).

## Integrity

Before any external distribution, verify artifact integrity (hash) as part
of the release step (SEC-006). The workflow prints SHA-256 checksums for
every artifact.
