#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")

G3 = BASE / "showtrials_translation_glossary_g3.tsv"
REVIEW = BASE / "showtrials_translation_glossary_g3_review.tsv"
REPORT = BASE / "showtrials_translation_glossary_g3_validation_report.txt"
TSV = BASE / "showtrials_translation_glossary_g3_validation.tsv"

rows = list(csv.DictReader(G3.open("r", encoding="utf-8", newline=""), delimiter="\t"))
review_rows = list(csv.DictReader(REVIEW.open("r", encoding="utf-8", newline=""), delimiter="\t"))

checks = []
failures = 0
warnings = 0

def add(level, check, detail):
    global failures, warnings
    checks.append({"level": level, "check": check, "detail": detail})
    if level == "FAIL":
        failures += 1
    elif level == "WARN":
        warnings += 1

seen = set()
for r in rows:
    key = (r["source_ru"], r["layer"])
    if key in seen:
        add("FAIL", "duplicate_source_layer", f"{r['layer']} {r['source_ru']}")
    seen.add(key)

    if not r["source_ru"]:
        add("FAIL", "missing_source_ru", r["layer"])

    if r["status"] == "approved" and not r["canonical_en"]:
        add("FAIL", "approved_without_canonical", f"{r['layer']} {r['source_ru']}")

    if r["layer"] in {"organizations", "processes"} and r["status"] != "approved":
        add("FAIL", "org_or_process_not_approved", f"{r['layer']} {r['source_ru']}")

    if r["layer"] == "people" and int(r.get("person_document_count") or r.get("source_count") or 0) >= 20 and r["status"] != "approved":
        add("WARN", "high_frequency_person_not_approved", f"{r['source_ru']} {r['canonical_en']}")

review_keys = {(r["source_ru"], r["layer"]) for r in review_rows}
for r in rows:
    if r["g3_review_reason"] and (r["source_ru"], r["layer"]) not in review_keys:
        add("FAIL", "review_reason_missing_from_review_file", f"{r['layer']} {r['source_ru']}")

if not checks:
    add("OK", "all_checks", "passed")

with TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["level", "check", "detail"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(checks)

by_status = Counter(r["status"] for r in rows)
by_layer = Counter(r["layer"] for r in rows)

report = [
    "ShowTrials translation glossary G3 validation",
    "",
    f"Rows: {len(rows)}",
    f"Review rows: {len(review_rows)}",
    f"Failures: {failures}",
    f"Warnings: {warnings}",
    "",
    "Rows by layer:",
]
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Validation rows:")
for c in checks[:120]:
    report.append(f"{c['level']}\t{c['check']}\t{c['detail']}")

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)
