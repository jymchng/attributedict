# Compatibility

## Validated matrix

| Environment | Result |
|---|---|
| CPython 3.10 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.11 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.12 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.13 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.14 (linux x86_64) | ✅ 191 tests pass |
| CPython 3.9 | ✅ covered by CI matrix (`tests.yml`) |
| abi3 wheel `cp39-abi3` on CPython 3.10 | ✅ installs + all pickle protocols |
| Windows x86_64 / macOS arm64+x86_64 / manylinux x86_64+aarch64 | ✅ cibuildwheel matrix (`wheels.yml`) |
| PyPy | ❌ not supported (v1) |
| Free-threaded CPython 3.13t | ❌ not supported (v1) |

Validated 2026-08-15 on linux x86_64 (CPython 3.10.20, 3.11.15, 3.12.13,
3.13.13, 3.14.4).

## Interop with dataclasses / pydantic / SQLAlchemy / TypedDict

`AttributeDict` is a genuine `dict` subclass, so it interoperates with the
mapping-based APIs of the most common structured-data libraries. The matrix
below was validated empirically in a dedicated CPython 3.13.13 environment
(`pydantic` 2.13.4, `sqlalchemy` 2.0.52) using the probe scripts referenced
at the end of this section.

### Coercion: AttributeDict INTO each construct

| Construct | Works? | How |
|---|---|---|
| `dataclasses` | ✅ | `Cfg(**ad)` builds an instance; `dataclasses.asdict()` round-trips to a plain `dict` |
| `pydantic` | ✅ | `Model.model_validate(ad)` and `Model.model_construct(**ad)` |
| `sqlalchemy` | ✅ | `Row(**ad)` builds a mapped instance; `session.add`/commit persists; Core `insert().values(ad)` builds a statement |
| `TypedDict` | ✅ | structural compliance — keys and value types match the annotation (shape-checked at runtime) |

### Held as a value: each construct holding an AttributeDict

| Construct | Works? | Notes |
|---|---|---|
| `dataclasses` | ✅ | a field holds the AttributeDict instance (identity preserved); mutations through the field mutate the AttributeDict |
| `pydantic` | ✅* | a field accepts an AttributeDict and keeps its data — but pydantic **coerces a `dict`-typed field to a plain `dict`**, so attribute-access sugar is lost after validation (see caveats) |
| `sqlalchemy` | ✅* | a JSON column accepts an AttributeDict and round-trips its data correctly — but SQLAlchemy **normalizes** the in-memory value to a plain `dict` (see caveats) |
| `TypedDict` | ✅ | a value can be an AttributeDict matching the nested TypedDict shape |

### Inheritance behavior

**Axis (i) — subclassing `AttributeDict` itself: works.**
Custom class attributes, methods, and overrides all behave; `tp_getattro` /
`tp_setattro` remain intact on subclasses (item + attribute access,
attribute-set → item). The one gotcha is the documented "type attributes
win" rule applied to subclass members: a **method named like a key shadows
the key on the attribute path** (`d.env` returns the method), while
`d["env"]` still returns the item.

**Axis (ii) — AttributeDict within typed-model hierarchies: works.**
- **dataclass**: an inherited field holding an AttributeDict works across a
  base → child hierarchy.
- **pydantic**: a subclass's inherited dict field validates from an
  AttributeDict (data preserved; subtype-coercion caveat applies).
- **sqlalchemy**: single-table polymorphic inheritance persists a row whose
  JSON column was an AttributeDict, reloads the correct subclass, and
  round-trips the data.

### Caveats

1. **Subtype normalization**: pydantic (dict-typed fields) and SQLAlchemy
   (JSON columns) convert an AttributeDict to a plain `dict` on
   validation/assignment. The data is preserved, but attribute-access sugar
   is lost at the boundary — re-wrap with `AttributeDict(...)` if you need
   it after validation.
2. **Type-attribute shadowing**: a method (dict built-in or subclass method)
   whose name collides with a key wins on the attribute path. Use item
   access (`d["key"]`) for keys that look like Python attribute names.

### Reproduce

```bash
/tmp/attrdict-env/bin/python docs/attributedict-coercion-probe.py     # 8/8 PASS
/tmp/attrdict-env/bin/python docs/attributedict-heldvalue-probe.py    # 8/10 PASS (2 expected findings)
/tmp/attrdict-env/bin/python docs/attributedict-inheritance-probe.py  # 12/12 PASS
```

## Version-specific notes

- **Pickle**: all protocols (0–5) verified on every tested version; the
 `__reduce__` 5-tuple form is stable across 3.10–3.14.
- **dict subclass internals**: no version-specific behavior differences
 observed across 3.10–3.14 (mapping views, fromkeys, copy, equality,
 unhashable).
- **repr recursion**: `Py_ReprEnter`/`Py_ReprLeave` behave identically
 across the range.
- **GC**: the portable `Py_VISIT`/`Py_CLEAR` pattern works on all tested
 versions (no `PyObject_VisitManagedDict` dependency — mitigation).

## Unsupported environments (documented)

- **PyPy** and other non-CPython interpreters.
- **Free-threaded CPython 3.13t** — not validated; explicitly unsupported
 in v1.

If you need support for these, please open an issue; CI validation would be
required before declaring support.
