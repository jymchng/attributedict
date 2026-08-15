"""I-002: tests for the reference pure-Python AttributeDict oracle.

These tests pin the *spec contract* (FR-001..FR-015, spec 08) against the
reference implementation. They are the cross-check oracle for the C
implementation (I-013 will run the same behavioral assertions against the
C type).
"""

from __future__ import annotations

import copy
import pickle

import pytest

from attributedict._reference import AttributeDict

# ---------------------------------------------------------------------------
# FR-001 — type/package identity (reference is importable, dict subclass)
# ---------------------------------------------------------------------------


def test_fr001_dict_subclass_and_import():
    assert issubclass(AttributeDict, dict)
    assert AttributeDict.__module__ == "attributedict._reference"


# ---------------------------------------------------------------------------
# FR-002 — construction forms
# ---------------------------------------------------------------------------


def test_fr002_empty():
    assert AttributeDict() == {}


def test_fr002_mapping():
    assert AttributeDict({"a": 1}) == {"a": 1}


def test_fr002_iterable_of_pairs():
    assert AttributeDict([("a", 1), ("b", 2)]) == {"a": 1, "b": 2}


def test_fr002_kwargs():
    assert AttributeDict(a=1, b=2) == {"a": 1, "b": 2}


def test_fr002_mapping_plus_kwargs():
    assert AttributeDict({"a": 1}, b=2) == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# FR-003 — attribute get
# ---------------------------------------------------------------------------


def test_fr003_attr_get_existing():
    d = AttributeDict(host="localhost")
    assert d.host == "localhost"


def test_fr003_attr_get_missing_raises_attribute_error():
    with pytest.raises(AttributeError):
        AttributeDict().missing  # noqa: B018


# ---------------------------------------------------------------------------
# FR-004 — attribute set
# ---------------------------------------------------------------------------


def test_fr004_attr_set_stores_key():
    d = AttributeDict()
    d.foo = 1
    assert d["foo"] == 1
    assert d.foo == 1


# ---------------------------------------------------------------------------
# FR-005 — attribute delete
# ---------------------------------------------------------------------------


def test_fr005_attr_delete_removes_key():
    d = AttributeDict(foo=1)
    del d.foo
    assert "foo" not in d


def test_fr005_attr_delete_missing_raises_attribute_error():
    d = AttributeDict()
    with pytest.raises(AttributeError):
        del d.missing  # noqa: B018


# ---------------------------------------------------------------------------
# FR-006 — keys win over methods
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["items", "keys", "values", "get", "update", "copy"])
def test_fr006_keys_win(name):
    d = AttributeDict({name: 42})
    assert getattr(d, name) == 42


def test_fr006_dict_items_still_reachable():
    d = AttributeDict({"items": 42})
    assert d.items == 42
    # The mapping view remains reachable through the base dict API.
    view = dict.items(d)
    assert isinstance(view, type({}.items()))
    assert dict(view) == {"items": 42}


def test_fr006_no_key_falls_back_to_method():
    d = AttributeDict(a=1)
    assert callable(d.items)
    assert callable(d.keys)
    assert callable(d.get)


# ---------------------------------------------------------------------------
# FR-007 — recursive nested conversion
# ---------------------------------------------------------------------------


def test_fr007_nested_conversion():
    d = AttributeDict({"db": {"host": "x", "ports": [1, {"a": 2}]}})
    assert isinstance(d.db, AttributeDict)
    assert d.db.host == "x"
    assert isinstance(d.db.ports, list)
    assert d.db.ports[1].a == 2


def test_fr007_sets_not_converted():
    d = AttributeDict({"s": {1, 2}})
    assert isinstance(d.s, set)


def test_fr007_cycle_safe():
    inner = {}
    outer = {"self": inner}
    inner["back"] = outer
    d = AttributeDict(outer)
    # No infinite recursion: the cycle resolves to AttributeDict instances.
    assert isinstance(d, AttributeDict)
    assert d.self.back is d


# ---------------------------------------------------------------------------
# FR-008 — mapping protocol
# ---------------------------------------------------------------------------


def test_fr008_mapping_protocol():
    d = AttributeDict(a=1)
    assert len(d) == 1
    assert list(iter(d)) == ["a"]
    assert d["a"] == 1
    d["b"] = 2
    assert d["b"] == 2
    del d["b"]
    assert "b" not in d
    assert "a" in d
    from collections.abc import MutableMapping

    assert isinstance(d, MutableMapping)
    assert isinstance(d, dict)


# ---------------------------------------------------------------------------
# FR-009 — dict methods; fromkeys returns AttributeDict
# ---------------------------------------------------------------------------


def test_fr009_dict_methods():
    d = AttributeDict(a=1)
    assert d.get("a") == 1
    assert d.setdefault("b", 2) == 2
    d.update({"c": 3})
    assert d == {"a": 1, "b": 2, "c": 3}
    assert d.pop("a") == 1
    k, v = d.popitem()
    assert k in ("b", "c")
    d.clear()
    assert d == {}


def test_fr009_copy_is_attribute_dict():
    d = AttributeDict(a=1)
    c = d.copy()
    assert isinstance(c, AttributeDict)
    assert c == {"a": 1}


def test_fr009_fromkeys_returns_attribute_dict():
    ad = AttributeDict.fromkeys(["a", "b"], 0)
    assert isinstance(ad, AttributeDict)
    assert ad == {"a": 0, "b": 0}


def test_fr009_views():
    d = AttributeDict(a=1)
    assert list(d.keys()) == ["a"]
    assert list(d.values()) == [1]
    assert list(d.items()) == [("a", 1)]


# ---------------------------------------------------------------------------
# FR-010 — repr/str
# ---------------------------------------------------------------------------


def test_fr010_repr():
    assert repr(AttributeDict({"a": 1})) == "AttributeDict({'a': 1})"


def test_fr010_repr_nested():
    d = AttributeDict({"a": {"b": 2}})
    assert repr(d) == "AttributeDict({'a': AttributeDict({'b': 2})})"


# ---------------------------------------------------------------------------
# FR-011 — equality
# ---------------------------------------------------------------------------


def test_fr011_equality_dict():
    assert AttributeDict(a=1) == {"a": 1}
    assert AttributeDict(a=1) != {"a": 2}


def test_fr011_equality_unrelated():
    assert (AttributeDict(a=1) == object()) is False


# ---------------------------------------------------------------------------
# FR-012 — unhashable
# ---------------------------------------------------------------------------


def test_fr012_unhashable():
    with pytest.raises(TypeError):
        hash(AttributeDict())


# ---------------------------------------------------------------------------
# FR-013 — copy/pickle, cycles
# ---------------------------------------------------------------------------


def test_fr013_shallow_copy():
    d = AttributeDict(a=1, nested={"x": 1})
    c = copy.copy(d)
    assert isinstance(c, AttributeDict)
    assert c == d


def test_fr013_deepcopy_nested_preserved():
    d = AttributeDict(a=AttributeDict(x=1))
    dc = copy.deepcopy(d)
    assert isinstance(dc.a, AttributeDict)
    assert dc.a.x == 1


def test_fr013_deepcopy_self_reference_terminates():
    d = AttributeDict()
    d.self_ref = d
    dc = copy.deepcopy(d)
    assert dc.self_ref is dc


def test_fr013_pickle_roundtrip():
    d = AttributeDict(a=1, nested=AttributeDict(x=2))
    data = pickle.dumps(d)
    loaded = pickle.loads(data)
    assert isinstance(loaded, AttributeDict)
    assert isinstance(loaded.nested, AttributeDict)
    assert loaded == d


# ---------------------------------------------------------------------------
# FR-014 — edge-case keys
# ---------------------------------------------------------------------------

EDGE_KEYS = [
    "normal",
    "with-space",
    "123",
    "_private",
    "__dunder__",
    "foo-bar",
    "",
]
NON_STR_KEYS = [1, None, object(), (1, 2)]


@pytest.mark.parametrize("key", EDGE_KEYS)
def test_fr014_edge_keys_mapping_access(key):
    d = AttributeDict({key: "v"})
    assert d[key] == "v"


@pytest.mark.parametrize("key", NON_STR_KEYS)
def test_fr014_non_str_keys_mapping_access(key):
    d = AttributeDict({key: "v"})
    assert d[key] == "v"


@pytest.mark.parametrize("key", ["with-space", "123", "foo-bar", ""])
def test_fr014_non_identifier_attr_access_raises(key):
    d = AttributeDict({key: "v"})
    with pytest.raises(AttributeError):
        getattr(d, key)


def test_fr014_identifier_keys_attr_access():
    d = AttributeDict({"normal": 1, "_private": 2, "__dunder__": 3})
    assert d.normal == 1
    assert d._private == 2
    assert d.__dunder__ == 3


# ---------------------------------------------------------------------------
# FR-015 — error semantics
# ---------------------------------------------------------------------------


def test_fr015_missing_key_keyerror():
    with pytest.raises(KeyError):
        AttributeDict()["missing"]


def test_fr015_unhashable_key_typeerror():
    with pytest.raises(TypeError):
        d = AttributeDict()
        d[[1, 2]] = "x"
