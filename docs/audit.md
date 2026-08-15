# Final Audit (I-020)

**Date:** 2026-08-15
**Repo:** https://github.com/jymchng/attributedict
**Version audited:** 0.1.0 (HEAD `2c8da38`)

## 1. Traceability Matrix

The full chain *Intent → Requirements → Spec → Issues → Implementation →
Tests → Packaging → CI → Docs* is closed for every requirement. No orphaned
requirements.

### Functional requirements

| ID | Requirement | Spec | Issues | Tests |
|---|---|---|---|---|
| FR-001 | Type/package identity | 01, 03, 08 | I-001, I-002, I-005 | test_bootstrap, test_c_extension |
| FR-002 | All dict construction forms | 03, 08 | I-006 | test_nested, test_reference |
| FR-003 | Attribute get (keys win) | 03, 05, 08 | I-008 | test_attributes, test_reference |
| FR-004 | Attribute set → mapping | 03, 08 | I-008 | test_attributes, test_reference |
| FR-005 | Attribute delete (AttributeError) | 03, 08 | I-008, I-011 | test_attributes, test_errors |
| FR-006 | Keys win over methods | 03, 08 | I-002, I-008 | test_attributes, test_mapping, test_c_extension |
| FR-007 | Recursive cycle-safe conversion | 03, 06 | I-006 | test_nested, test_memory, test_property_based |
| FR-008 | Mapping protocol + MutableMapping | 03, 05 | I-007 | test_mapping, test_c_extension |
| FR-009 | dict methods; copy/fromkeys → AttributeDict | 03, 08 | I-007 | test_mapping, test_reference |
| FR-010 | repr `AttributeDict({...})` | 03, 08 | I-009 | test_repr_equality_hash |
| FR-011 | dict equality | 03, 08 | I-009 | test_repr_equality_hash |
| FR-012 | Unhashable | 03, 08 | I-009 | test_repr_equality_hash, test_errors |
| FR-013 | pickle/copy incl. cycles | 03, 08 | I-010 | test_copy_pickle |
| FR-014 | Edge-case keys | 03, 08 | I-008, I-011 | test_errors, test_attributes |
| FR-015 | Error semantics, no stale exceptions | 03, 07, 08 | I-011 | test_errors, test_memory |

### Non-functional requirements

| ID | Requirement | Spec | Issues | Evidence |
|---|---|---|---|---|
| NFR-001 | CPython 3.9–3.14 | 04 | I-003, I-019 | tests.yml matrix; compat docs (3.10–3.14 locally, 3.9 in CI) |
| NFR-002 | C subclass of dict | 04, 05 | I-005 | isinstance(d,dict); tp_base=dict |
| NFR-003 | abi3 | 04, 09 | I-003, I-005, I-015 | cp39-abi3 wheel; verified on 3.10 |
| NFR-004 | Memory safety | 04, 07 | I-012 | ASan/UBSan CI, stress tests, refcount smoke |
| NFR-005 | GIL-thread-safe | 04 | — | dict-subclass inherits GIL semantics (documented) |
| NFR-006 | Benchmarks vs dict/reference | 04, 11 | I-014 | benchmarks/results/results.json; docs/performance.md |
| NFR-007 | Packaging | 04, 09 | I-015 | sdist + abi3 wheel; cibuildwheel matrix |
| NFR-008 | CI matrix | 04, 13 | I-017 | tests/lint/sanitizers/wheels/docs/release/coverage workflows |
| NFR-009 | Dev tooling | 04 | I-016 | ruff, mypy, nox, pre-commit; all gates green |
| NFR-010 | Documentation | 04, 14 | I-018 | 16-doc set + README + SECURITY + CHANGELOG |

### Security requirements

| ID | Requirement | Spec | Issues | Evidence |
|---|---|---|---|---|
| SEC-001 | C memory safety as boundary | 12 | I-004, I-012 | ASan/UBSan clean; code-review checklist (spec 07) |
| SEC-002 | No secrets committed | 12 | all | repo-wide scan clean (this audit) |
| SEC-003 | Zero runtime deps | 12 | I-001 | `dependencies = []` |
| SEC-004 | Least-privilege Actions | 12, 13 | I-017 | per-workflow `permissions:`; contents: read default |
| SEC-005 | dict-semantics input validation | 12 | I-006..011 | no injection surface in a mapping type |
| SEC-006 | No auto-publish; integrity check | 12, 09 | I-015, I-017 | release.yml manual-trigger + sha256 |

## 2. Requirements Implemented vs Rejected

**Implemented:** all FR-001…FR-015, NFR-001…NFR-010, SEC-001…SEC-006,
MEM-001…MEM-009, PKG-001…PKG-009, DOC-001…DOC-004.

**Rejected / deferred (documented):**
- PyPI publishing — deferred (C-006; no publishing credentials by design).
- YAML/dataclass/pydantic interop — out of v1 scope (A-008).
- Free-threaded CPython 3.13t and PyPy — unsupported in v1 (NFR-001, A-006);
  documented in docs/compatibility.md.
- Weakref support — matches dict (dict has none); MEM-009.

## 3. Assumptions (A-001…A-008)

All eight recorded assumptions held during implementation and remain valid:
package/import/repo name `attributedict`; repr format; recursive conversion;
keys win; unhashable; no free-threaded support; wheel matrix; no
YAML/dataclass interop.

## 4. Known Limitations & Technical Debt

- **C line coverage 92.34%** (I-021/I-023): the C core is measured with
  gcov (209 executable lines) and CI gates at **> 90%** via the test-only
  `PY_ATTRIBUTEDICT_TESTING` allocation-failure switch
  (`tests/test_failinject.py`); the small uncovered remainder is module-init
  and a few OOM paths not driven by the sweep. No fault-injection code ships
  in production wheels.
- **Python-layer coverage** measures only the pure-Python wrapper/reference
  (~98%); the C core is measured by gcov (above).
- **3.9 CI coverage**: 3.9 runs in the tests.yml matrix but was not
  locally validated (3.10–3.14 were); abi3 wheel targets 3.9+.
- **Single-file C source** (~600 lines): acceptable at this size; split into
  module.c/attributes.c/conversion.c if it grows (documented in spec 05).
- **`setup.py` + `pyproject.toml` dual config**: required for the abi3
  wheel tag (`bdist_wheel py_limited_api`); documented in setup.py.

## 5. Security Review

- **Secrets scan:** clean (repo-wide grep for PATs, private keys, AWS keys,
  passwords — none found; excludes .git).
- **Dependency check:** zero runtime dependencies (C-004); build deps
  pinned in `pyproject.toml` `[build-system]`.
- **C memory-safety review:** ASan/UBSan CI job (sanitizers.yml) runs the
  full suite + stress; refcount/GC contract documented in spec 07 with a
  code-review checklist; MEM-004 no-stale-exception discipline enforced.
- **Least privilege:** all workflows declare minimal `permissions:`;
  release.yml scopes `contents: write` only for the release job.
- **No publishing credentials** anywhere (C-006).

## 6. Reproducibility

- `python -m build` from a clean tree produces `attributedict-0.1.0.tar.gz`
  and `attributedict-0.1.0-cp39-abi3-linux_x86_64.whl`.
- The abi3 wheel installs and passes a smoke test in a fresh venv
  (verified this audit).
- Benchmarks committed as data (`benchmarks/results/results.json`) with
  environment captured; docs/performance.md summarizes honestly.

## 7. Version / Platform / ABI / Performance / Security Summary

- **Supported:** CPython 3.9–3.14; manylinux x86_64/aarch64, macOS
  arm64/x86_64, Windows x86_64 (wheels.yml matrix).
- **Unsupported:** PyPy, free-threaded 3.13t.
- **ABI:** Limited API / Stable ABI (`cp39-abi3`); `PyObject_VisitManagedDict`
  is NOT public (R-001) — portable `Py_VISIT`/`Py_CLEAR` used.
- **Performance:** C is at parity with plain dict for inherited ops and
  3–17× faster than the pure-Python reference; construction carries the
  documented O(n) conversion cost (measured, no unsupported claims).
- **Security:** zero runtime deps; sanitizer-validated memory safety;
  protected manual release.

## 8. Conclusion

The repository satisfies its specification: all 15 functional requirements,
10 non-functional requirements, and 6 security requirements are
implemented, tested (191 tests), packaged (sdist + abi3 wheels), CI-gated
(tests/lint/sanitizers/wheels/docs/release/coverage), documented (16 docs +
README/SECURITY/CHANGELOG), and benchmarked. No orphaned requirements;
secrets clean; reproducible builds verified. **Audit PASSED.**
