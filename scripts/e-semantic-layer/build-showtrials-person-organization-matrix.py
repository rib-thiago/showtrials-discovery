#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/tmp/showtrials-discovery")

PERSON_DOCS = BASE / "showtrials_literal_person_documents.tsv"
ORG_DOCS = BASE / "showtrials_organization_documents.tsv"
FAMILIES = BASE / "showtrials_organization_families.tsv"
CATALOG = BASE / "showtrials_master_catalog.tsv"
DOC_TYPES = BASE / "showtrials_document_types_v4.tsv"

OUT_MATRIX = BASE / "showtrials_person_organization_matrix.tsv"
OUT_PERSON_SUMMARY = BASE / "showtrials_person_organization_summary.tsv"
OUT_ORG_SUMMARY = BASE / "showtrials_organization_person_summary.tsv"
OUT_REPORT = BASE / "showtrials_person_organization_matrix_report.txt"

def load_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

catalog = {r["document_post_id"]: r for r in load_tsv(CATALOG)}
doc_types = {r["document_post_id"]: r.get("document_type", "") for r in load_tsv(DOC_TYPES)}
org_family = {r["organization"]: r["organization_family"] for r in load_tsv(FAMILIES)}

doc_people = defaultdict(set)
person_total_docs = Counter()

for r in load_tsv(PERSON_DOCS):
    doc_id = r["document_post_id"]
    person = r["person"]
    doc_people[doc_id].add(person)
    person_total_docs[person] += 1

doc_orgs = defaultdict(set)
org_total_docs = Counter()

for r in load_tsv(ORG_DOCS):
    doc_id = r["document_post_id"]
    org = r["organization"]
    doc_orgs[doc_id].add(org)
    org_total_docs[org] += 1

pair_docs = defaultdict(set)
pair_processes = defaultdict(Counter)
pair_collections = defaultdict(Counter)
pair_doc_types = defaultdict(Counter)

for doc_id, people in doc_people.items():
    orgs = doc_orgs.get(doc_id, set())
    if not orgs:
        continue

    meta = catalog.get(doc_id, {})
    process = meta.get("primary_process") or "UNSET"
    collection = meta.get("primary_collection") or "UNSET"
    dtype = doc_types.get(doc_id, "unknown")

    for person in people:
        for org in orgs:
            key = (person, org)
            pair_docs[key].add(doc_id)
            pair_processes[key][process] += 1
            pair_collections[key][collection] += 1
            pair_doc_types[key][dtype] += 1

matrix_rows = []

for (person, org), docs in pair_docs.items():
    p_total = person_total_docs[person]
    o_total = org_total_docs[org]
    count = len(docs)

    matrix_rows.append({
        "person": person,
        "organization": org,
        "organization_family": org_family.get(org, "unclassified"),
        "document_count": count,
        "person_total_documents": p_total,
        "organization_total_documents": o_total,
        "share_of_person_documents": round(count / p_total, 4) if p_total else 0,
        "share_of_organization_documents": round(count / o_total, 4) if o_total else 0,
        "association_weight": round(
            (count / p_total if p_total else 0)
            * (count / o_total if o_total else 0)
            * count,
            6
        ),
        "top_processes": " | ".join(f"{k}:{v}" for k, v in pair_processes[(person, org)].most_common(5)),
        "top_collections": " | ".join(f"{k}:{v}" for k, v in pair_collections[(person, org)].most_common(5)),
        "top_document_types": " | ".join(f"{k}:{v}" for k, v in pair_doc_types[(person, org)].most_common(5)),
        "documents": " | ".join(sorted(docs)),
        "interpretation_note": "document_cooccurrence_not_direct_affiliation_claim",
    })

matrix_rows = sorted(
    matrix_rows,
    key=lambda r: (-int(r["document_count"]), -float(r["association_weight"]), r["person"], r["organization"])
)

with OUT_MATRIX.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "organization", "organization_family",
        "document_count", "person_total_documents", "organization_total_documents",
        "share_of_person_documents", "share_of_organization_documents",
        "association_weight",
        "top_processes", "top_collections", "top_document_types",
        "documents", "interpretation_note"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(matrix_rows)

person_summary = defaultdict(list)
org_summary = defaultdict(list)

for r in matrix_rows:
    person_summary[r["person"]].append(r)
    org_summary[r["organization"]].append(r)

with OUT_PERSON_SUMMARY.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "organization_count", "top_organizations",
        "top_families", "total_pair_document_sum"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for person, rows in sorted(person_summary.items(), key=lambda x: (-sum(int(r["document_count"]) for r in x[1]), x[0])):
        family_counter = Counter()
        for r in rows:
            family_counter[r["organization_family"]] += int(r["document_count"])

        top_orgs = " | ".join(
            f"{r['organization']}:{r['document_count']}"
            for r in sorted(rows, key=lambda x: (-int(x["document_count"]), x["organization"]))[:10]
        )

        w.writerow({
            "person": person,
            "organization_count": len(rows),
            "top_organizations": top_orgs,
            "top_families": " | ".join(f"{k}:{v}" for k, v in family_counter.most_common(8)),
            "total_pair_document_sum": sum(int(r["document_count"]) for r in rows),
        })

with OUT_ORG_SUMMARY.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "organization", "organization_family", "person_count",
        "top_people", "total_pair_document_sum"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for org, rows in sorted(org_summary.items(), key=lambda x: (-sum(int(r["document_count"]) for r in x[1]), x[0])):
        top_people = " | ".join(
            f"{r['person']}:{r['document_count']}"
            for r in sorted(rows, key=lambda x: (-int(x["document_count"]), x["person"]))[:15]
        )

        w.writerow({
            "organization": org,
            "organization_family": org_family.get(org, "unclassified"),
            "person_count": len(rows),
            "top_people": top_people,
            "total_pair_document_sum": sum(int(r["document_count"]) for r in rows),
        })

report = []
report.append("ShowTrials person-organization matrix")
report.append("")
report.append(f"Person-organization pairs: {len(matrix_rows)}")
report.append(f"People with organizations: {len(person_summary)}")
report.append(f"Organizations with people: {len(org_summary)}")
report.append("")
report.append("Top person-organization pairs:")
for r in matrix_rows[:50]:
    report.append(
        f"{r['document_count']}\tweight={r['association_weight']}"
        f"\t{r['person']}\t→\t{r['organization']}"
        f"\t{r['organization_family']}"
    )

report.append("")
report.append("Top organizations by person-pair volume:")
for org, rows in sorted(org_summary.items(), key=lambda x: (-sum(int(r["document_count"]) for r in x[1]), x[0]))[:30]:
    report.append(
        f"{sum(int(r['document_count']) for r in rows)}"
        f"\tpeople={len(rows)}\t{org}\t{org_family.get(org, 'unclassified')}"
    )

report.append("")
report.append("Outputs:")
report.append(str(OUT_MATRIX))
report.append(str(OUT_PERSON_SUMMARY))
report.append(str(OUT_ORG_SUMMARY))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_MATRIX)
print(OUT_PERSON_SUMMARY)
print(OUT_ORG_SUMMARY)
print(OUT_REPORT)
