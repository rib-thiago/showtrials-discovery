#!/usr/bin/env python3
"""Validate completed repository reorganization from repo-reorganization-map.tsv."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "repo-reorganization-map.tsv"
VALIDATION_TSV = ROOT / "repo-reorganization-validation.tsv"
VALIDATION_REPORT = ROOT / "repo-reorganization-validation-report.txt"

REQUIRED_FIELDS = [
    "current_path",
    "proposed_path",
    "phase",
    "artifact_type",
    "commit_group",
    "mtime_iso",
    "notes",
]

VALIDATION_FIELDS = ["current_path", "proposed_path", "validation_status", "notes"]


def read_map(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing input map: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"Map is missing required fields: {', '.join(missing)}")
        return list(reader)


def rel_path(value: str, field: str) -> Path:
    if not value:
        raise ValueError(f"{field} is empty")
    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"{field} must be relative: {value}")
    if ".." in path.parts:
        raise ValueError(f"{field} must not contain '..': {value}")
    return path


def status_row(row: dict[str, str], status: str, notes: str) -> dict[str, str]:
    return {
        "current_path": row.get("current_path", "").strip(),
        "proposed_path": row.get("proposed_path", "").strip(),
        "validation_status": status,
        "notes": notes,
    }


def validate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    proposed_seen: set[str] = set()

    for row in rows:
        current_value = row.get("current_path", "").strip()
        proposed_value = row.get("proposed_path", "").strip()
        try:
            current_abs = ROOT / rel_path(current_value, "current_path")
            proposed_abs = ROOT / rel_path(proposed_value, "proposed_path")
        except ValueError as exc:
            results.append(status_row(row, "fail", str(exc)))
            continue

        notes: list[str] = []
        status = "ok"

        if proposed_value in proposed_seen:
            status = "fail"
            notes.append("duplicate proposed_path in map")
        proposed_seen.add(proposed_value)

        if current_value == proposed_value:
            if not current_abs.exists():
                status = "fail"
                notes.append("self-mapped file is missing")
            else:
                notes.append("self-mapped file exists")
        else:
            if current_abs.exists():
                status = "fail"
                notes.append("old current_path still exists")
            if not proposed_abs.exists():
                status = "fail"
                notes.append("proposed_path is missing")
            if status == "ok":
                notes.append("moved path validated")

        results.append(status_row(row, status, "; ".join(notes)))

    for root_file in ["README.md", ".gitignore"]:
        path = ROOT / root_file
        if not path.exists():
            results.append(
                {
                    "current_path": root_file,
                    "proposed_path": root_file,
                    "validation_status": "fail",
                    "notes": f"{root_file} is missing from repository root",
                }
            )

    return results


def write_validation(rows: list[dict[str, str]]) -> None:
    with VALIDATION_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=VALIDATION_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows_checked: int, results: list[dict[str, str]]) -> None:
    counts = Counter(row["validation_status"] for row in results)
    report = [
        "Repository Reorganization Validation Report",
        f"map\t{MAP_PATH}",
        f"validation_tsv\t{VALIDATION_TSV}",
        f"rows_checked\t{rows_checked}",
        f"passes\t{counts.get('ok', 0)}",
        f"warnings\t{counts.get('warning', 0)}",
        f"failures\t{counts.get('fail', 0)}",
    ]
    VALIDATION_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    rows = read_map(MAP_PATH)
    results = validate_rows(rows)
    write_validation(results)
    write_report(len(rows), results)

    print(VALIDATION_TSV)
    print(VALIDATION_REPORT)
    failures = sum(1 for row in results if row["validation_status"] == "fail")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
