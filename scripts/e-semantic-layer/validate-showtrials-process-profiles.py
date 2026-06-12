#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    FAMILY_PROCESS_PROFILES,
    ORGANIZATION_PROCESS_PROFILES,
    PERSON_PROCESS_PROFILES,
    PROCESS_PROFILES_VALIDATION_REPORT,
    ensure_parent,
)

FILES = [
    ("person", PERSON_PROCESS_PROFILES),
    ("organization", ORGANIZATION_PROCESS_PROFILES),
    ("organization_family", FAMILY_PROCESS_PROFILES),
]

REPORT = PROCESS_PROFILES_VALIDATION_REPORT

failures = []
warnings = []

for entity_field, path in FILES:
    rows = list(csv.DictReader(path.open("r", encoding="utf-8", newline=""), delimiter="\t"))

    if not rows:
        failures.append(f"empty file: {path.name}")

    seen = set()

    for r in rows:
        entity = r.get(entity_field, "")
        if not entity:
            failures.append(f"missing entity in {path.name}")

        if entity in seen:
            failures.append(f"duplicate entity in {path.name}: {entity}")
        seen.add(entity)

        if int(r.get("total_process_documents") or 0) <= 0:
            failures.append(f"nonpositive total_process_documents in {path.name}: {entity}")

        share = float(r.get("top_process_share") or 0)
        if share <= 0 or share > 1:
            failures.append(f"invalid top_process_share in {path.name}: {entity}={share}")

        if "cooccurrence" not in r.get("interpretation_note", ""):
            warnings.append(f"unsafe interpretation note in {path.name}: {entity}")

report = [
    "ShowTrials process profiles validation",
    "",
    f"Failures: {len(failures)}",
    f"Warnings: {len(warnings)}",
]

if failures:
    report.append("")
    report.append("Failures:")
    report.extend(failures[:80])

if warnings:
    report.append("")
    report.append("Warnings:")
    report.extend(warnings[:80])

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
