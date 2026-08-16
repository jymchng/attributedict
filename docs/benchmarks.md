# Benchmarks

## How to run

```bash
python benchmarks/bench.py # print the comparison table
python benchmarks/bench.py --json benchmarks/results/results.json # write JSON
```

## What is measured

- Construction: kwargs, mapping, nested (reference + C; plain dict where
 applicable).
- Key lookup / assignment / deletion (`d[k]`, `d[k]=v`, `del d[k]`).
- Attribute lookup / assignment / deletion (`d.name`, `d.name=v`, `del d.name`).
- Iteration (`list(d)`).
- Shallow copy (`d.copy`).

Each operation is compared across plain `dict`, the pure-Python reference
(`attributedict._reference`), and the C `AttributeDict`.

## Methodology

- `timeit` with `N=100_000` iterations, 5 repeats; report mean and median
 microseconds per operation.
- Warm cache: one untimed run precedes the timed repeats.
- Environment (Python version, platform, CPU) is captured in the JSON output
 for reproducibility.
- Import/module setup is never measured (imports happen before timing).

## Results

Committed as data in `benchmarks/results/results.json`. Summarized in
[performance.md](performance.md).

## CI

Benchmarks are not run in full in CI; a smoke run validates the
script executes. Full results are produced on demand by maintainers.
