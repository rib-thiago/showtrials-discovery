#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")
PROFILES = BASE / "showtrials_person_institution_profiles_v2.tsv"
REPORT = BASE / "showtrials_person_institution_profiles_v2_validation_report.txt"

rows = list(csv.DictReader(PROFILES.open("r", encoding="utf-8", newline=""), delimiter="\t"))

failures = []
warnings = []

for r in rows:
    if not r["person"]:
        failures.append("missing person")
    if not r["interpretation_note"]:
        failures.append(f"missing interpretation note: {r.get('person')}")
    if "cooccurrence" not in r["interpretation_note"]:
        warnings.append(f"interpretation note may be unsafe: {r.get('person')}")

report = [
    "ShowTrials person institution profiles v2 validation",
    "",
    f"People: {len(rows)}",
    f"Failures: {len(failures)}",
    f"Warnings: {len(warnings)}",
]

if failures:
    report.append("")
    report.append("Failures:")
    report.extend(failures)

if warnings:
    report.append("")
    report.append("Warnings:")
    report.extend(warnings[:50])

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
