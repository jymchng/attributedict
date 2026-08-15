# 03 — Functional Requirements

## Purpose

Precise functional requirements with stable identifiers.

## Scope

Every FR-001 … FR-015, with acceptance criteria, decisions, and cross-refs.

## Requirements

### FR-001 — Type and package identity
`AttributeDict` is the public type; package/import name is `attributedict`.
Users import from the Python package (`from attributedict import
AttributeDict`); the C extension module is an implementation detail, not the
public import path (thin Python wrapper in `src/attributedict/__init__.py`).

**AC**: `import attributedict; attributedict.AttributeDict is
attributedict._attributedict.AttributeDict`; no unstable C names in public API.

### FR-002 — Construction
Support all dict forms: `AttributeDict()`, `(mapping)`, `(iterable_of_pairs)`,
`(**kwargs)`, `(mapping, **kwargs)`. Inherit dict's `__new__`/`__init__`
behavior via the C subclass; recursive conversion (FR-007) applies at
construction.

**AC**: each form constructs an AttributeDict with correct contents.

### FR-003 — Attribute get
`d.foo` returns `d["foo"]` when `"foo"` is a key; otherwise raises
`AttributeError`.

**AC**: `AttributeDict(host="localhost").host == "localhost"`;
`AttributeDict().missing` raises AttributeError.

### FR-004 — Attribute set
`d.foo = x` stores `d["foo"] = x`.

**AC**: after `d.foo = 1`, `d["foo"] == 1`.

### FR-005 — Attribute delete
`del d.foo` deletes key `"foo"`; raises `AttributeError` (or `KeyError`
consistent with `del d["foo"]`? — spec decision: mirror `del d["foo"]`
KeyError semantics but surface as AttributeError; see decisions) when absent.

**AC**: after `del d.foo`, `"foo" not in d`.

### FR-006 — Key/method collision resolution — **keys win**
When a key name equals a real type attribute or method, the **real type
attribute wins on the attribute path** (I-024; supersedes the earlier
"keys win" decision D-004). `d = AttributeDict({"items": 42})` → `d.items`
is the bound `dict.items` method; the key's value is reachable via mapping
access (`d["items"] == 42`) and via `dict.items(d)`. Resolution order:
(1) real type attribute lookup; (2) else mapping-key lookup (identifier
keys only); (3) else AttributeError.

**AC**: `callable(d.items)` and `d["items"] == 42`; `dict.items(d)` is the
mapping view; documented + tested for `keys`, `values`, `get`, `update`,
`copy`, descriptors, dunders.

### FR-007 — Recursive nested conversion
At construction, recursively convert contained `dict` instances (and dicts
inside lists/tuples) into `AttributeDict`. Sets/frozensets are not converted
by default (documented). Conversion is cycle-safe (a mapping seen in-progress
is reused, not re-converted).

**AC**: `AttributeDict({"db": {"host": "x", "ports": [1, {"a": 2}]}})` yields
`.db.host == "x"` and `.db.ports[1].a == 2`.

### FR-008 — Mapping protocol + MutableMapping
`len`, `iter`, `getitem`, `setitem`, `delitem`, `contains` work; the type is
`collections.abc.MutableMapping`-compatible and `isinstance(d, dict)` is true
(C subclass of dict).

**AC**: protocol methods behave exactly like dict for valid keys.

### FR-009 — dict methods
Inherit `get`, `setdefault`, `update`, `pop`, `popitem`, `clear`, `copy`,
`keys`, `items`, `values`, `fromkeys` from the dict subclass. `fromkeys`
returns an `AttributeDict` (spec decision; tested).

**AC**: each method matches dict behavior; `fromkeys` returns AttributeDict.

### FR-010 — repr/str
`repr(AttributeDict({'a': 1})) == "AttributeDict({'a': 1})"`; nested values
use `repr` recursively; recursive structures render with `...` like dict.

**AC**: repr/str deterministic and debugging-useful.

### FR-011 — Equality
`==`/`!=` against AttributeDict, dict, other Mappings, unrelated objects use
dict semantics (dict's `tp_richcompare` inherited).

**AC**: `AttributeDict(a=1) == {"a": 1}` True; `== object()` False.

### FR-012 — Hashability
Unhashable, like dict.

**AC**: `hash(AttributeDict())` raises TypeError.

### FR-013 — Pickle and copy
`pickle.dumps/loads`, `copy.copy`, `copy.deepcopy` supported; nested
AttributeDict stays AttributeDict; self-references and cycles work.

**AC**: round-trips preserve structure and type; deepcopy of a self-referencing
AttributeDict terminates and preserves the cycle.

### FR-014 — Edge-case keys
Non-string keys (int, None, object, tuple) fully usable via mapping syntax.
Keys that are not valid identifiers ("with-space", "123", "foo-bar", "") are
usable via mapping but not attribute syntax. `_private` and `__dunder__`
keys are tested explicitly (attribute access behavior defined in 08).

**AC**: mapping access works for all; attribute access raises AttributeError
for non-identifiers; dunder/underscore behavior documented + tested.

### FR-015 — Error semantics
Missing key → KeyError; missing attribute → AttributeError; unhashable key →
TypeError. Exact messages documented. C code never leaves a stale exception
after a successful operation (`PyErr_Clear` discipline).

**AC**: tests assert exception types and message stability for the documented
cases.

## Cross-references

- 04-non-functional-requirements, 05-system-architecture, 08-api-specification,
  10-testing, decisions.md.
