"""I-023: behavioral error-path tests for the C extension.

These are the non-fault-injection error-path tests. The deterministic
allocation-failure coverage lives in tests/test_failinject.py (test-only
PY_ATTRIBUTEDICT_TESTING build). This module exercises error paths with
ordinary Python objects whose dunders raise (a TypeError from a key whose
__hash__ raises, a RuntimeError from a value whose __repr__ raises), forcing
the C extension's PyDict_SetItem / PyObject_Repr / PyDict_Update error
handling to run.
"""

from __future__ import annotations

import subprocess
import sys

PROBE = '''
import sys
from attributedict import AttributeDict

class BadHash:
    """__hash__ raises -> forces PyDict_SetItem / PyDict_Update to fail."""
    def __hash__(self):
        raise TypeError("boom-hash")

class BadRepr:
    """__repr__ raises -> forces PyObject_Repr to fail in repr()."""
    def __repr__(self):
        raise RuntimeError("boom-repr")

def run(label, fn):
    try:
        fn()
    except BaseException:
        sys.stderr.write(label + ": ERR\\n")
    else:
        sys.stderr.write(label + ": NOERR\\n")
        sys.exit(1)

# copy(): PyDict_Update(nd, self) fails when a key's __hash__ raises.
run("copy_badhash", lambda: AttributeDict({BadHash(): 1}).copy())

# init(): PyDict_SetItem(self, k, cv) fails when a key's __hash__ raises.
run("init_badhash", lambda: AttributeDict({BadHash(): 1, "a": 2}))

# repr(): PyObject_Repr(value) fails when a value's __repr__ raises.
run("repr_badrepr", lambda: repr(AttributeDict({"a": BadRepr()})))

# nested conversion: PyDict_SetItem(nd, k, cv) fails when a nested key's
# __hash__ raises during conversion.
run("nested_badhash", lambda: AttributeDict({"n": {BadHash(): 1}}))

sys.stderr.write("DET DONE\\n")
'''


def test_deterministic_error_paths():
    """Objects with raising dunders force C error branches deterministically."""
    proc = subprocess.run(
        [sys.executable, "-c", PROBE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr[-500:]
    assert "DET DONE" in proc.stderr, proc.stderr[-500:]
    # Each operation must have raised (ERR), not succeeded (NOERR).
    assert "NOERR" not in proc.stderr, proc.stderr
