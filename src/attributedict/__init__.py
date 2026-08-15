"""attributedict: dict semantics with attribute access.

Public API::

    from attributedict import AttributeDict

The performance-critical implementation lives in the C extension module
``attributedict._attributedict``. This module is a thin public wrapper.

The distribution is published on PyPI as ``py-attributedict`` (the import
name stays ``attributedict``).
"""

from importlib.metadata import PackageNotFoundError, version

from ._attributedict import AttributeDict

try:
    __version__: str = version("py-attributedict")
except PackageNotFoundError:  # pragma: no cover - editable/source installs
    __version__ = "0.0.0+unknown"

__all__ = ["AttributeDict"]  # public API contract (DOC-001)
# __version__ stays a module-level attribute, intentionally not in __all__.
