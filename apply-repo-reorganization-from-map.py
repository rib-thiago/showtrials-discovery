#!/usr/bin/env python3
"""Apply repository reorganization from repo-reorganization-map.tsv."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "repo-reorganization-map.tsv"
APPLY_TSV = ROOT / "repo-reorganization-apply.tsv"
APPLY_REPORT = ROOT / "repo-reorganization-apply-report.txt"

REQUIRED_FIELDS = [
    "current_path",
    "proposed_path",
    "phase",
    "artifact_type",
    "commit_group",
    "mtime_iso",
    "notes",
]

APPLY_FIELDS = ["current_path", "proposed_path", "status", "notes"]
PRESERVE_SELF = {"README.md", ".gitignore"}


def read_map(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing input map: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"Map is missing required fields: {', '.join(missing)}")
        return list(reader)


def write_apply(rows: list[dict[str, str]]) -> None:
    with APPLY_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=APPLY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict[str, str]], directories_created: int) -> None:
    counts = Counter(row["status"] for row in rows)
    report = [
        "Repository Reorganization Apply Report",
        f"map\t{MAP_PATH}",
        f"apply_tsv\t{APPLY_TSV}",
        f"files_planned\t{len(rows)}",
        f"files_moved\t{counts.get('moved', 0)}",
        f"files_skipped\t{counts.get('skipped', 0) + counts.get('dry_run', 0)}",
        f"files_failed\t{counts.get('failed', 0)}",
        f"directories_created\t{directories_created}",
    ]
    APPLY_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")


def rel_path(value: str, field: str) -> Path:
    if not value:
        raise ValueError(f"{field} is empty")
    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"{field} must be relative: {value}")
    if ".." in path.parts:
        raise ValueError(f"{field} must not contain '..': {value}")
    return path


def prevalidate(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    seen_sources: set[str] = set()
    seen_targets: set[str] = set()
    planned_sources = {row.get("current_path", "").strip() for row in rows}

    for idx, row in enumerate(rows, start=2):
        current_value = row.get("current_path", "").strip()
        proposed_value = row.get("proposed_path", "").strip()
        try:
            current_rel = rel_path(current_value, "current_path")
            proposed_rel = rel_path(proposed_value, "proposed_path")
        except ValueError as exc:
            errors.append(f"line {idx}: {exc}")
            continue

        if current_value in seen_sources:
            errors.append(f"line {idx}: duplicate current_path: {current_value}")
        seen_sources.add(current_value)

        if proposed_value in seen_targets:
            errors.append(f"line {idx}: duplicate proposed_path: {proposed_value}")
        seen_targets.add(proposed_value)

        current_abs = ROOT / current_rel
        proposed_abs = ROOT / proposed_rel

        if not current_abs.exists():
            errors.append(f"line {idx}: current_path does not exist: {current_value}")

        if current_value == proposed_value:
            if current_value not in PRESERVE_SELF:
                errors.append(f"line {idx}: self-mapped file is not explicitly preserved: {current_value}")
            continue

        if proposed_abs.exists():
            errors.append(f"line {idx}: proposed_path already exists: {proposed_value}")

        if proposed_value in planned_sources:
            errors.append(
                f"line {idx}: proposed_path is also a current_path in this map; chained moves are not allowed: {proposed_value}"
            )

    return errors


def planned_directories(rows: list[dict[str, str]]) -> set[Path]:
    directories: set[Path] = set()
    for row in rows:
        current_value = row["current_path"].strip()
        proposed_value = row["proposed_path"].strip()
        if current_value == proposed_value:
            continue
        parent = (ROOT / rel_path(proposed_value, "proposed_path")).parent
        if parent != ROOT:
            directories.add(parent)
    return directories


def build_status_rows(rows: list[dict[str, str]], status: str, note: str) -> list[dict[str, str]]:
    return [
        {
            "current_path": row.get("current_path", "").strip(),
            "proposed_path": row.get("proposed_path", "").strip(),
            "status": status,
            "notes": note,
        }
        for row in rows
    ]


def apply_moves(rows: list[dict[str, str]], dry_run: bool) -> tuple[list[dict[str, str]], int]:
    directories = planned_directories(rows)
    created_count = 0
    status_rows: list[dict[str, str]] = []

    if dry_run:
        return build_status_rows(rows, "dry_run", "validated only; no files moved"), 0

    for directory in sorted(directories):
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=False)
            created_count += 1

    for row in rows:
        current_value = row["current_path"].strip()
        proposed_value = row["proposed_path"].strip()
        current_abs = ROOT / rel_path(current_value, "current_path")
        proposed_abs = ROOT / rel_path(proposed_value, "proposed_path")

        if current_value == proposed_value:
            status_rows.append(
                {
                    "current_path": current_value,
                    "proposed_path": proposed_value,
                    "status": "skipped",
                    "notes": "preserved at root",
                }
            )
            continue

        try:
            current_abs.rename(proposed_abs)
            status_rows.append(
                {
                    "current_path": current_value,
                    "proposed_path": proposed_value,
                    "status": "moved",
                    "notes": "moved by pathlib.Path.rename",
                }
            )
        except OSError as exc:
            status_rows.append(
                {
                    "current_path": current_value,
                    "proposed_path": proposed_value,
                    "status": "failed",
                    "notes": str(exc),
                }
            )
            raise

    return status_rows, created_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply repository reorganization from TSV map.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and write reports without moving files.")
    args = parser.parse_args()

    rows = read_map(MAP_PATH)
    errors = prevalidate(rows)
    if errors:
        failed_rows = build_status_rows(rows, "failed", "prevalidation failed; no files moved")
        write_apply(failed_rows)
        write_report(failed_rows, 0)
        message = "\n".join(errors[:50])
        if len(errors) > 50:
            message += f"\n... {len(errors) - 50} additional errors"
        raise SystemExit(f"Prevalidation failed; no files moved.\n{message}")

    status_rows, directories_created = apply_moves(rows, args.dry_run)
    write_apply(status_rows)
    write_report(status_rows, directories_created)

    print(APPLY_TSV)
    print(APPLY_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
