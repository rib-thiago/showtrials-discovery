#!/usr/bin/env python3
import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    DOCUMENT_TYPES_V4,
    FAMILY_PROCESS_MATRIX,
    FAMILY_PROCESS_PROFILES,
    LITERAL_PEOPLE,
    LITERAL_PERSON_DOCUMENTS,
    MASTER_CATALOG,
    ORGANIZATIONS,
    ORGANIZATION_DOCUMENTS,
    ORGANIZATION_FAMILIES,
    ORGANIZATION_FAMILY_DOCUMENT_MATRIX,
    ORGANIZATION_HIERARCHY,
    ORGANIZATION_PERSON_SUMMARY,
    ORGANIZATION_PROCESS_MATRIX,
    ORGANIZATION_PROCESS_PROFILES,
    PERSON_ALIASES,
    PERSON_INSTITUTION_PROFILES_V2,
    PERSON_ORGANIZATION_MATRIX,
    PERSON_ORGANIZATION_SUMMARY,
    PERSON_PROCESS_MATRIX,
    PERSON_PROCESS_PROFILES,
    PROCESSES,
    PROCESS_DOCUMENT_MATRIX,
    ROLE_DOCUMENTS_V2,
    ROLES_V2,
    SEMANTIC_LAYER_INVENTORY,
    SEMANTIC_LAYER_REPORT,
    SEMANTIC_LAYER_VALIDATION,
    ensure_parent,
)

FILES = {
    "catalog": MASTER_CATALOG,
    "people": LITERAL_PEOPLE,
    "person_documents": LITERAL_PERSON_DOCUMENTS,
    "person_aliases": PERSON_ALIASES,
    "document_types": DOCUMENT_TYPES_V4,
    "organizations": ORGANIZATIONS,
    "organization_documents": ORGANIZATION_DOCUMENTS,
    "organization_hierarchy": ORGANIZATION_HIERARCHY,
    "organization_families": ORGANIZATION_FAMILIES,
    "organization_family_document_matrix": ORGANIZATION_FAMILY_DOCUMENT_MATRIX,
    "roles_v2": ROLES_V2,
    "role_documents_v2": ROLE_DOCUMENTS_V2,
    "person_organization_matrix": PERSON_ORGANIZATION_MATRIX,
    "person_organization_summary": PERSON_ORGANIZATION_SUMMARY,
    "organization_person_summary": ORGANIZATION_PERSON_SUMMARY,
    "person_context_profiles_v2": PERSON_INSTITUTION_PROFILES_V2,
    "person_process_matrix": PERSON_PROCESS_MATRIX,
    "organization_process_matrix": ORGANIZATION_PROCESS_MATRIX,
    "family_process_matrix": FAMILY_PROCESS_MATRIX,
    "processes": PROCESSES,
    "process_document_matrix": PROCESS_DOCUMENT_MATRIX,
    "person_process_profiles": PERSON_PROCESS_PROFILES,
    "organization_process_profiles": ORGANIZATION_PROCESS_PROFILES,
    "family_process_profiles": FAMILY_PROCESS_PROFILES,
}

REPORT = SEMANTIC_LAYER_REPORT
TSV = SEMANTIC_LAYER_INVENTORY
VALIDATION = SEMANTIC_LAYER_VALIDATION

def load_rows(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def columns(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        return next(reader, [])

inventory = []
validation = []

for name, path in FILES.items():
    exists = path.exists()
    rows = load_rows(path) if exists else []
    cols = columns(path) if exists else []

    inventory.append({
        "layer": name,
        "path": str(path),
        "exists": "yes" if exists else "no",
        "row_count": len(rows),
        "column_count": len(cols),
        "columns": " | ".join(cols),
    })

    if not exists:
        validation.append({
            "level": "FAIL",
            "check": "missing_file",
            "layer": name,
            "detail": str(path),
        })
    elif not cols:
        validation.append({
            "level": "FAIL",
            "check": "missing_header",
            "layer": name,
            "detail": str(path),
        })
    elif len(rows) == 0:
        validation.append({
            "level": "WARN",
            "check": "empty_file",
            "layer": name,
            "detail": str(path),
        })

# Cross-layer checks
catalog = load_rows(FILES["catalog"])
catalog_ids = {r.get("document_post_id", "") for r in catalog if r.get("document_post_id")}

doc_types = load_rows(FILES["document_types"])
doc_type_ids = {r.get("document_post_id", "") for r in doc_types if r.get("document_post_id")}

process_docs = load_rows(FILES["process_document_matrix"])
process_doc_ids = {r.get("document_post_id", "") for r in process_docs if r.get("document_post_id")}

if catalog_ids and doc_type_ids and catalog_ids != doc_type_ids:
    validation.append({
        "level": "FAIL",
        "check": "catalog_vs_document_types_id_mismatch",
        "layer": "document_types",
        "detail": f"catalog={len(catalog_ids)} document_types={len(doc_type_ids)}",
    })

if catalog_ids and process_doc_ids and catalog_ids != process_doc_ids:
    validation.append({
        "level": "FAIL",
        "check": "catalog_vs_process_docs_id_mismatch",
        "layer": "process_document_matrix",
        "detail": f"catalog={len(catalog_ids)} process_docs={len(process_doc_ids)}",
    })

# Interpretation-note safety checks
for layer_name in [
    "person_organization_matrix",
    "person_context_profiles_v2",
    "person_process_profiles",
    "organization_process_profiles",
    "family_process_profiles",
]:
    rows = load_rows(FILES[layer_name])
    if not rows:
        continue

    if "interpretation_note" not in rows[0]:
        validation.append({
            "level": "WARN",
            "check": "missing_interpretation_note_column",
            "layer": layer_name,
            "detail": "",
        })
        continue

    bad = [
        r for r in rows
        if "cooccurrence" not in (r.get("interpretation_note") or "")
    ]
    if bad:
        validation.append({
            "level": "WARN",
            "check": "unsafe_interpretation_note",
            "layer": layer_name,
            "detail": str(len(bad)),
        })

if not validation:
    validation.append({
        "level": "OK",
        "check": "all_checks",
        "layer": "semantic_layer",
        "detail": "passed",
    })

with ensure_parent(TSV).open("w", encoding="utf-8", newline="") as f:
    fields = ["layer", "path", "exists", "row_count", "column_count", "columns"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(inventory)

with ensure_parent(VALIDATION).open("w", encoding="utf-8", newline="") as f:
    fields = ["level", "check", "layer", "detail"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(validation)

failures = sum(1 for r in validation if r["level"] == "FAIL")
warnings = sum(1 for r in validation if r["level"] == "WARN")

report = []
report.append("ShowTrials semantic layer diagnosis")
report.append("")
report.append(f"Files checked: {len(inventory)}")
report.append(f"Failures: {failures}")
report.append(f"Warnings: {warnings}")
report.append("")
report.append("Layer inventory:")
for r in inventory:
    report.append(
        f"{r['layer']}\trows={r['row_count']}\tcols={r['column_count']}\texists={r['exists']}"
    )

report.append("")
report.append("Key counts:")
lookup = {r["layer"]: r for r in inventory}
for key in [
    "catalog",
    "people",
    "person_documents",
    "document_types",
    "organizations",
    "organization_documents",
    "organization_hierarchy",
    "organization_families",
    "roles_v2",
    "person_organization_matrix",
    "processes",
    "process_document_matrix",
    "person_process_matrix",
    "organization_process_matrix",
    "family_process_matrix",
    "person_process_profiles",
]:
    r = lookup.get(key)
    if r:
        report.append(f"{key}: {r['row_count']}")

report.append("")
report.append("Validation:")
for r in validation:
    report.append(f"{r['level']}\t{r['check']}\t{r['layer']}\t{r['detail']}")

report.append("")
report.append("Interpretation policy:")
report.append("Frequency and cooccurrence layers are contextual evidence, not biographical or causal claims.")
report.append("Do not promote centrality metrics to historical interpretation without manual curatorial review.")
report.append("Next recommended front: build a search/query layer that consumes these stable semantic TSVs.")

report.append("")
report.append("Outputs:")
report.append(str(TSV))
report.append(str(VALIDATION))
report.append(str(REPORT))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(TSV)
print(VALIDATION)
print(REPORT)
