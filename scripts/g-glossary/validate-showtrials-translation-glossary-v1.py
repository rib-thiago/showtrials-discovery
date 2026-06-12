#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    TRANSLATION_GLOSSARY_V1,
    TRANSLATION_GLOSSARY_V1_REVIEW,
    TRANSLATION_GLOSSARY_V1_VALIDATION_REPORT,
    ensure_parent,
)

GLOSSARY = TRANSLATION_GLOSSARY_V1
REVIEW = TRANSLATION_GLOSSARY_V1_REVIEW
REPORT = TRANSLATION_GLOSSARY_V1_VALIDATION_REPORT

rows = list(csv.DictReader(GLOSSARY.open("r", encoding="utf-8", newline=""), delimiter="\t"))
review_rows = list(csv.DictReader(REVIEW.open("r", encoding="utf-8", newline=""), delimiter="\t"))

failures = []
warnings = []
seen = set()

for r in rows:
    key = (r["source_ru"], r["layer"])
    if key in seen:
        failures.append(f"duplicate source/layer: {key}")
    seen.add(key)

    if not r["source_ru"]:
        failures.append("missing source_ru")

    if r["status"] == "approved" and not r["canonical_en"]:
        failures.append(f"approved without canonical_en: {r['source_ru']}")

    if not r["canonical_en"]:
        warnings.append(f"missing canonical_en: {r['layer']} {r['source_ru']}")

    if r["priority"] == "high" and r["layer"] in {"organizations", "processes"} and r["status"] != "approved":
        failures.append(f"high priority org/process not approved: {r['source_ru']}")

review_keys = {(r["source_ru"], r["layer"]) for r in review_rows}
for r in rows:
    if r["review_reason"] and (r["source_ru"], r["layer"]) not in review_keys:
        failures.append(f"review_reason not in review file: {r['source_ru']}")

report = [
    "ShowTrials translation glossary v1 validation",
    "",
    f"Glossary rows: {len(rows)}",
    f"Review rows: {len(review_rows)}",
    f"Failures: {len(failures)}",
    f"Warnings: {len(warnings)}",
]

if failures:
    report.append("")
    report.append("Failures:")
    report.extend(failures[:100])

if warnings:
    report.append("")
    report.append("Warnings:")
    report.extend(warnings[:100])

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
