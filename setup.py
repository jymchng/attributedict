"""setuptools build configuration for the C extension.

The extension is built with the Limited API / Stable ABI (abi3) enabled so
that a single ``cp39-abi3`` wheel covers CPython 3.9-3.14 (D-002, PKG-003).

Two mechanisms work together:
- ``Extension(py_limited_api=True)`` names the built artifact ``*.abi3.so``;
- ``bdist_wheel py_limited_api="cp39"`` makes the wheel tag ``cp39-abi3``
  (without this, bdist_wheel falls back to the interpreter tag on builds
  where the runtime's EXTENSION_SUFFIXES lack an ``.abi3`` entry).

Pyodide (WebAssembly/emscripten) exception: pyodide wheels are tagged
``cpXY-emscripten_*_wasm32`` and do NOT use the stable ABI, so abi3 tagging
is skipped when building under emscripten (``sys.platform == 'emscripten'``).
"""

import sys

from setuptools import Extension, setup

IS_EMSCRIPTEN = sys.platform == "emscripten"

ext_kwargs = {}
options = {}
if not IS_EMSCRIPTEN:
    # abi3 only applies to non-emscripten (native) builds.
    ext_kwargs["py_limited_api"] = True
    options["bdist_wheel"] = {"py_limited_api": "cp39"}

setup(
    ext_modules=[
        Extension(
            "attributedict._attributedict",
            sources=["src/attributedict/_attributedict.c"],
            **ext_kwargs,
        ),
    ],
    options=options,
)
