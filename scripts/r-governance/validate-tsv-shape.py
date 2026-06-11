#!/usr/bin/env python3
"""Validate that TSV rows have the same column count as the header."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def validate(path: Path) -> tuple[int, int, list[tuple[int, int]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))

    if not rows:
        return 0, 0, [(0, 0)]

    expected = len(rows[0])
    bad = []

    for line_no, row in enumerate(rows[1:], start=2):
        if len(row) != expected:
            bad.append((line_no, len(row)))

    return expected, len(rows) - 1, bad


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TSV column shape.")
    parser.add_argument("paths", nargs="+", help="TSV files to validate")
    args = parser.parse_args()

    failures = 0

    for raw in args.paths:
        path = Path(raw)
        expected, data_rows, bad = validate(path)

        print(f"path\t{path}")
        print(f"header_cols\t{expected}")
        print(f"data_rows\t{data_rows}")
        print(f"bad_rows\t{len(bad)}")

        for line_no, cols in bad[:30]:
            print(f"bad\tline={line_no}\tcols={cols}")

        if bad:
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
