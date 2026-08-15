"""I-013: C-extension behavior tests.

Verify the actual compiled type: module/name, dict-method inheritance,
isinstance, mapping-view reachability, cycle-safe conversion. See spec 10.
"""

from __future__ import annotations

import attributedict._attributedict as cmod
import pytest

from attributedict import AttributeDict


def test_type_module_and_name():
    assert AttributeDict.__module__ == "attributedict._attributedict"
    assert AttributeDict.__name__ == "AttributeDict"


def test_public_type_is_c_type():
    assert AttributeDict is cmod.AttributeDict


def test_bases_is_dict():
    assert AttributeDict.__bases__ == (dict,)


def test_isinstance_dict():
    d = AttributeDict(a=1)
    assert isinstance(d, dict)
    assert type(d) is AttributeDict


def test_dict_method_inheritance():
    for meth in (
        "get",
        "setdefault",
        "update",
        "pop",
        "popitem",
        "clear",
        "keys",
        "items",
        "values",
        "fromkeys",
    ):
        assert callable(getattr(AttributeDict, meth)), meth


def test_dict_items_reachable_when_key_shadows():
    d = AttributeDict(items=42)
    assert d.items == 42
    view = dict.items(d)
    assert isinstance(view, type({}.items()))
    assert dict(view) == {"items": 42}


def test_dict_get_reachable_when_key_shadows():
    d = AttributeDict(get="shadowed")
    assert d.get == "shadowed"
    assert dict.get(d, "missing", "default") == "default"


def test_cycle_safe_conversion():
    inner = {}
    outer = {"self": inner}
    inner["back"] = outer
    d = AttributeDict(outer)
    assert type(d) is AttributeDict
    assert d.self.back is d


def test_weakref_matches_dict():
    import weakref

    # dict does not support weakrefs; AttributeDict matches
    with pytest.raises(TypeError):
        weakref.ref(AttributeDict())


def test_subclassing_supported():
    class MyAD(AttributeDict):
        pass

    d = MyAD(a=1)
    assert type(d) is MyAD
    assert isinstance(d, dict)
    assert d.a == 1
