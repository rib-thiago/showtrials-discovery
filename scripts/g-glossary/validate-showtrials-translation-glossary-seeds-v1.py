#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")
FILE = BASE / "showtrials_translation_glossary_seeds_v1.tsv"
REPORT = BASE / "showtrials_translation_glossary_seeds_v1_validation_report.txt"

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

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(REPORT)
