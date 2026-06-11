#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")
MATRIX = BASE / "showtrials_person_organization_matrix.tsv"
REPORT = BASE / "showtrials_person_organization_matrix_validation_report.txt"

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

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
