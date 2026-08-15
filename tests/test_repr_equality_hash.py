"""I-009: repr, equality, and hash tests (C impl).

Covers FR-010 (repr), FR-011 (equality), FR-012 (unhashable).
See spec 03, 08.
"""

from __future__ import annotations

import pytest

from attributedict import AttributeDict

# ---------------------------------------------------------------------------
# FR-010 — repr / str
# ---------------------------------------------------------------------------


def test_repr_flat():
    assert repr(AttributeDict({"a": 1})) == "AttributeDict({'a': 1})"


def test_repr_empty():
    assert repr(AttributeDict()) == "AttributeDict({})"


def test_repr_nested():
    d = AttributeDict({"a": {"b": 2}})
    assert repr(d) == "AttributeDict({'a': AttributeDict({'b': 2})})"


def test_repr_multi_item_order():
    d = AttributeDict(a=1, b=2)
    assert repr(d) == "AttributeDict({'a': 1, 'b': 2})"


def test_repr_recursive():
    r = AttributeDict()
    r.self_ref = r
    s = repr(r)
    assert s.startswith("AttributeDict({'self_ref': AttributeDict({...})})")


def test_str_delegates_to_repr():
    d = AttributeDict(a=1)
    assert str(d) == repr(d)


# ---------------------------------------------------------------------------
# FR-011 — equality
# ---------------------------------------------------------------------------


def test_eq_dict():
    assert AttributeDict(a=1) == {"a": 1}


def test_eq_other_attribute_dict():
    assert AttributeDict(a=1) == AttributeDict(a=1)


def test_neq_dict():
    assert AttributeDict(a=1) != {"a": 2}


def test_eq_unrelated_object():
    assert (AttributeDict(a=1) == object()) is False


def test_eq_nested():
    assert AttributeDict({"a": {"b": 1}}) == {"a": {"b": 1}}


# ---------------------------------------------------------------------------
# FR-012 — unhashable
# ---------------------------------------------------------------------------


def test_unhashable():
    with pytest.raises(TypeError):
        hash(AttributeDict())


def test_unhashable_nonempty():
    with pytest.raises(TypeError):
        hash(AttributeDict(a=1))
