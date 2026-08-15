"""Reference pure-Python implementation of AttributeDict (I-002).

This module is the *spec oracle* for the C implementation. It mirrors
spec 03 (FR-001..FR-015) and 08 (API specification) exactly and is used:

- as the cross-check baseline in the test suite (I-013), and
- as the pure-Python comparison baseline in the benchmarks (I-014).

It is NOT the public import path: ``attributedict.AttributeDict`` is the
C implementation (or the bootstrap stub before I-005). Users should not
import from this module.

Semantics implemented (per spec):
- dict subclass; all dict construction forms (FR-002).
- attribute get/set/delete mirror mapping access (FR-003..005).
- keys win over type attributes/methods (FR-006, D-004).
- recursive, cycle-safe nested conversion at construction (FR-007).
- repr ``AttributeDict({...})``; dict equality; unhashable (FR-010..012).
- copy/pickle supported; nested AttributeDict preserved; cycles work (FR-013).
- edge-case keys and error semantics (FR-014/015).

Implementation notes for the C port:
- Attribute lookups MUST use the key-first resolution order (FR-006).
- ALL internal iteration uses ``dict`` base methods so that keys named
  ``items``/``keys``/``values``/``get``/... cannot intercept internals.
- Nested conversion is idempotent: already-converted AttributeDicts are
  left untouched (needed for shallow-copy semantics of ``copy()``).
"""

from __future__ import annotations

import copy as _copy
from typing import Any, Dict, Iterable, Tuple, Type, TypeVar

__all__ = ["AttributeDict"]

AD = TypeVar("AD", bound="AttributeDict")


# ---------------------------------------------------------------------------
# Nested conversion (FR-007): recursive, cycle-safe, idempotent.
# ---------------------------------------------------------------------------


class _Converting:
    """Tracks in-progress conversions so cycles reuse one object."""

    __slots__ = ("_seen",)

    def __init__(self) -> None:
        self._seen: Dict[int, Any] = {}

    def get(self, obj: Any) -> Any:
        return self._seen.get(id(obj))

    def put(self, obj: Any, converted: Any) -> None:
        self._seen[id(obj)] = converted


def convert_value(value: Any, ctx: _Converting) -> Any:
    """Recursively convert *value* per FR-007.

    - dict (but NOT an already-converted AttributeDict) -> AttributeDict
    - lists/tuples -> same container type with converted elements
    - sets/frozensets -> NOT converted (A-008)
    - anything else -> unchanged
    """
    if isinstance(value, AttributeDict):
        # Already converted: share it (idempotent; shallow-copy semantics).
        return value
    if isinstance(value, dict):
        existing = ctx.get(value)
        if existing is not None:
            return existing
        converted = AttributeDict.__new__(AttributeDict)
        ctx.put(value, converted)
        # Fill via dict base so nested keys named e.g. "update" cannot
        # interfere; conversion of values is recursive and cycle-safe.
        for k, v in dict.items(value):
            dict.__setitem__(converted, k, convert_value(v, ctx))
        return converted
    if isinstance(value, list):
        return [convert_value(item, ctx) for item in value]
    if isinstance(value, tuple):
        return tuple(convert_value(item, ctx) for item in value)
    return value


# ---------------------------------------------------------------------------
# The type
# ---------------------------------------------------------------------------


class AttributeDict(dict):
    """A ``dict`` subclass whose keys are also accessible as attributes.

    ``d["host"] == d.host`` when the key is a valid identifier and does not
    collide with a real type attribute (see FR-006 "keys win": keys win).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Exact dict construction semantics (FR-002), then convert in place.
        super().__init__(*args, **kwargs)
        ctx = _Converting()
        if args and isinstance(args[0], dict):
            # The top-level source maps to *self*, so self-references inside
            # the source resolve to the object being constructed.
            ctx.put(args[0], self)
        for k in list(dict.keys(self)):
            v = dict.__getitem__(self, k)
            dict.__setitem__(self, k, convert_value(v, ctx))

    # -- attribute get (FR-003 / FR-006: keys win) -------------------------
    def __getattribute__(self, name: str) -> Any:
        # Keys win: any present key that is a usable attribute name shadows
        # type attributes/methods (FR-006). Non-identifier keys are NOT
        # reachable via attribute syntax (FR-014).
        if isinstance(name, str) and name.isidentifier():
            try:
                return dict.__getitem__(self, name)
            except KeyError:
                pass
        return object.__getattribute__(self, name)

    # -- attribute set (FR-004) -------------------------------------------
    def __setattr__(self, name: str, value: Any) -> None:
        # Always mapping assignment (D-005 / spec 05).
        dict.__setitem__(self, name, value)

    # -- attribute delete (FR-005) ----------------------------------------
    def __delattr__(self, name: str) -> None:
        if name in self:
            del self[name]
            return
        raise AttributeError(
            f"{type(self).__name__!r} object has no attribute {name!r}"
        )

    # -- repr (FR-010) -----------------------------------------------------
    def __repr__(self) -> str:
        inner = ", ".join(f"{k!r}: {v!r}" for k, v in dict.items(self))
        return f"{type(self).__name__}({{{inner}}})"

    # -- copy (FR-009/013) -------------------------------------------------
    def copy(self: AD) -> AD:
        """Return a shallow copy as an AttributeDict."""
        return type(self)(self)

    __copy__ = copy

    def __deepcopy__(self, memo: Dict[int, Any]) -> "AttributeDict":
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        cls = type(self)
        new = cls.__new__(cls)
        memo[id(self)] = new
        for k, v in dict.items(self):
            dict.__setitem__(new, _copy.deepcopy(k, memo),
                             _copy.deepcopy(v, memo))
        return new

    # -- pickle (FR-013) ---------------------------------------------------
    def __reduce__(self):
        return (_reconstruct, (type(self), dict(self)))

    # -- classmethod fromkeys (FR-009) --------------------------------------
    @classmethod
    def fromkeys(cls: Type[AD], iterable: Iterable[Any], value: Any = None) -> AD:
        return cls(dict.fromkeys(iterable, value))


def _reconstruct(cls: Type[AD], data: Dict[Any, Any]) -> AD:
    """Pickle helper: rebuild an AttributeDict from a plain dict.

    Nested AttributeDicts inside *data* are already AttributeDict instances
    (they pickled as such); construction leaves them untouched and converts
    any plain dicts per FR-007.
    """
    return cls(data)


# Reference type used by tests/benchmarks as the oracle.
ReferenceAttributeDict = AttributeDict
