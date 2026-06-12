#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ROLES_V2,
    ROLES_V2_VALIDATION_REPORT,
    ensure_parent,
)

ROLES = ROLES_V2
REPORT = ROLES_V2_VALIDATION_REPORT

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

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
