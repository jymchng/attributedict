"""setuptools build configuration for the C extension.

The extension is built with the Limited API / Stable ABI (abi3) enabled so
that a single ``cp39-abi3`` wheel covers CPython 3.9-3.14 (D-002, PKG-003).

Two mechanisms work together:
- ``Extension(py_limited_api=True)`` names the built artifact ``*.abi3.so``;
- ``bdist_wheel py_limited_api="cp39"`` makes the wheel tag ``cp39-abi3``
  (without this, bdist_wheel falls back to the interpreter tag on builds
  where the runtime's EXTENSION_SUFFIXES lack an ``.abi3`` entry).
"""

from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "attributedict._attributedict",
            sources=["src/attributedict/_attributedict.c"],
            py_limited_api=True,
        ),
    ],
    options={
        "bdist_wheel": {
            "py_limited_api": "cp39",
        },
    },
)
