#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict, Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    DOCUMENT_TYPES_V4,
    LITERAL_PEOPLE,
    LITERAL_PERSON_DOCUMENTS,
    MASTER_CATALOG,
    ORGANIZATION_DOCUMENTS,
    ORGANIZATION_FAMILY_DOCUMENT_MATRIX,
    PERSON_CENTRALITY,
    PERSON_CENTRALITY_REPORT,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
PERSON_DOCS = LITERAL_PERSON_DOCUMENTS
ORG_DOCS = ORGANIZATION_DOCUMENTS
FAMILY_MATRIX = ORGANIZATION_FAMILY_DOCUMENT_MATRIX
DOC_TYPES = DOCUMENT_TYPES_V4
CATALOG = MASTER_CATALOG

OUT = PERSON_CENTRALITY
OUT_REPORT = PERSON_CENTRALITY_REPORT

def load_tsv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

people = {r["person"]: r for r in load_tsv(PEOPLE)}
catalog = {r["document_post_id"]: r for r in load_tsv(CATALOG)}
doc_types = {r["document_post_id"]: r.get("document_type", "") for r in load_tsv(DOC_TYPES)}

person_docs = defaultdict(set)
for r in load_tsv(PERSON_DOCS):
    person_docs[r["person"]].add(r["document_post_id"])

doc_orgs = defaultdict(set)
for r in load_tsv(ORG_DOCS):
    doc_orgs[r["document_post_id"]].add(r["organization"])

doc_families = defaultdict(set)
for r in load_tsv(FAMILY_MATRIX):
    for fam in (r.get("organization_families") or "").split(" | "):
        fam = fam.strip()
        if fam:
            doc_families[r["document_post_id"]].add(fam)

rows = []

for person, docs in person_docs.items():
    orgs = set()
    families = set()
    processes = set()
    collections = set()
    doctypes = set()

    process_counter = Counter()
    collection_counter = Counter()
    doctype_counter = Counter()
    family_counter = Counter()
    org_counter = Counter()

    dated_docs = []

    for doc_id in docs:
        meta = catalog.get(doc_id, {})
        date = meta.get("document_date", "")
        if date:
            dated_docs.append(date)

        proc = meta.get("primary_process") or "UNSET"
        coll = meta.get("primary_collection") or "UNSET"
        dtype = doc_types.get(doc_id, "unknown")

        processes.add(proc)
        collections.add(coll)
        doctypes.add(dtype)

        process_counter[proc] += 1
        collection_counter[coll] += 1
        doctype_counter[dtype] += 1

        for org in doc_orgs.get(doc_id, set()):
            orgs.add(org)
            org_counter[org] += 1

        for fam in doc_families.get(doc_id, set()):
            families.add(fam)
            family_counter[fam] += 1

    doc_count = len(docs)
    organization_diversity = len(orgs)
    family_diversity = len(families)
    process_diversity = len(processes)
    collection_diversity = len(collections)
    document_type_diversity = len(doctypes)

    institutional_breadth_score = (
        organization_diversity
        + family_diversity * 3
        + process_diversity * 2
        + collection_diversity
        + document_type_diversity
    )

    centrality_score = (
        doc_count
        + organization_diversity * 5
        + family_diversity * 10
        + process_diversity * 8
        + collection_diversity * 3
        + document_type_diversity * 4
    )

    rows.append({
        "person": person,
        "document_count": doc_count,
        "total_words": people.get(person, {}).get("total_words", ""),
        "first_date": min(dated_docs) if dated_docs else people.get(person, {}).get("first_date", ""),
        "last_date": max(dated_docs) if dated_docs else people.get(person, {}).get("last_date", ""),
        "organization_diversity": organization_diversity,
        "family_diversity": family_diversity,
        "process_diversity": process_diversity,
        "collection_diversity": collection_diversity,
        "document_type_diversity": document_type_diversity,
        "institutional_breadth_score": institutional_breadth_score,
        "centrality_score": centrality_score,
        "top_families": " | ".join(f"{k}:{v}" for k, v in family_counter.most_common(8)),
        "top_organizations": " | ".join(f"{k}:{v}" for k, v in org_counter.most_common(10)),
        "top_processes": " | ".join(f"{k}:{v}" for k, v in process_counter.most_common(8)),
        "top_collections": " | ".join(f"{k}:{v}" for k, v in collection_counter.most_common(8)),
        "top_document_types": " | ".join(f"{k}:{v}" for k, v in doctype_counter.most_common(8)),
        "interpretation_note": "centrality_metrics_from_document_cooccurrence_not_biographical_claim",
    })

rows = sorted(rows, key=lambda r: (-r["centrality_score"], -r["document_count"], r["person"]))

with ensure_parent(OUT).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "document_count", "total_words", "first_date", "last_date",
        "organization_diversity", "family_diversity", "process_diversity",
        "collection_diversity", "document_type_diversity",
        "institutional_breadth_score", "centrality_score",
        "top_families", "top_organizations", "top_processes",
        "top_collections", "top_document_types", "interpretation_note"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials person centrality")
report.append("")
report.append(f"People: {len(rows)}")
report.append("")
report.append("Top by centrality_score:")
for r in rows[:50]:
    report.append(
        f"{r['centrality_score']}\tdocs={r['document_count']}"
        f"\torgs={r['organization_diversity']}"
        f"\tfamilies={r['family_diversity']}"
        f"\tprocesses={r['process_diversity']}"
        f"\tcollections={r['collection_diversity']}"
        f"\tdoctypes={r['document_type_diversity']}"
        f"\t{r['person']}"
    )

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(OUT_REPORT)
