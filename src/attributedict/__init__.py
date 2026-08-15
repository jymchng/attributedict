"""attributedict: dict semantics with attribute access.

Public API::

    from attributedict import AttributeDict

The performance-critical implementation lives in the C extension module
``attributedict._attributedict``. This module is a thin public wrapper.
"""

from ._attributedict import AttributeDict

__all__ = ["AttributeDict"]
__version__ = "0.1.0"
