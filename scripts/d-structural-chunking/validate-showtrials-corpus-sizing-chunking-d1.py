#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

CATALOG = BASE / "showtrials_master_catalog.tsv"
DOCS = BASE / "showtrials_corpus_sizing_by_document_d1.tsv"
TYPES = BASE / "showtrials_corpus_sizing_by_document_type_d1.tsv"
PROCESSES = BASE / "showtrials_corpus_sizing_by_process_d1.tsv"
POLICY = BASE / "showtrials_chunking_policy_recommendations_d1.tsv"

REPORT = BASE / "showtrials_corpus_sizing_chunking_d1_validation_report.txt"
TSV = BASE / "showtrials_corpus_sizing_chunking_d1_validation.tsv"

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

catalog = load(CATALOG)
docs = load(DOCS)
types = load(TYPES)
processes = load(PROCESSES)
policy = load(POLICY)

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

catalog_chars = sum(int(r.get("content_chars") or 0) for r in catalog)
doc_chars = sum(int(r.get("content_chars") or 0) for r in docs)

if catalog_chars != doc_chars:
    add("FAIL", "char_sum_mismatch", f"catalog={catalog_chars} docs={doc_chars}")

if not types:
    add("FAIL", "missing_type_summary", "no document type summary rows")

if not processes:
    add("FAIL", "missing_process_summary", "no process summary rows")

if not policy:
    add("FAIL", "missing_policy", "no chunking policy rows")

for r in policy:
    if r["profile_strategy"] == "missing_profile":
        add("WARN", "missing_profile", r["document_type"])

for r in docs:
    if int(r["estimated_chunks_by_profile_target"] or 0) <= 0 and int(r["content_chars"] or 0) > 0:
        add("FAIL", "nonpositive_chunk_estimate", r["document_post_id"])

if not checks:
    add("OK", "all_checks", "passed")

with TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["level", "check", "detail"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(checks)

report = [
    "ShowTrials D1 corpus sizing + chunking validation",
    "",
    f"Catalog rows: {len(catalog)}",
    f"Document sizing rows: {len(docs)}",
    f"Document type rows: {len(types)}",
    f"Process rows: {len(processes)}",
    f"Policy rows: {len(policy)}",
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
