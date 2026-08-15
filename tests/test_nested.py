"""I-006: construction forms + recursive nested conversion tests (C impl).

Covers FR-002 (all dict construction forms) and FR-007 (recursive,
cycle-safe nested conversion). See spec 03, 06, 08.
"""

from __future__ import annotations

from collections import OrderedDict

import pytest

from attributedict import AttributeDict


# ---------------------------------------------------------------------------
# FR-002 — construction forms
# ---------------------------------------------------------------------------


def test_empty():
    assert AttributeDict() == {}


def test_mapping():
    assert AttributeDict({"a": 1}) == {"a": 1}


def test_iterable_of_pairs():
    assert AttributeDict([("a", 1), ("b", 2)]) == {"a": 1, "b": 2}


def test_kwargs():
    assert AttributeDict(a=1, b=2) == {"a": 1, "b": 2}


def test_mapping_plus_kwargs():
    assert AttributeDict({"a": 1}, b=2) == {"a": 1, "b": 2}


def test_from_ordered_dict():
    od = OrderedDict([("a", 1), ("b", 2)])
    d = AttributeDict(od)
    assert d == {"a": 1, "b": 2}
    assert isinstance(d, AttributeDict)


# ---------------------------------------------------------------------------
# FR-007 — recursive nested conversion
# ---------------------------------------------------------------------------


def test_nested_dict():
    d = AttributeDict({"db": {"host": "x"}})
    assert isinstance(d.db, AttributeDict)
    assert d.db.host == "x"


def test_nested_dict_in_list():
    d = AttributeDict({"servers": [{"host": "a"}, {"host": "b"}]})
    assert isinstance(d.servers, list)
    assert isinstance(d.servers[0], AttributeDict)
    assert d.servers[0].host == "a"
    assert d.servers[1].host == "b"


def test_nested_dict_in_tuple():
    d = AttributeDict({"t": (1, {"a": 2})})
    assert isinstance(d.t, tuple)
    assert isinstance(d.t[1], AttributeDict)
    assert d.t[1].a == 2


def test_deeply_nested():
    d = AttributeDict({"db": {"host": "x", "ports": [1, {"a": 2}]}})
    assert d.db.host == "x"
    assert d.db.ports[1].a == 2


def test_sets_not_converted():
    d = AttributeDict({"s": {1, 2}})
    assert isinstance(d.s, set)


def test_frozenset_not_converted():
    d = AttributeDict({"fs": frozenset({1})})
    assert isinstance(d.fs, frozenset)


def test_non_container_untouched():
    obj = object()
    d = AttributeDict({"o": obj, "i": 5, "s": "str"})
    assert d.o is obj
    assert d.i == 5
    assert d.s == "str"


# ---------------------------------------------------------------------------
# FR-007 — cycle safety
# ---------------------------------------------------------------------------


def test_self_referential_dict_terminates():
    inner = {}
    outer = {"self": inner}
    inner["back"] = outer
    d = AttributeDict(outer)
    assert isinstance(d, AttributeDict)
    assert d.self.back is d


def test_cycle_preserves_identity():
    d = AttributeDict()
    d.self_ref = d
    # constructing from an existing AttributeDict shares it (idempotent)
    d2 = AttributeDict({"x": d})
    assert d2.x is d


def test_idempotent_existing_attribute_dict_shared():
    nested = AttributeDict(x=1)
    d = AttributeDict(nested=nested)
    assert d.nested is nested
