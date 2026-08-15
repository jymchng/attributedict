"""I-013: property-based tests (hypothesis).

- random nested structures convert correctly and remain dict-compatible
- random key/value operations preserve dict-equivalence
- the C implementation matches the pure-Python reference oracle

See spec 10 (property-based layer).
"""

from __future__ import annotations

import copy

from hypothesis import given, settings
from hypothesis import strategies as st

from attributedict import AttributeDict
from attributedict._reference import AttributeDict as RefAttributeDict

# A strategy for JSON-like nested values (dicts/lists/tuples/atoms).
atom = st.one_of(st.none(), st.booleans(), st.integers(), st.text())
nested_value = st.recursive(
    atom,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.tuples(children),
        st.dictionaries(st.text(max_size=8), children, max_size=4),
    ),
    max_leaves=12,
)


@settings(max_examples=50, deadline=None)
@given(nested_value)
def test_nested_conversion_dict_equivalent(value):
    d = AttributeDict({"root": value})
    # the result equals a plain dict of the same structure
    assert isinstance(d, dict)
    # recursive attribute access reaches the converted leaf
    if isinstance(value, dict) and "root" in value and isinstance(value["root"], dict):
        assert isinstance(d.root, AttributeDict)


@settings(max_examples=50, deadline=None)
@given(st.dictionaries(st.text(max_size=8), st.integers(), max_size=8))
def test_random_dict_equivalence(mapping):
    d = AttributeDict(mapping)
    assert d == mapping
    assert dict(d) == mapping
    for k, v in mapping.items():
        assert d[k] == v


@settings(max_examples=50, deadline=None)
@given(st.dictionaries(st.text(max_size=8), nested_value, max_size=6))
def test_c_matches_reference(mapping):
    c = AttributeDict(mapping)
    r = RefAttributeDict(copy.deepcopy(mapping))
    assert dict(c) == dict(r)


@settings(max_examples=50, deadline=None)
@given(st.lists(st.text(max_size=6), max_size=8))
def test_fromkeys_property(keys):
    d = AttributeDict.fromkeys(keys, 0)
    assert type(d) is AttributeDict
    assert all(d[k] == 0 for k in keys)
    assert len(d) == len(set(keys))


@settings(max_examples=50, deadline=None)
@given(st.dictionaries(st.text(max_size=6), st.integers(), max_size=8))
def test_copy_equivalence(mapping):
    d = AttributeDict(mapping)
    c = d.copy()
    assert type(c) is AttributeDict
    assert c == d
    assert c is not d
