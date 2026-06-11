#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

FILES = {
    "catalog": BASE / "showtrials_master_catalog.tsv",
    "people": BASE / "showtrials_literal_people.tsv",
    "person_documents": BASE / "showtrials_literal_person_documents.tsv",
    "person_aliases": BASE / "showtrials_person_aliases.tsv",
    "document_types": BASE / "showtrials_document_types_v4.tsv",
    "organizations": BASE / "showtrials_organizations.tsv",
    "organization_documents": BASE / "showtrials_organization_documents.tsv",
    "organization_hierarchy": BASE / "showtrials_organization_hierarchy.tsv",
    "organization_families": BASE / "showtrials_organization_families.tsv",
    "organization_family_document_matrix": BASE / "showtrials_organization_family_document_matrix.tsv",
    "roles_v2": BASE / "showtrials_roles_v2.tsv",
    "role_documents_v2": BASE / "showtrials_role_documents_v2.tsv",
    "person_organization_matrix": BASE / "showtrials_person_organization_matrix.tsv",
    "person_organization_summary": BASE / "showtrials_person_organization_summary.tsv",
    "organization_person_summary": BASE / "showtrials_organization_person_summary.tsv",
    "person_context_profiles_v2": BASE / "showtrials_person_institution_profiles_v2.tsv",
    "person_process_matrix": BASE / "showtrials_person_process_matrix.tsv",
    "organization_process_matrix": BASE / "showtrials_organization_process_matrix.tsv",
    "family_process_matrix": BASE / "showtrials_family_process_matrix.tsv",
    "processes": BASE / "showtrials_processes.tsv",
    "process_document_matrix": BASE / "showtrials_process_document_matrix.tsv",
    "person_process_profiles": BASE / "showtrials_person_process_profiles.tsv",
    "organization_process_profiles": BASE / "showtrials_organization_process_profiles.tsv",
    "family_process_profiles": BASE / "showtrials_family_process_profiles.tsv",
}

REPORT = BASE / "showtrials_semantic_layer_report.txt"
TSV = BASE / "showtrials_semantic_layer_inventory.tsv"
VALIDATION = BASE / "showtrials_semantic_layer_validation.tsv"

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

with TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["layer", "path", "exists", "row_count", "column_count", "columns"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(inventory)

with VALIDATION.open("w", encoding="utf-8", newline="") as f:
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

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(TSV)
print(VALIDATION)
print(REPORT)
