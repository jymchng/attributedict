# 14 — Documentation

## Purpose

The documentation plan for users, developers, and operators.

## Scope

User, developer, packaging, and performance docs.

## Documents

### README.md
Project intro, install, quickstart, API summary, supported versions,
contributing link, license.

### docs/
- **installation.md** — pip install (wheel/source), supported Python
  3.9–3.14, platforms.
- **quickstart.md** — the AttributeDict examples.
- **api.md** — full API reference (08-api-specification).
- **attribute-semantics.md** — resolution order, keys-win rule, edge cases.
- **mapping-semantics.md** — dict compatibility and deviations.
- **nested.md** — recursive conversion rules.
- **serialization.md** — pickle/copy/deepcopy.
- **errors.md** — exception contract.
- **architecture.md** — C object design, layout, refcounts, GC.
- **development.md** — build from source, run tests, sanitizers.
- **benchmarks.md** — methodology + results (11-performance).
- **packaging.md** — source build, abi3 wheels, platform support.
- **release.md** — release process.
- **troubleshooting.md** — common issues.
- **FAQ.md** — frequently asked questions.

### CONTRIBUTING.md, SECURITY.md, CHANGELOG.md, LICENSE (MIT)

## Requirements

- DOC-001 Every documented behavior is tested.
- DOC-002 Typing limitations documented honestly (no fake precision).
- DOC-003 Performance claims backed by measured data.
- DOC-004 Compatibility matrix explicitly lists supported/unsupported
  environments (CPython 3.9–3.14; no PyPy/free-threaded).

## Cross-references

- 04-non-functional-requirements (NFR-010), 08-api-specification,
  09-packaging, 11-performance.
