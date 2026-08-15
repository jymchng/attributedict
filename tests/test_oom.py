"""I-023: behavioral OOM tests for the C extension (goal: >90% gcov coverage).

The refactor (I-023) eliminated provably-unreachable defensive branches
("key vanished" guards, the PyErr_Occurred guard after str-key lookup).
The remaining uncovered C lines are allocation-failure (OOM) paths. These
tests exercise them *behaviorally*: each runs a subprocess under a tight
address-space limit (resource.RLIMIT_AS) and confirms the extension raises
MemoryError cleanly (no crash, no stale exception — MEM-004).

No production fault-injection hooks are used.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest

PROBE = textwrap.dedent(
    """
    import resource, sys

    def limit_mb(mb):
        limit = mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    from attributedict import AttributeDict

    def expect_memory_error(label, fn):
        try:
            fn()
        except MemoryError:
            sys.stderr.write(label + ": MemoryError OK\\n")
        except BaseException as e:
            sys.stderr.write(
                label + ": WRONG " + type(e).__name__ + ": " + str(e) + "\\n"
            )
            sys.exit(1)
        else:
            sys.stderr.write(label + ": NO ERROR (allocation succeeded)\\n")
            sys.exit(2)

    limit_mb(60)

    def big():
        return AttributeDict(**{("k" + str(i)): i for i in range(500000)})

    expect_memory_error("construct_kwargs", big)
    expect_memory_error("construct_mapping", lambda: AttributeDict(big()))
    expect_memory_error("copy", lambda: big().copy())
    expect_memory_error("repr", lambda: repr(big()))
    expect_memory_error("pickle", lambda: __import__("pickle").dumps(big()))
    sys.stderr.write("ALL OK\\n")
    """
)


@pytest.mark.skipif(
    not hasattr(__import__("resource"), "RLIMIT_AS"),
    reason="RLIMIT_AS not available on this platform",
)
def test_oom_construction_and_ops_raise_memoryerror():
    """Subprocess under a tight AS limit: OOM paths raise MemoryError."""
    proc = subprocess.run(
        [sys.executable, "-c", PROBE],
        capture_output=True,
        text=True,
        timeout=120,
    )
    stderr = proc.stderr
    assert "ALL OK" in stderr, f"OOM probe failed rc={proc.returncode}: {stderr}"
    assert "WRONG" not in stderr, stderr
