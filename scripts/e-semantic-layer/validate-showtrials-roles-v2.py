#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")
ROLES = BASE / "showtrials_roles_v2.tsv"
REPORT = BASE / "showtrials_roles_v2_validation_report.txt"

rows = list(csv.DictReader(ROLES.open("r", encoding="utf-8", newline=""), delimiter="\t"))

failures = []
warnings = []

for r in rows:
    if not r["role"]:
        failures.append("missing role")
    if not r["role_class"]:
        failures.append(f"missing class: {r.get('role')}")
    if r["role_class"] == "unclassified":
        warnings.append(f"unclassified: {r['role']}")

report = [
    "ShowTrials roles v2 validation",
    "",
    f"Roles: {len(rows)}",
    f"Failures: {len(failures)}",
    f"Warnings: {len(warnings)}",
]

if warnings:
    report.append("")
    report.append("Warnings:")
    report.extend(warnings)

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
