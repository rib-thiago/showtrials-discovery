#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    FAMILY_PROCESS_MATRIX,
    MASTER_CATALOG,
    ORGANIZATION_PROCESS_MATRIX,
    PERSON_PROCESS_MATRIX,
    PROCESS_DOCUMENT_MATRIX,
    PROCESS_LAYER_VALIDATION_REPORT,
    PROCESSES,
    ensure_parent,
)

CATALOG = MASTER_CATALOG
PROCESS_DOCS = PROCESS_DOCUMENT_MATRIX
PERSON_PROCESS = PERSON_PROCESS_MATRIX
ORG_PROCESS = ORGANIZATION_PROCESS_MATRIX
FAMILY_PROCESS = FAMILY_PROCESS_MATRIX

REPORT = PROCESS_LAYER_VALIDATION_REPORT

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

catalog = load(CATALOG)
processes = load(PROCESSES)
process_docs = load(PROCESS_DOCS)
person_process = load(PERSON_PROCESS)
org_process = load(ORG_PROCESS)
family_process = load(FAMILY_PROCESS)

failures = []
warnings = []

catalog_ids = {r["document_post_id"] for r in catalog}
process_doc_ids = {r["document_post_id"] for r in process_docs}

if catalog_ids != process_doc_ids:
    failures.append(f"process_doc_ids mismatch: catalog={len(catalog_ids)} process_docs={len(process_doc_ids)}")

process_names = {r["process"] for r in processes}
process_doc_names = {r["process"] for r in process_docs}

if not process_doc_names.issubset(process_names):
    failures.append("process_doc_names contains process absent from processes.tsv")

for name, rows, key_fields in [
    ("person_process", person_process, ("person", "process")),
    ("org_process", org_process, ("organization", "process")),
    ("family_process", family_process, ("organization_family", "process")),
]:
    seen = set()
    for r in rows:
        key = tuple(r[k] for k in key_fields)
        if key in seen:
            failures.append(f"duplicate {name}: {key}")
        seen.add(key)
        if int(r["document_count"] or 0) <= 0:
            failures.append(f"nonpositive document_count in {name}: {key}")

if not processes:
    failures.append("empty processes.tsv")

known_kinds = {
    "major_show_trial", "related_case", "person_dossier",
    "prehistory", "articles", "misc", "other", "unset"
}

for r in processes:
    if r["process_kind"] not in known_kinds:
        warnings.append(f"unknown process_kind: {r['process']} -> {r['process_kind']}")

report = [
    "ShowTrials process layer validation",
    "",
    f"Catalog documents: {len(catalog)}",
    f"Processes: {len(processes)}",
    f"Process-document rows: {len(process_docs)}",
    f"Person-process rows: {len(person_process)}",
    f"Organization-process rows: {len(org_process)}",
    f"Family-process rows: {len(family_process)}",
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
