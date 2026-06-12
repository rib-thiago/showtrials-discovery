#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PERSON_ORGANIZATION_MATRIX,
    PERSON_ORGANIZATION_MATRIX_VALIDATION_REPORT,
    ensure_parent,
)

MATRIX = PERSON_ORGANIZATION_MATRIX
REPORT = PERSON_ORGANIZATION_MATRIX_VALIDATION_REPORT

rows = list(csv.DictReader(MATRIX.open("r", encoding="utf-8", newline=""), delimiter="\t"))

failures = []
warnings = []

seen = set()

for r in rows:
    key = (r["person"], r["organization"])
    if key in seen:
        failures.append(f"duplicate pair: {key}")
    seen.add(key)

    if not r["person"]:
        failures.append("missing person")
    if not r["organization"]:
        failures.append(f"missing organization: {r.get('person')}")
    if int(r["document_count"] or 0) <= 0:
        failures.append(f"nonpositive document_count: {key}")
    if "cooccurrence" not in r["interpretation_note"]:
        warnings.append(f"unsafe interpretation note: {key}")

report = [
    "ShowTrials person-organization matrix validation",
    "",
    f"Rows: {len(rows)}",
    f"Failures: {len(failures)}",
    f"Warnings: {len(warnings)}",
]

if failures:
    report.append("")
    report.append("Failures:")
    report.extend(failures[:50])

if warnings:
    report.append("")
    report.append("Warnings:")
    report.extend(warnings[:50])

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
