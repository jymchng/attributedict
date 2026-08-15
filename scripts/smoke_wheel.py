"""Smoke-test an installed attributedict wheel (used by CI wheels.yml).

Run from a clean venv after ``pip install`` of a wheel::

    python scripts/smoke_wheel.py
"""

import attributedict
from attributedict import AttributeDict

d = AttributeDict(host="x", nested={"a": [1, {"b": 2}]})
assert d.host == "x" and d.nested.a[1].b == 2
assert isinstance(d.nested, AttributeDict)
assert attributedict.__version__

print(f"wheel smoke OK (attributedict {attributedict.__version__})")
