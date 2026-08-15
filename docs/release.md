# Release

## Policy (PKG-008, SEC-006)

Releases are a **manual, protected step**. No publishing credentials are
configured in CI, and nothing auto-publishes. The `release.yml` workflow
(I-017) is triggered manually (or by a tag) and creates a GitHub Release
with the built artifacts — it never pushes to PyPI unless a trusted
publisher environment is explicitly configured by the maintainer.

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
6. Run the `release.yml` workflow (manual trigger) which:
   - builds sdist + abi3 wheels (cibuildwheel matrix),
   - validates each wheel installs + passes the smoke test,
   - creates a GitHub Release with the artifacts.

## Integrity

Before any external distribution, verify artifact integrity (hash) as part
of the release step (SEC-006).
