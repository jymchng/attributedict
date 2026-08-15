"""Pickle support for the C AttributeDict (I-010).

Provides the ``reconstruct`` helper referenced by ``AttributeDict.__reduce__``
so pickling works across ALL protocols (0-5) while preserving the type and
reference cycles.

``__reduce__`` returns the 5-tuple form
``(reconstruct, (cls,), None, None, iter(self.items()))``. Pickle:

1. calls ``reconstruct(cls)`` to create the (empty) AttributeDict,
2. then applies the dictitems iterator via ``obj.update(items)``
   (the inherited dict method), which pickle's memo makes cycle-safe.

This module is an implementation detail; it is not part of the public API.
"""

from __future__ import annotations

from typing import Any, Type, TypeVar

AD = TypeVar("AD", bound="Any")


def reconstruct(cls: Type[AD]) -> AD:
    """Create an empty AttributeDict of type *cls* (fill happens via pickle's
    dictitems update, which is cycle-safe through the memo)."""
    return cls.__new__(cls)
