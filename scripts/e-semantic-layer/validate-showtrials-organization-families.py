#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

FILE = BASE / "showtrials_organization_families.tsv"

REPORT = BASE / "showtrials_organization_families_validation_report.txt"

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

Path(REPORT).write_text(
    "\n".join(report) + "\n",
    encoding="utf-8"
)

print(REPORT)
