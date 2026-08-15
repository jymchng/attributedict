# 12 — Security

## Purpose

Security and supply-chain requirements for the package.

## Scope

C memory safety, secrets, dependency hygiene, CI security.

## Requirements

- SEC-001 C memory safety is a security boundary: refcount correctness,
  no buffer overruns, no use-after-free, no leaks (see 07-memory-management).
- SEC-002 Never commit secrets or credentials. The private repo is created
  via the github-tools MCP server; no tokens in code, config, or CI logs.
- SEC-003 No third-party runtime dependencies (C-004) — reduces supply-chain
  surface. Build deps pinned in `pyproject.toml`/lock where practical.
- SEC-004 GitHub Actions use least-privilege permissions; workflow files
  declare minimal `permissions:`; no untrusted PR access to secrets.
- SEC-005 Input validation: keys/values accepted per dict semantics; no
  injection surface in a mapping type; documented.
- SEC-006 Publish only via an explicit, protected release step (no
  auto-publish); verify artifact integrity (hash) before release.

## Security Review

Final audit includes: secrets scan (gitleaks or equivalent), dependency
vulnerability check (pip-audit in CI if cheap), and a review that C code does
not introduce memory-unsafe patterns. Sanitizer jobs gate merges.

## Cross-references

- 07-memory-management, 09-packaging, 13-ci, risks.md.
