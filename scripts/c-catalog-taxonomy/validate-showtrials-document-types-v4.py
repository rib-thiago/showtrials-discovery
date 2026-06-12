#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    DOCUMENT_TYPES_V4,
    DOCUMENT_TYPES_V4_VALIDATION,
    DOCUMENT_TYPES_V4_VALIDATION_REPORT,
    MASTER_CATALOG,
    ensure_parent,
)

DOCS = DOCUMENT_TYPES_V4
CATALOG = MASTER_CATALOG

REPORT = DOCUMENT_TYPES_V4_VALIDATION_REPORT
TSV = DOCUMENT_TYPES_V4_VALIDATION

failures = []
warnings = []

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    catalog_rows = list(csv.DictReader(f, delimiter="\t"))

with DOCS.open("r", encoding="utf-8", newline="") as f:
    type_rows = list(csv.DictReader(f, delimiter="\t"))

catalog_ids = {r["document_post_id"] for r in catalog_rows}
type_ids = {r["document_post_id"] for r in type_rows}

if len(type_rows) != len(catalog_rows):
    failures.append(("row_count", f"catalog={len(catalog_rows)} types={len(type_rows)}"))

missing = catalog_ids - type_ids
extra = type_ids - catalog_ids

if missing:
    failures.append(("missing_ids", str(len(missing))))
if extra:
    failures.append(("extra_ids", str(len(extra))))

type_counts = Counter(r["document_type"] for r in type_rows)
unknown = type_counts.get("unknown", 0)

if unknown > 0:
    warnings.append(("unknown_remaining", f"unknown={unknown}"))

with ensure_parent(TSV).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["level", "check", "message"])
    for k, msg in failures:
        w.writerow(["FAIL", k, msg])
    for k, msg in warnings:
        w.writerow(["WARN", k, msg])
    if not failures and not warnings:
        w.writerow(["OK", "all_checks", "validation passed"])

report = []
report.append("ShowTrials document types v4 validation")
report.append("")
report.append(f"Catalog rows: {len(catalog_rows)}")
report.append(f"Type rows: {len(type_rows)}")
report.append(f"Failures: {len(failures)}")
report.append(f"Warnings: {len(warnings)}")
report.append("")
report.append("Type counts:")
for dtype, count in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{dtype}")

if failures:
    report.append("")
    report.append("Failures:")
    for k, msg in failures:
        report.append(f"{k}\t{msg}")

if warnings:
    report.append("")
    report.append("Warnings:")
    for k, msg in warnings:
        report.append(f"{k}\t{msg}")

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)
