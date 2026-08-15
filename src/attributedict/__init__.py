"""attributedict: dict semantics with attribute access.

Public API::

    from attributedict import AttributeDict

The performance-critical implementation lives in the C extension module
``attributedict._attributedict``. This module is a thin public wrapper.
"""

__all__ = ["AttributeDict"]
__version__ = "0.1.0"

try:
    # Real C implementation (registered in I-005).
    from ._attributedict import AttributeDict
except ImportError:
    # I-001 bootstrap stub: keeps the package importable until the C type is
    # registered. This stub carries NO behavior beyond being a dict subclass.
    class AttributeDict(dict):  # type: ignore[no-redef]
        """Bootstrap stub. Replaced by the C implementation in I-005."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    AttributeDict.__module__ = __name__  # type: ignore[attr-defined]
