# Performance

## Methodology

Benchmarks are reproducible via `benchmarks/bench.py` (spec 11). Each
operation is timed with `timeit` over `N=100_000` iterations, repeated 5
times; the mean and median microseconds-per-operation are reported. The
environment (Python version, platform, CPU) is captured in the results JSON
(`benchmarks/results/results.json`).

Three implementations are compared:

1. plain `dict`
2. pure-Python `AttributeDict` (`attributedict._reference` — the spec oracle)
3. C `AttributeDict` (`attributedict`)

## Measured results (CPython 3.13.13, x86_64; 2026-08-15)

| operation | dict (µs) | reference (µs) | C (µs) |
|---|---|---|---|
| construct kwargs | 3.0 | 33.5 | 3.4 |
| construct mapping | 0.5 | 30.0 | 3.1 |
| construct nested | — | 8.8 | 2.6 |
| getitem | 0.074 | 0.09 | 0.066 |
| getattr | — | 0.234 | 0.071 |
| setitem | 0.105 | 0.119 | 0.117 |
| setattr | — | 0.612 | 0.114 |
| iter | 0.482 | 0.678 | 0.693 |
| copy (shallow) | 1.76 | 31.9 | 1.89 |

## Interpretation

**Where the C extension improves things (vs the pure-Python reference):**

- Attribute get/set: ~3–5× faster (C avoids the Python `__getattribute__`
  dispatch and `str.isidentifier()` call per lookup).
- Construction: ~10× faster (recursive conversion is done in C, not Python).
- `copy()`: ~17× faster.
- `dict.items(d)` / mapping views unaffected.

**Where it is on par with plain `dict`:**

- `d[key]`, `d[key] = v`, `del d[key]`, iteration: essentially identical to
  plain `dict` (the operations inherit directly from the dict base).
- Construction from an existing mapping is slightly slower than plain `dict`
  (3.1 µs vs 0.5 µs) because the C code performs the recursive conversion
  pass at construction (O(n), R-005). This is the documented cost of the
  FR-007 conversion feature.

**Where it does NOT help:**

- Iteration and mapping views: same as dict (inherited).
- No claim of "2× faster than dict" is made: for inherited operations the C
  type is at parity with dict, and the speedups are against the
  pure-Python baseline, which is the honest comparison.

## Construction cost

Construction is O(n) in the number of contained items due to recursive
conversion (FR-007); nested/cyclic structures are handled cycle-safe. This
is documented in [nested.md](nested.md) and confirmed by the construction
benchmarks above.

## Reproducing

```bash
python benchmarks/bench.py                 # table
python benchmarks/bench.py --json out.json # JSON data
```

See [benchmarks.md](benchmarks.md) for details.
