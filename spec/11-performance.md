# 11 — Performance

## Purpose

Benchmark methodology and performance expectations.

## Scope

What to measure, against what, and how to report results.

## Benchmarks

Measure, at minimum:

- Construction (kwargs, mapping, nested).
- Key lookup / assignment / deletion.
- Attribute lookup / assignment / deletion.
- Iteration.
- Nested access (deeply nested AttributeDict).
- Copy (shallow + deep).

Compare: (1) plain `dict`, (2) pure-Python `AttributeDict` baseline,
(3) C `AttributeDict`.

## Methodology

- Use `pyperf` or `pytest-benchmark` with a fixed, documented environment
  (Python version, OS, CPU if reported).
- Repeat runs; report mean + spread (e.g. median and p95).
- Run on a warm cache; avoid measuring import/module setup.
- Provide a reproducible `benchmarks/` script and a nox session `benchmarks`.

## Reporting

- Results stored as data (JSON/CSV) and summarized in `docs/performance.md`.
- Explicitly state what the C extension improves and where it does not
  (e.g. attribute vs key lookup may be similar; construction may be slower
  due to recursive conversion).
- No unsupported claims: a claim like "attribute access is 2× faster" must be
  backed by the measured data and methodology.

## Cross-references

- 04-non-functional-requirements (NFR-006), 10-testing, 14-documentation.
