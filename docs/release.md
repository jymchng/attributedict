# Release

## Policy (PKG-008, SEC-006)

Releases are a **manual, protected step**. No publishing credentials are
configured in CI, and nothing auto-publishes. The `release.yml` workflow is
triggered manually and:

1. builds the sdist + abi3 wheels (cibuildwheel matrix),
2. verifies artifact integrity (SHA-256),
3. creates a GitHub Release with the artifacts (draft),
4. publishes the artifacts to **PyPI via trusted publishing (OIDC)** —
   no tokens or secrets are stored in the repository.

## PyPI trusted publishing setup (one-time)

1. Create or claim the `attributedict` project on PyPI.
2. On PyPI → "Your account" → "Publishing", add a publishing source:
   - **Platform**: GitHub
   - **Owner**: `jymchng`
   - **Repository**: `attributedict`
   - **Workflow**: `release.yml`
   - **Environment**: `release`
3. That's it — the `publish` job in `release.yml` authenticates via OIDC
   with no stored credentials.

## Process

1. Bump the version in `pyproject.toml` / `src/attributedict/__init__.py`.
2. Update `CHANGELOG.md`.
3. Build locally and verify:

   ```bash
   python -m build
   # smoke-test the wheel in a clean venv
   ```

4. Run the full validation: `nox -s tests lint typecheck coverage`.
5. Create a Git tag (`vX.Y.Z`) and push it.
6. Run the `release.yml` workflow (manual trigger, passing the tag), which:
   - builds sdist + abi3 wheels (cibuildwheel matrix),
   - verifies artifact integrity (SHA-256, SEC-006),
   - creates a GitHub Release (draft) with the artifacts,
   - publishes to PyPI via trusted publishing (OIDC).

## Integrity

Before any external distribution, verify artifact integrity (hash) as part
of the release step (SEC-006). The workflow prints SHA-256 checksums for
every artifact.
