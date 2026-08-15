"""I-010: copy and pickle support tests (C impl).

Covers FR-013: copy.copy, copy.deepcopy, pickle round-trips incl. cycles.
See spec 03, 08.
"""

from __future__ import annotations

import copy
import pickle

import pytest

from attributedict import AttributeDict

# ---------------------------------------------------------------------------
# copy.copy (shallow)
# ---------------------------------------------------------------------------


def test_copy_copy_preserves_type():
    d = AttributeDict(a=1)
    c = copy.copy(d)
    assert type(c) is AttributeDict
    assert c == d


def test_copy_copy_shallow_shares_nested():
    d = AttributeDict(nested=AttributeDict(x=1))
    c = copy.copy(d)
    assert c.nested is d.nested


# ---------------------------------------------------------------------------
# copy.deepcopy
# ---------------------------------------------------------------------------


def test_deepcopy_preserves_type_and_nested():
    d = AttributeDict(a=1, nested=AttributeDict(x=1))
    dc = copy.deepcopy(d)
    assert type(dc) is AttributeDict
    assert type(dc.nested) is AttributeDict
    assert dc.nested is not d.nested
    assert dc.nested == d.nested


def test_deepcopy_nested_list_of_dicts():
    d = AttributeDict(servers=[{"host": "a"}])
    dc = copy.deepcopy(d)
    assert type(dc.servers[0]) is AttributeDict
    assert dc.servers[0].host == "a"


def test_deepcopy_self_reference_terminates_and_preserves():
    r = AttributeDict()
    r.self_ref = r
    dc = copy.deepcopy(r)
    assert dc.self_ref is dc


# ---------------------------------------------------------------------------
# pickle round-trips
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("protocol", [0, 1, 2, 3, 4, 5])
def test_pickle_all_protocols(protocol):
    d = AttributeDict(a=1, nested=AttributeDict(x=[1, {"y": 2}]))
    loaded = pickle.loads(pickle.dumps(d, protocol=protocol))
    assert type(loaded) is AttributeDict
    assert type(loaded.nested) is AttributeDict
    assert loaded == d


@pytest.mark.parametrize("protocol", [0, 1, 2, 4, 5])
def test_pickle_cycle(protocol):
    r = AttributeDict()
    r.self_ref = r
    loaded = pickle.loads(pickle.dumps(r, protocol=protocol))
    assert type(loaded) is AttributeDict
    assert loaded.self_ref is loaded


def test_pickle_mutual_cycle():
    a = AttributeDict()
    b = AttributeDict()
    a.b = b
    b.a = a
    loaded = pickle.loads(pickle.dumps(a))
    assert loaded.b.a is loaded


def test_pickle_method_named_keys():
    d = AttributeDict(items=42, keys="k")
    loaded = pickle.loads(pickle.dumps(d))
    assert loaded.items == 42
    assert loaded.keys == "k"
