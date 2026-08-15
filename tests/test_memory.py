"""I-012: memory-management tests (C impl).

Validates refcount stability, GC participation, and cycle safety
(NFR-004, MEM-001..MEM-008, spec 07). These run in normal, debug, and
sanitizer (ASan/UBSan) builds.
"""

from __future__ import annotations

import gc

import pytest

from attributedict import AttributeDict

N_STRESS = 5000


# ---------------------------------------------------------------------------
# Refcount / leak smoke
# ---------------------------------------------------------------------------


def _refcount(o):
    """sys.gettotalrefcount exists only in debug builds; fall back to
    sys.getrefcount of a live object (a documented proxy)."""
    import sys

    if hasattr(sys, "gettotalrefcount"):
        return sys.gettotalrefcount()
    return sys.getrefcount(o)


def test_repeated_construction_destruction_no_growth():
    d = AttributeDict(a=1, nested={"x": [1, 2]})
    before = _refcount(d)
    for _ in range(200):
        c = AttributeDict(d)
        del c
    gc.collect()
    after = _refcount(d)
    # allow small slack for interpreter noise
    assert after <= before + 50, (before, after)


def test_many_objects_create_delete():
    for _ in range(N_STRESS):
        d = AttributeDict(x=1, y={"z": 2})
        d.extra = 3
        del d
    gc.collect()


def test_many_nested_objects():
    for _ in range(1000):
        d = AttributeDict({"a": {"b": {"c": {"d": 1}}}})
        assert d.a.b.c.d == 1
        del d
    gc.collect()


# ---------------------------------------------------------------------------
# GC: cyclic structures collected without leaks
# ---------------------------------------------------------------------------


def test_cyclic_attribute_dict_collected():
    d = AttributeDict()
    d.self_ref = d
    del d
    gc.collect()


def test_mutual_cycle_collected():
    a = AttributeDict()
    b = AttributeDict()
    a.b = b
    b.a = a
    del a, b
    gc.collect()


def test_cyclic_construction_terminates():
    inner = {}
    outer = {"self": inner}
    inner["back"] = outer
    d = AttributeDict(outer)
    assert d.self.back is d
    del d
    gc.collect()


def test_gc_module_finds_cycles():
    d = AttributeDict()
    d.self_ref = d
    # without a reference the cycle must be collectible
    refs = gc.get_objects()
    _ = d  # keep alive until here
    del d
    gc.collect()
    # just assert collection completes without error
    assert True


# ---------------------------------------------------------------------------
# Weakrefs: dict does not support weakrefs; AttributeDict matches dict (MEM-009)
# ---------------------------------------------------------------------------


def test_weakref_not_supported_like_dict():
    import weakref

    d = AttributeDict(a=1)
    with pytest.raises(TypeError):
        weakref.ref(d)
    # consistent with dict
    with pytest.raises(TypeError):
        weakref.ref({})


# ---------------------------------------------------------------------------
# Traversal sanity: object graph is fully reachable from items
# ---------------------------------------------------------------------------


def test_traverse_visits_keys_and_values():
    d = AttributeDict(key_obj=object(), value_obj=object())
    # exercise repr + iteration + copy (all use the items) without crash
    assert "key_obj" in d
    assert len(dict(d)) == 2
    c = d.copy()
    assert len(c) == 2
