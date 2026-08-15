# attributedict

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow.

## Quick start

1. Build in place: `pip install -e .` (or `nox -s tests`).
2. Run the tests: `nox -s tests`.
3. Lint and typecheck: `nox -s lint typecheck`.

## Pull requests

- Follow the specification-driven workflow: requirements → spec → issues → implementation → tests → packaging → CI → audit.
- Every behavior change updates `spec/` and `CHANGELOG.md`.
- Tests must pass under `nox -s tests`; memory-safety jobs (ASan/UBSan) must be clean.
