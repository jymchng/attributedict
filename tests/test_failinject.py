"""I-023: deterministic allocation-failure tests (test-only fault injection).

The C extension is built with PY_ATTRIBUTEDICT_TESTING (test builds only)
which exposes ``set_allocation_fail_count(n)``: setting n >= 0 lets n
allocations succeed then fails the (n+1)-th. Sweeping n deterministically
covers every OOM branch in _attributedict.c (the standard CPython
_testcapi.set_nomemory approach).

Each (operation, n) runs in a FRESH subprocess: fault injection inside
tp_init/tp_dealloc can leave an interpreter in a fragile state, and a
segfault in one run must not poison the parent pytest process. The
subprocess asserts the operation raises MemoryError.

Production wheels never define PY_ATTRIBUTEDICT_TESTING, so no
fault-injection code ships.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

import attributedict._attributedict as cmod
import pytest

pytestmark = pytest.mark.skipif(
    not hasattr(cmod, "set_allocation_fail_count"),
    reason="extension not built with PY_ATTRIBUTEDICT_TESTING",
)

# (name, setup_code, op_code) — setup+op run INSIDE the try.
CASES = [
    ("construct", "d = AttributeDict(a=1, b={'c': [1, 2]})", None),
    ("copy", "d = AttributeDict(a=1)", "d.copy()"),
    ("repr", "d = AttributeDict(a=1, b=2)", "repr(d)"),
    ("pickle", "d = AttributeDict(a=1)", "__import__('pickle').dumps(d)"),
    (
        "nested",
        "d = AttributeDict({'db': {'host': 'x', 'ports': [1, {'a': 2}]}})",
        None,
    ),
]

# Max fail counts to sweep per case (well above the allocation-site counts,
# so the tail of each sweep observes NO_ERROR and stops cleanly).
N_MAX = 16
# n values that MUST raise MemoryError (allocation-site count per case,
# generous): every injected failure at or below this must fire.
MUST_FAIL_UP_TO = {
    "construct": 6,
    "copy": 2,
    "repr": 8,
    "pickle": 6,
    "nested": 6,
}


def _probe(setup: str, op: str, n: int) -> str:
    body = op if op else "d"
    return textwrap.dedent(
        f"""
        import sys
        import attributedict._attributedict as c
        from attributedict import AttributeDict
        c.set_allocation_fail_count({n})
        try:
            {setup}
            {body}
        except MemoryError:
            sys.stderr.write("MEMORY_ERROR\\n")
        else:
            sys.stderr.write("NO_ERROR\\n")
        """
    )


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
@pytest.mark.parametrize("n", range(N_MAX))
def test_failinject_raises_memoryerror(case, n):
    name, setup, op = case
    proc = subprocess.run(
        [sys.executable, "-c", _probe(setup, op, n)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # A segfault (rc<0) is a REAL bug in our NULL handling — fail loudly.
    assert proc.returncode == 0, (
        f"{name} n={n} crashed rc={proc.returncode}: {proc.stderr[-500:]}"
    )
    # At the low end the injected failure must have fired -> MemoryError.
    # At the high end the operation may fully succeed (NO_ERROR) once the
    # allocation-site count is exhausted — that is expected, not a failure.
    if n <= MUST_FAIL_UP_TO[name]:
        assert "MEMORY_ERROR" in proc.stderr, (
            f"{name} n={n} did not raise MemoryError: {proc.stderr[-500:]}"
        )
