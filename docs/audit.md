# Final Audit

**Date:** 2026-08-15
**Repo:** https://github.com/OWNER/attributedict
**Version audited:** 0.1.0 (HEAD `2c8da38`)

## 1. Traceability Matrix

The full chain *Intent → Requirements → Spec → Issues → Implementation →
Tests → Packaging → CI → Docs* is closed for every requirement. No orphaned
requirements.


### Functional requirements

| Requirement | Spec | Tests |
| --- | --- | --- |
| Type/package identity | 01, 03, 08 | test_bootstrap, test_c_extension |
| All dict construction forms | 03, 08 | test_nested, test_reference |
| Attribute get (keys win) | 03, 05, 08 | test_attributes, test_reference |
| Attribute set → mapping | 03, 08 | test_attributes, test_reference |
| Attribute delete (AttributeError) | 03, 08 | test_attributes, test_errors |
| Keys win over methods | 03, 08 | test_attributes, test_mapping, test_c_extension |
| Recursive cycle-safe conversion | 03, 06 | test_nested, test_memory, test_property_based |
| Mapping protocol + MutableMapping | 03, 05 | test_mapping, test_c_extension |
| dict methods; copy/fromkeys → AttributeDict | 03, 08 | test_mapping, test_reference |
| repr `AttributeDict({...})` | 03, 08 | test_repr_equality_hash |
| dict equality | 03, 08 | test_repr_equality_hash |
| Unhashable | 03, 08 | test_repr_equality_hash, test_errors |
| pickle/copy incl. cycles | 03, 08 | test_copy_pickle |
| Edge-case keys | 03, 08 | test_errors, test_attributes |
| Error semantics, no stale exceptions | 03, 07, 08 | test_errors, test_memory |

### Non-functional requirements

| Requirement | Spec | Evidence |
| --- | --- | --- |
| CPython 3.9–3.14 | 04 | tests.yml matrix; compat docs (3.10–3.14 locally, 3.9 in CI) |
| C subclass of dict | 04, 05 | isinstance(d,dict); tp_base=dict |
| abi3 | 04, 09 | cp39-abi3 wheel; verified on 3.10 |
| Memory safety | 04, 07 | ASan/UBSan CI, stress tests, refcount smoke |
| GIL-thread-safe | 04 | dict-subclass inherits GIL semantics (documented) |
| Benchmarks vs dict/reference | 04, 11 | benchmarks/results/results.json; docs/performance.md |
| Packaging | 04, 09 | sdist + abi3 wheel; cibuildwheel matrix |
| CI matrix | 04, 13 | tests/lint/sanitizers/wheels/docs/release/coverage workflows |
| Dev tooling | 04 | ruff, mypy, nox, pre-commit; all gates green |
| Documentation | 04, 14 | 16-doc set + README + SECURITY + CHANGELOG |

### Security requirements

| Requirement | Spec | Evidence |
| --- | --- | --- |
| C memory safety as boundary | 12 | ASan/UBSan clean; code-review checklist (spec 07) |
| No secrets committed | 12 | repo-wide scan clean (this audit) |
| Zero runtime deps | 12 | `dependencies = []` |
| Least-privilege Actions | 12, 13 | per-workflow `permissions:`; contents: read default |
| dict-semantics input validation | 12 | no injection surface in a mapping type |
| No auto-publish; integrity check | 12, 09 | release.yml manual-trigger + sha256 |
## 2. Requirements Implemented vs Rejected

**Implemented:** all recorded requirements (functional, non-functional,
security, memory, packaging, and documentation) were delivered and verified.

**Rejected / deferred (documented):**
- PyPI publishing — deferred (no publishing credentials by design).
- YAML/dataclass/pydantic interop — out of v1 scope.
- Free-threaded CPython 3.13t and PyPy — unsupported in v1;
 documented in docs/compatibility.md.
- Weakref support — matches dict (dict has none).

## 3. Assumptions

All eight recorded assumptions held during implementation and remain valid:
package/import/repo name `attributedict`; repr format; recursive conversion;
keys win; unhashable; no free-threaded support; wheel matrix; no
YAML/dataclass interop.

## 4. Known Limitations & Technical Debt

- **C line coverage 92.34%** : the C core is measured with
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
 passwords — none found; excludes.git).
- **Dependency check:** zero runtime dependencies; build deps
 pinned in `pyproject.toml` `[build-system]`.
- **C memory-safety review:** ASan/UBSan CI job (sanitizers.yml) runs the
 full suite + stress; refcount/GC contract documented in spec 07 with a
 code-review checklist; no-stale-exception discipline enforced.
- **Least privilege:** all workflows declare minimal `permissions:`;
 release.yml scopes `contents: write` only for the release job.
- **No publishing credentials** anywhere.

## 6. Reproducibility

- `python -m build` from a clean tree produces `py_attributedict-<version>.tar.gz`
 and `py_attributedict-<version>-cp39-abi3-linux_x86_64.whl` (version derived
 from git tags by setuptools-scm).
- The abi3 wheel installs and passes a smoke test in a fresh venv
 (verified this audit).
- Benchmarks committed as data (`benchmarks/results/results.json`) with
 environment captured; docs/performance.md summarizes honestly.

## 7. Version / Platform / ABI / Performance / Security Summary

- **Supported:** CPython 3.9–3.14; manylinux x86_64/aarch64/i686/ppc64le/s390x/armv7l, macOS arm64/x86_64, Windows AMD64/ARM64/x86 (wheels.yml matrix).
- **Unsupported:** PyPy, free-threaded 3.13t.
- **ABI:** Limited API / Stable ABI (`cp39-abi3`); `PyObject_VisitManagedDict`
 is NOT public — portable `Py_VISIT`/`Py_CLEAR` used.
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
