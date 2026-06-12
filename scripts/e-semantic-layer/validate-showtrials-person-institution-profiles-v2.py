#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PERSON_INSTITUTION_PROFILES_V2,
    PERSON_INSTITUTION_PROFILES_V2_VALIDATION_REPORT,
    ensure_parent,
)

PROFILES = PERSON_INSTITUTION_PROFILES_V2
REPORT = PERSON_INSTITUTION_PROFILES_V2_VALIDATION_REPORT

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

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
