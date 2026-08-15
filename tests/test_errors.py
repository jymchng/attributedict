"""I-011: error semantics + edge-case key tests (C impl).

Covers FR-014 (edge-case keys) and FR-015 (exception types + message
stability; no stale exceptions). See spec 03, 08.
"""

from __future__ import annotations

import pytest

from attributedict import AttributeDict

TYPE_NAME = "attributedict._attributedict.AttributeDict"


# ---------------------------------------------------------------------------
# FR-015 — exception types
# ---------------------------------------------------------------------------


def test_missing_key_keyerror():
    with pytest.raises(KeyError):
        AttributeDict()["missing"]


def test_missing_attr_attributeerror():
    with pytest.raises(AttributeError):
        AttributeDict().missing  # noqa: B018


def test_del_missing_attr_attributeerror():
    d = AttributeDict()
    with pytest.raises(AttributeError):
        del d.missing  # noqa: B018


def test_del_missing_key_keyerror():
    d = AttributeDict()
    with pytest.raises(KeyError):
        del d["missing"]


def test_unhashable_key_setitem_typeerror():
    d = AttributeDict()
    with pytest.raises(TypeError):
        d[[1, 2]] = "x"


def test_unhashable_key_getitem_typeerror():
    with pytest.raises(TypeError):
        AttributeDict()[[1, 2]]


def test_hash_typeerror():
    with pytest.raises(TypeError):
        hash(AttributeDict())


# ---------------------------------------------------------------------------
# FR-015 — message stability
# ---------------------------------------------------------------------------


def test_missing_key_message():
    with pytest.raises(KeyError) as ei:
        AttributeDict()["missing"]
    assert "'missing'" in str(ei.value)


def test_missing_attr_message():
    with pytest.raises(AttributeError) as ei:
        AttributeDict().missing  # noqa: B018
    msg = str(ei.value)
    assert "has no attribute 'missing'" in msg
    assert TYPE_NAME in msg


def test_del_missing_attr_message():
    d = AttributeDict()
    with pytest.raises(AttributeError) as ei:
        del d.missing  # noqa: B018
    msg = str(ei.value)
    assert "has no attribute 'missing'" in msg


# ---------------------------------------------------------------------------
# FR-014 — edge-case key matrix (attribute vs mapping access)
# ---------------------------------------------------------------------------

IDENTIFIER_KEYS = ["normal", "_private", "__dunder__", "items", "keys", "get"]
NON_IDENTIFIER_KEYS = ["with-space", "123", "foo-bar", ""]


@pytest.mark.parametrize("key", IDENTIFIER_KEYS)
def test_identifier_keys_attribute_access(key):
    d = AttributeDict({key: "v"})
    assert getattr(d, key) == "v"
    assert d[key] == "v"


@pytest.mark.parametrize("key", NON_IDENTIFIER_KEYS)
def test_non_identifier_keys_mapping_only(key):
    d = AttributeDict({key: "v"})
    assert d[key] == "v"
    with pytest.raises(AttributeError):
        getattr(d, key)


@pytest.mark.parametrize("key", [1, None, (1, 2)])
def test_non_str_keys_mapping_only(key):
    d = AttributeDict({key: "v"})
    assert d[key] == "v"
    with pytest.raises(AttributeError):
        getattr(d, str(key))


# ---------------------------------------------------------------------------
# MEM-004 — no stale exceptions after successful operations
# ---------------------------------------------------------------------------


def test_no_stale_exception_after_attr_ops():
    d = AttributeDict()
    # cause a failure
    with pytest.raises(AttributeError):
        del d.missing  # noqa: B018
    # subsequent ops succeed and see a clean interpreter state
    d.foo = 1
    assert d.foo == 1
    del d.foo
    assert d == {}
    assert "foo" not in d


def test_no_stale_exception_after_keyerror():
    d = AttributeDict(a=1)
    with pytest.raises(KeyError):
        d["missing"]
    # dict still fully usable
    assert d["a"] == 1
    d["b"] = 2
    assert len(d) == 2
