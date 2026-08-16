# Nested conversion

## What happens at construction

When you build an `AttributeDict`, every contained mapping is recursively
converted into an `AttributeDict` — including mappings inside lists and
tuples (FR-007, D-003):

```python
from attributedict import AttributeDict

x = AttributeDict({
    "database": {
        "host": "localhost",
        "ports": [5432, {"tls": True}],
    }
})

x.database.host        # "localhost"
x.database.ports[0]    # 5432
x.database.ports[1].tls  # True
```

## What is NOT converted

- `set` / `frozenset` are left untouched (A-008).
- Any non-container value is left as-is (identity preserved).
- An already-converted `AttributeDict` passed as a value is **shared**
  (idempotent conversion — shallow-copy semantics).

## Cycle safety

Conversion is cycle-safe (FR-007): a mapping that is being converted is
reused rather than re-converted, so self-referential structures terminate
and the cycle is preserved:

```python
inner = {}
outer = {"self": inner}
inner["back"] = outer

d = AttributeDict(outer)
d.self.back is d  # True — the cycle is preserved
```

## Cost

Construction is O(n) in the number of contained items (R-005). See
[performance](performance.md) for measured data.
