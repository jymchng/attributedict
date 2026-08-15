# 05 — System Architecture

## Purpose

Describe the system architecture: the C object, its storage, attribute
resolution, and the Python wrapper layer.

## Scope

Architecture decisions D-001…D-011, the C layout, and the Python-facing
boundary.

## Architectural Overview

```text
Python public API: attributedict.AttributeDict (thin wrapper)
        ↓
C extension: attributedict._attributedict (module init)
        ↓
C type: AttributeDict_Type (PyTypeObject)
   - inherits from dict (PyDict_Type)
   - custom tp_getattro / tp_setattro
   - custom tp_new / tp_init (recursive conversion)
   - GC slots (tp_traverse / tp_clear) because it holds Python objects
```

## C Object Design

- **Layout**: the type is a subclass of `dict`, so it uses `PyDictObject`
  storage (entries owned by the dict); no extra per-instance C struct needed
  beyond the base. Recursive conversion is done during construction, not
  stored separately.
- **GC**: because the object can participate in reference cycles (contained
  values may reference the AttributeDict), the type implements
  `tp_traverse`/`tp_clear` using the portable `Py_VISIT`/`Py_CLEAR` pattern
  over the dict items — the `PyObject_VisitManagedDict` helpers are NOT
  public in the Limited API as of 3.13; see "Verified Limited-API
  availability" below.
- **Weakrefs**: inherit dict's weakref support if applicable; tested.

## Verified Limited-API availability (I-003)

Static analysis of CPython 3.13 headers (Limited API, 3.9 target):

- Public and used: `PyDict_Type`, `PyDict_GetItemWithError`, `PyDict_SetItem`,
  `PyDict_DelItem`, `PyDict_Contains`, `PyObject_GenericGetAttr`,
  `PyObject_GenericSetAttr`, `PyObject_GenericGetDict`, `PyUnicode_IsIdentifier`,
  `Py_ReprEnter`/`Py_ReprLeave`, `Py_VISIT`/`Py_CLEAR`,
  `Py_TPFLAGS_BASETYPE`/`Py_TPFLAGS_HAVE_GC`.
- NOT public in 3.13: `PyObject_VisitManagedDict`/`PyObject_ClearManagedDict`,
  `PyObject_GC_Visit`/`PyObject_GC_Clear`. GC must use the portable
  `Py_VISIT`/`Py_CLEAR` pattern (see docs/architecture.md).
- No required API is missing from the Limited API for 3.9+.

## Mapping-protocol approach

Because the type subclasses `PyDict_Type`:

- `mp_length`, `mp_subscript`, `mp_ass_subscript`, `sq_contains` are
  **inherited** from dict — no overrides needed (FR-008).
- `tp_richcompare` inherited — dict equality (FR-011).
- `tp_hash` inherited — unhashable (FR-012, D-007).
- dict methods (`get`, `setdefault`, `update`, `pop`, `popitem`, `clear`,
  `copy`, `keys`, `items`, `values`, `fromkeys`) inherited; `copy` and
  `fromkeys` overridden to return `AttributeDict` (FR-009).

## GC pattern for a dict subclass (portable)

`tp_traverse` visits the dict items (keys and values) via `PyDict_Items` +
`Py_VISIT`; `tp_clear` clears the dict contents. This is correct for cycles
and available in the Limited API across 3.9–3.14.

## Attribute Resolution (tp_getattro)

Resolution order (final, per I-024 superseding D-004 keys-win):

1. Look up the name as a **real type attribute** via
   `PyObject_GenericGetAttr` (methods, descriptors, dunders). If found,
   return it.
2. Otherwise, if the name is a `str` that is a valid identifier **and** a
   mapping key, return the key's value.
3. Otherwise raise `AttributeError`.

This makes `d.items` return the bound `dict.items` method even when a key
`"items"` exists; the key's value is reachable via mapping access
(`d["items"]`) and via `dict.items(d)`. Descriptors/data-descriptors on the
type are never shadowed by keys; documented + tested.

## Attribute Set/Delete (tp_setattro)

- `d.name = value` → `d["name"] = value` (always mapping assignment).
- `del d.name` → delete key `"name"`; if absent, raise AttributeError
  (mirroring the attribute-delete expectation; exact message documented).
- Setting/deleting names that are not valid identifiers is still a mapping
  operation via attribute syntax only when the name is a valid attribute
  name; otherwise AttributeError.

## Python Wrapper Layer

`src/attributedict/__init__.py` re-exports `AttributeDict` from the C module
and defines `__all__`. `py.typed` is shipped. No substantial logic lives in
the wrapper.

## C Source Layout

```text
src/attributedict/
├── __init__.py        # public re-export
├── py.typed
└── _attributedict.c   # module init + type definition
```

If complexity grows, split into `module.c`, `attributedict.c/.h`,
`conversion.c/.h`, `attributes.c/.h` — only if each file has a coherent
responsibility.

## Constraints

- C-002 isinstance(d, dict) true (subclass).
- C-003 abi3 (Limited API only).
- C-004 no third-party runtime deps.

## Decisions

- D-001 subclass dict + custom tp_getattro/tp_setattro.
- D-002 abi3.
- D-003 recursive conversion.
- D-004 keys win.
- D-007 unhashable.

## Cross-references

- 03-functional-requirements, 04-non-functional-requirements,
  08-api-specification, 07-memory-management, decisions.md.
