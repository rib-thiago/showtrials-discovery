#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    TRANSLATION_GLOSSARY_SEEDS_V1,
    TRANSLATION_GLOSSARY_SEEDS_V1_VALIDATION_REPORT,
    ensure_parent,
)

FILE = TRANSLATION_GLOSSARY_SEEDS_V1
REPORT = TRANSLATION_GLOSSARY_SEEDS_V1_VALIDATION_REPORT

rows = list(csv.DictReader(FILE.open("r", encoding="utf-8", newline=""), delimiter="\t"))

failures = []
warnings = []
seen = set()

for r in rows:
    src = r["source_ru"]
    key = (src, r["layer"])
    if not src:
        failures.append("missing source_ru")
    if key in seen:
        failures.append(f"duplicate source/layer: {key}")
    seen.add(key)

    if not r["canonical_en"]:
        warnings.append(f"missing canonical_en: {r['layer']} {src}")

    if r["status"] == "approved" and not r["canonical_en"]:
        failures.append(f"approved without canonical_en: {r['layer']} {src}")

    if r["priority"] not in {"high", "medium", "low"}:
        failures.append(f"bad priority: {r['priority']} {src}")

report = [
    "ShowTrials translation glossary seeds v1 validation",
    "",
    f"Rows: {len(rows)}",
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
