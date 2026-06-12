#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PERSON_CENTRALITY,
    PERSON_CENTRALITY_VALIDATION_REPORT,
    ensure_parent,
)

FILE = PERSON_CENTRALITY
REPORT = PERSON_CENTRALITY_VALIDATION_REPORT

rows = list(csv.DictReader(FILE.open("r", encoding="utf-8", newline=""), delimiter="\t"))

failures = []
warnings = []

for r in rows:
    if not r["person"]:
        failures.append("missing person")
    if int(r["document_count"] or 0) <= 0:
        failures.append(f"nonpositive document_count: {r.get('person')}")
    if "cooccurrence" not in r["interpretation_note"]:
        warnings.append(f"unsafe interpretation_note: {r.get('person')}")

scores = [int(r["centrality_score"]) for r in rows]
if scores != sorted(scores, reverse=True):
    warnings.append("rows are not sorted by descending centrality_score")

report = [
    "ShowTrials person centrality validation",
    "",
    f"People: {len(rows)}",
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
