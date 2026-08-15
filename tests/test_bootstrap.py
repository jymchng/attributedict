"""I-001 bootstrap smoke tests.

These tests validate only that the package skeleton imports and is a dict
subclass; the real behavioral suite lands in I-013.
"""

import attributedict


def test_public_all():
    assert attributedict.__all__ == ["AttributeDict"]


def test_attribute_dict_is_dict_subclass():
    assert issubclass(attributedict.AttributeDict, dict)


def test_stub_constructs_from_kwargs():
    d = attributedict.AttributeDict(host="localhost", port=8080)
    assert d["host"] == "localhost"
    assert d["port"] == 8080


def test_c_extension_module_importable():
    import attributedict._attributedict as cmod

    assert cmod.__name__ == "attributedict._attributedict"
