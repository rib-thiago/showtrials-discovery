#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ORGANIZATION_FAMILIES,
    ORGANIZATION_FAMILIES_VALIDATION_REPORT,
    ensure_parent,
)

FILE = ORGANIZATION_FAMILIES

REPORT = ORGANIZATION_FAMILIES_VALIDATION_REPORT

rows = []

with FILE.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

failures = []
warnings = []

for r in rows:
    if not r["organization"]:
        failures.append("missing organization")

    if not r["organization_family"]:
        failures.append(
            f"missing family: {r['organization']}"
        )

unclassified = [
    r for r in rows
    if r["organization_family"] == "unclassified"
]

if unclassified:
    warnings.append(
        f"unclassified organizations: {len(unclassified)}"
    )

report = []
report.append("ShowTrials organization families validation")
report.append("")
report.append(f"Organizations: {len(rows)}")
report.append(f"Failures: {len(failures)}")
report.append(f"Warnings: {len(warnings)}")

if warnings:
    report.append("")
    report.append("Warnings:")
    report.extend(warnings)

ensure_parent(REPORT).write_text(
    "\n".join(report) + "\n",
    encoding="utf-8"
)

print(REPORT)
