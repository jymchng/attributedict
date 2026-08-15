"""I-007: mapping protocol + dict-method compatibility tests (C impl).

Covers FR-008 (mapping protocol, MutableMapping, isinstance dict) and
FR-009 (inherited dict methods, copy/fromkeys return AttributeDict).
See spec 03, 05, 08.
"""

from __future__ import annotations

from collections.abc import MutableMapping

import pytest

from attributedict import AttributeDict


# ---------------------------------------------------------------------------
# FR-008 — mapping protocol
# ---------------------------------------------------------------------------


def test_len_iter_contains():
    d = AttributeDict(a=1, b=2)
    assert len(d) == 2
    assert set(iter(d)) == {"a", "b"}
    assert "a" in d and "c" not in d


def test_getitem_setitem_delitem():
    d = AttributeDict()
    d["x"] = 1
    assert d["x"] == 1
    del d["x"]
    assert "x" not in d


def test_isinstance_dict_and_mutablemapping():
    d = AttributeDict(a=1)
    assert isinstance(d, dict)
    assert isinstance(d, MutableMapping)


# ---------------------------------------------------------------------------
# FR-009 — inherited dict methods
# ---------------------------------------------------------------------------


def test_get():
    d = AttributeDict(a=1)
    assert d.get("a") == 1
    assert d.get("missing") is None
    assert d.get("missing", "default") == "default"


def test_setdefault():
    d = AttributeDict()
    assert d.setdefault("k", 5) == 5
    assert d["k"] == 5
    assert d.setdefault("k", 99) == 5  # existing not overwritten


def test_update():
    d = AttributeDict(a=1)
    d.update({"b": 2})
    d.update(c=3)
    assert d == {"a": 1, "b": 2, "c": 3}


def test_pop():
    d = AttributeDict(a=1)
    assert d.pop("a") == 1
    assert "a" not in d
    assert d.pop("missing", "d") == "d"
    with pytest.raises(KeyError):
        d.pop("missing")


def test_popitem():
    d = AttributeDict(a=1, b=2)
    k, v = d.popitem()
    assert k in ("a", "b") and v in (1, 2)


def test_clear():
    d = AttributeDict(a=1)
    d.clear()
    assert d == {}


def test_copy_returns_attribute_dict():
    d = AttributeDict(a=1, nested={"x": 1})
    c = d.copy()
    assert isinstance(c, AttributeDict)
    assert c == d
    assert c.nested is d.nested  # shallow


def test_copy_module_level():
    import copy as _copy

    d = AttributeDict(a=1)
    c = _copy.copy(d)
    assert isinstance(c, AttributeDict)


def test_fromkeys_returns_attribute_dict():
    fk = AttributeDict.fromkeys(["a", "b"], 0)
    assert isinstance(fk, AttributeDict)
    assert fk == {"a": 0, "b": 0}


def test_views():
    d = AttributeDict(a=1, b=2)
    assert isinstance(d.keys(), type({}.keys()))
    assert isinstance(d.items(), type({}.items()))
    assert isinstance(d.values(), type({}.values()))
    assert set(d.keys()) == {"a", "b"}
    assert set(d.items()) == {("a", 1), ("b", 2)}
    assert set(d.values()) == {1, 2}


def test_dict_items_reachable_when_key_shadows():
    d = AttributeDict(items=42)
    assert d.items == 42
    view = dict.items(d)
    assert dict(view) == {"items": 42}
