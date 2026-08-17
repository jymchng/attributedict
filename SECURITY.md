# Security

## Reporting a vulnerability

If you discover a security issue in `attributedict`, please **do not** open
a public issue. Contact the maintainers privately via GitHub's security
advisory workflow.

Please include:

- a minimal reproduction,
- the affected version(s),
- the impact and any proposed fix.

## Security posture

- The C extension is a memory-safety boundary: refcount correctness, GC
  participation, and error-path discipline are enforced by code review
  (spec 07 checklist), the ASan/UBSan CI job, and stress tests.
- Zero third-party runtime dependencies (C-004) — minimal supply-chain
  surface.
- No secrets or credentials are committed; tokens are provided via
  environment variables only.
- GitHub Actions workflows use least-privilege permissions (SEC-004).
- Releases are manual and protected; artifacts are integrity-checked
  (SEC-006).

## Supported versions

Security fixes are provided for the latest release. See the
[compatibility matrix](docs/installation.md) for supported environments.
