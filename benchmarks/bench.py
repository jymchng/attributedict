"""Reproducible benchmarks for AttributeDict (I-014).

Compares, for each operation:
  1. plain dict
  2. pure-Python AttributeDict (attributedict._reference)
  3. C AttributeDict (attributedict)

Methodology (spec 11):
- fixed environment captured in the output (python version, platform, cpu)
- warm cache: each timed loop runs `repeat` times; we report best-of-repeats
  (median) per operation, which is the standard timeit best-of-N approach
- no import/module setup measured (imports happen before timing)

Usage:
    python benchmarks/bench.py                # run all, print table
    python benchmarks/bench.py --json out.json  # write results as JSON

Output: benchmarks/results/*.json (committed as data).
"""

from __future__ import annotations

import argparse
import copy
import json
import platform
import sys
import timeit
from pathlib import Path

from attributedict import AttributeDict
from attributedict._reference import AttributeDict as RefAttributeDict

N = 100_000  # loop iterations per timing

# Construction inputs
MAPPING = {f"key{i}": i for i in range(50)}
KWARGS = {f"key{i}": i for i in range(50)}
NESTED = {"db": {"host": "x", "ports": [1] + [{"a": 2}] * 10}}

# Pre-built objects for lookup/set/del/iter/copy benchmarks
DICT = {f"key{i}": i for i in range(50)}
REF = RefAttributeDict(DICT)
C = AttributeDict(DICT)


def bench(name: str, stmt: str, globs: dict) -> dict:
    """Time *stmt* with the given globals; return {name, mean_us, median_us}."""
    timer = timeit.Timer(stmt, globals=globs)
    # warm cache
    timer.timeit(1)
    samples = timer.repeat(repeat=5, number=N)
    # samples are seconds per `number` runs; convert to us per op
    per_op = [s / N * 1e6 for s in samples]
    mean = sum(per_op) / len(per_op)
    ordered = sorted(per_op)
    median = ordered[len(ordered) // 2]
    return {"name": name, "mean_us_per_op": round(mean, 3), "median_us_per_op": round(median, 3)}


def run_all() -> list[dict]:
    results = []

    # --- construction ---
    results.append(bench("construct_kwargs_dict", "dict(**KWARGS)", globals()))
    results.append(bench("construct_kwargs_ref", "RefAttributeDict(**KWARGS)", globals()))
    results.append(bench("construct_kwargs_c", "AttributeDict(**KWARGS)", globals()))

    results.append(bench("construct_mapping_dict", "dict(MAPPING)", globals()))
    results.append(bench("construct_mapping_ref", "RefAttributeDict(MAPPING)", globals()))
    results.append(bench("construct_mapping_c", "AttributeDict(MAPPING)", globals()))

    results.append(bench("construct_nested_ref", "RefAttributeDict(NESTED)", globals()))
    results.append(bench("construct_nested_c", "AttributeDict(NESTED)", globals()))

    # --- key lookup ---
    results.append(bench("getitem_dict", "DICT['key25']", globals()))
    results.append(bench("getitem_ref", "REF['key25']", globals()))
    results.append(bench("getitem_c", "C['key25']", globals()))

    # --- attribute lookup ---
    results.append(bench("getattr_ref", "REF.key25", globals()))
    results.append(bench("getattr_c", "C.key25", globals()))

    # --- key assignment ---
    results.append(bench("setitem_dict", "DICT['k'] = 1; del DICT['k']", globals()))
    results.append(bench("setitem_ref", "REF['k'] = 1; del REF['k']", globals()))
    results.append(bench("setitem_c", "C['k'] = 1; del C['k']", globals()))

    # --- attribute assignment ---
    results.append(bench("setattr_ref", "REF.k = 1; del REF.k", globals()))
    results.append(bench("setattr_c", "C.k = 1; del C.k", globals()))

    # --- iteration ---
    results.append(bench("iter_dict", "list(DICT)", globals()))
    results.append(bench("iter_ref", "list(REF)", globals()))
    results.append(bench("iter_c", "list(C)", globals()))

    # --- copy (shallow) ---
    results.append(bench("copy_dict", "DICT.copy()", globals()))
    results.append(bench("copy_ref", "REF.copy()", globals()))
    results.append(bench("copy_c", "C.copy()", globals()))

    return results


def environment() -> dict:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu": platform.processor() or "unknown",
        "loop_iterations": N,
        "repeat": 5,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", help="write results to this JSON file")
    args = parser.parse_args()

    print(f"=== attributedict benchmarks ({environment()['python']} on {environment()['machine']}) ===")
    results = run_all()
    env = environment()

    print(f"{'operation':<28}{'mean us/op':>12}{'median us/op':>14}")
    print("-" * 56)
    for r in results:
        print(f"{r['name']:<28}{r['mean_us_per_op']:>12}{r['median_us_per_op']:>14}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"environment": env, "results": results}, indent=2))
        print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
