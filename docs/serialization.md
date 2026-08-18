# Serialization

## Copy

- `copy.copy(d)` returns a shallow `AttributeDict` (nested values shared).
- `copy.deepcopy(d)` returns a deep `AttributeDict`; nested `AttributeDict`
 instances stay `AttributeDict`. Self-references and cycles terminate and
 are preserved.

```python
import copy

d = AttributeDict(a=1, nested=AttributeDict(x=1))
shallow = copy.copy(d) # shallow.nested is d.nested
deep = copy.deepcopy(d) # deep.nested is not d.nested; same value
```

## Pickle

`pickle.dumps`/`pickle.loads` are supported across **all protocols (0–5)**,
preserving structure, the `AttributeDict` type, and reference cycles:

```python
import pickle

d = AttributeDict(a=1, nested=AttributeDict(x=[1, {"y": 2}]))
loaded = pickle.loads(pickle.dumps(d))
# type(loaded) is AttributeDict; type(loaded.nested) is AttributeDict
```

How it works: `AttributeDict.__reduce__` returns
`(reconstruct, (cls), None, None, iter(self.items))` — the 5-tuple form
lets pickle apply items lazily through its memo, so cyclic structures pickle
without recursion. `attributedict._pickle_support.reconstruct` creates the
empty instance.

## JSON / YAML / dataclasses

Interop with dataclasses / pydantic / SQLAlchemy / TypedDict **is supported**
(see [compatibility.md](compatibility.md)); the caveat is that those layers
normalize an AttributeDict to a plain `dict`. For JSON, converting to a
plain dict first remains the cleanest path:

```python
import json
json.dumps(dict(d))
```
