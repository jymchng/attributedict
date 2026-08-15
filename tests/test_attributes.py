"""I-008: attribute get/set/delete + keys-win resolution tests.

These test the C implementation (attributedict.AttributeDict) directly.
Semantics: FR-003..FR-006, FR-014 (see spec 03, 08).
"""

from __future__ import annotations

import pytest

from attributedict import AttributeDict

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


def test_fr004_attr_set_overwrites():
    d = AttributeDict(foo=1)
    d.foo = 2
    assert d["foo"] == 2


# ---------------------------------------------------------------------------
# FR-005 — attribute delete
# ---------------------------------------------------------------------------


def test_fr005_attr_delete_removes_key():
    d = AttributeDict(foo=1)
    del d.foo
    assert "foo" not in d


def test_fr005_attr_delete_missing_raises_attribute_error():
    with pytest.raises(AttributeError):
        del AttributeDict().missing


def test_fr005_attr_delete_vs_mapping_delete():
    # documented deviation: del d.missing -> AttributeError (not KeyError)
    d = AttributeDict()
    with pytest.raises(AttributeError):
        del d.missing
    with pytest.raises(KeyError):
        del d["missing"]


# ---------------------------------------------------------------------------
# FR-006 — real dict attributes win on the attribute path; mapping keeps keys
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["items", "keys", "values", "get", "update", "copy"])
def test_fr006_type_attribute_wins_on_attribute_path(name):
    d = AttributeDict({name: 42})
    # attribute access returns the real dict method (I-024)
    assert callable(getattr(d, name)), name
    # mapping access keeps the key's value
    assert d[name] == 42, name


def test_fr006_dict_items_method_and_key_value():
    d = AttributeDict({"items": 42})
    assert callable(d.items)
    assert list(d.items()) == [("items", 42)]
    assert d["items"] == 42
    view = dict.items(d)
    assert isinstance(view, type({}.items()))
    assert dict(view) == {"items": 42}


def test_fr006_non_type_key_still_reachable_as_attribute():
    d = AttributeDict(host="localhost")
    assert d.host == "localhost"


def test_fr006_dunder_and_underscore_keys():
    d = AttributeDict({"_private": 1, "__dunder__": 2})
    assert d._private == 1
    assert d.__dunder__ == 2


# ---------------------------------------------------------------------------
# FR-014 — edge-case keys
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["with-space", "123", "foo-bar", ""])
def test_fr014_non_identifier_attr_raises(key):
    d = AttributeDict({key: "v"})
    with pytest.raises(AttributeError):
        getattr(d, key)
    # mapping access still works
    assert d[key] == "v"


def test_fr014_non_str_keys_mapping_only():
    d = AttributeDict({1: "one", None: "none", (1, 2): "tuple"})
    assert d[1] == "one"
    assert d[None] == "none"
    assert d[(1, 2)] == "tuple"
    # not reachable via attribute syntax (no valid identifier)
    with pytest.raises(AttributeError):
        getattr(d, "1")


# ---------------------------------------------------------------------------
# MEM-004 — no stale exceptions after successful ops
# ---------------------------------------------------------------------------


def test_no_stale_exception_after_successful_attr_ops():
    d = AttributeDict()
    d.foo = 1  # set succeeds
    assert d.foo == 1  # get succeeds
    del d.foo  # delete succeeds
    assert d == {}  # dict still consistent
