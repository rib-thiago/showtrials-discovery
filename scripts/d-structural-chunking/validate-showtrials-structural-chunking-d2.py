#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/srv/projects/showtrials-discovery")

CATALOG = BASE / "showtrials_master_catalog.tsv"
DOCS = BASE / "showtrials_structural_chunking_d2_by_document.tsv"
TYPES = BASE / "showtrials_structural_chunking_d2_by_type.tsv"

REPORT = BASE / "showtrials_structural_chunking_d2_validation_report.txt"
TSV = BASE / "showtrials_structural_chunking_d2_validation.tsv"

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

catalog = load(CATALOG)
docs = load(DOCS)
types = load(TYPES)

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

if len(catalog) != len(docs):
    add("FAIL", "row_count_mismatch", f"catalog={len(catalog)} docs={len(docs)}")

if not types:
    add("FAIL", "missing_type_rows", "no D2 type rows")

low_types = [r for r in types if int(r["low_confidence_docs"] or 0) == int(r["documents"] or 0)]
for r in low_types:
    add("WARN", "all_low_confidence_type", r["document_type"])

if not checks:
    add("OK", "all_checks", "passed")

with TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["level", "check", "detail"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(checks)

report = [
    "ShowTrials D2 structural chunking validation",
    "",
    f"Catalog rows: {len(catalog)}",
    f"D2 document rows: {len(docs)}",
    f"D2 type rows: {len(types)}",
    f"Failures: {failures}",
    f"Warnings: {warnings}",
    "",
    "Validation rows:",
]
for c in checks[:120]:
    report.append(f"{c['level']}\t{c['check']}\t{c['detail']}")

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)
