#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    DOCUMENT_TYPES_V4,
    FAMILY_PROCESS_MATRIX,
    LITERAL_PERSON_DOCUMENTS,
    MASTER_CATALOG,
    ORGANIZATION_DOCUMENTS,
    ORGANIZATION_FAMILY_DOCUMENT_MATRIX,
    ORGANIZATION_PROCESS_MATRIX,
    PERSON_PROCESS_MATRIX,
    PROCESS_DOCUMENT_MATRIX,
    PROCESS_LAYER_REPORT,
    PROCESSES,
    ensure_parent,
)

CATALOG = MASTER_CATALOG
DOC_TYPES = DOCUMENT_TYPES_V4
FAMILY_MATRIX = ORGANIZATION_FAMILY_DOCUMENT_MATRIX
PERSON_DOCS = LITERAL_PERSON_DOCUMENTS
ORG_DOCS = ORGANIZATION_DOCUMENTS

OUT_PROCESSES = PROCESSES
OUT_PROCESS_DOCS = PROCESS_DOCUMENT_MATRIX
OUT_PERSON_PROCESS = PERSON_PROCESS_MATRIX
OUT_ORG_PROCESS = ORGANIZATION_PROCESS_MATRIX
OUT_FAMILY_PROCESS = FAMILY_PROCESS_MATRIX
OUT_REPORT = PROCESS_LAYER_REPORT

PROCESS_KIND_RULES = [
    ("major_show_trial", "ПРОЦЕСС 19-23 АВГУСТА 1936 г."),
    ("major_show_trial", "ПРОЦЕСС 23-29 ЯНВАРЯ 1937 г."),
    ("major_show_trial", "ПРОЦЕСС 2-12 МАРТА 1938 г."),
    ("related_case", "ПРОЦЕСС “МОСКОВСКОГО ЦЕНТРА”"),
    ("related_case", "ПРОЦЕСС “ЛЕНИНГРАДСКОГО ЦЕНТРА”"),
    ("related_case", "КРЕМЛЕВСКОЕ ДЕЛО"),
    ("person_dossier", "БУХАРИН"),
    ("person_dossier", "ТРОЦКИЙ"),
    ("prehistory", "ПРЕДЫСТОРИЯ"),
    ("articles", "СТАТЬИ"),
    ("misc", "РАЗНЫЕ ДОКУМЕНТЫ"),
]

def process_kind(name):
    for kind, token in PROCESS_KIND_RULES:
        if name == token:
            return kind
    if not name or name == "UNSET":
        return "unset"
    return "other"

def load_tsv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

catalog_rows = load_tsv(CATALOG)
doc_types = {r["document_post_id"]: r.get("document_type", "") for r in load_tsv(DOC_TYPES)}

doc_families = defaultdict(set)
for r in load_tsv(FAMILY_MATRIX):
    doc_id = r["document_post_id"]
    for fam in (r.get("organization_families") or "").split(" | "):
        fam = fam.strip()
        if fam:
            doc_families[doc_id].add(fam)

doc_people = defaultdict(set)
for r in load_tsv(PERSON_DOCS):
    doc_people[r["document_post_id"]].add(r["person"])

doc_orgs = defaultdict(set)
for r in load_tsv(ORG_DOCS):
    doc_orgs[r["document_post_id"]].add(r["organization"])

process_docs = defaultdict(list)
for r in catalog_rows:
    proc = r.get("primary_process") or "UNSET"
    process_docs[proc].append(r)

process_rows = []
process_doc_rows = []
person_process_counter = Counter()
person_process_docs = defaultdict(set)
org_process_counter = Counter()
org_process_docs = defaultdict(set)
family_process_counter = Counter()
family_process_docs = defaultdict(set)

for proc, docs in sorted(process_docs.items()):
    kind = process_kind(proc)
    dtype_counter = Counter()
    collection_counter = Counter()
    family_counter = Counter()
    person_counter = Counter()
    org_counter = Counter()
    dates = []
    total_words = 0

    for d in docs:
        doc_id = d["document_post_id"]
        dtype = doc_types.get(doc_id, "unknown")
        collection = d.get("primary_collection") or "UNSET"
        words = int(d.get("content_words") or 0)
        total_words += words

        if d.get("document_date"):
            dates.append(d["document_date"])

        dtype_counter[dtype] += 1
        collection_counter[collection] += 1

        for fam in doc_families.get(doc_id, set()):
            family_counter[fam] += 1
            family_process_counter[(fam, proc)] += 1
            family_process_docs[(fam, proc)].add(doc_id)

        for person in doc_people.get(doc_id, set()):
            person_counter[person] += 1
            person_process_counter[(person, proc)] += 1
            person_process_docs[(person, proc)].add(doc_id)

        for org in doc_orgs.get(doc_id, set()):
            org_counter[org] += 1
            org_process_counter[(org, proc)] += 1
            org_process_docs[(org, proc)].add(doc_id)

        process_doc_rows.append({
            "process": proc,
            "process_kind": kind,
            "document_post_id": doc_id,
            "document_date": d.get("document_date", ""),
            "document_title": d.get("document_title", ""),
            "document_type": dtype,
            "primary_collection": collection,
            "organization_families": " | ".join(sorted(doc_families.get(doc_id, set()))),
            "people_count": len(doc_people.get(doc_id, set())),
            "organization_count": len(doc_orgs.get(doc_id, set())),
            "content_words": d.get("content_words", ""),
            "document_url": d.get("document_url", ""),
        })

    process_rows.append({
        "process": proc,
        "process_kind": kind,
        "document_count": len(docs),
        "total_words": total_words,
        "first_date": min(dates) if dates else "",
        "last_date": max(dates) if dates else "",
        "person_count": len(person_counter),
        "organization_count": len(org_counter),
        "family_count": len(family_counter),
        "document_type_count": len(dtype_counter),
        "collection_count": len(collection_counter),
        "top_people": " | ".join(f"{k}:{v}" for k, v in person_counter.most_common(15)),
        "top_organizations": " | ".join(f"{k}:{v}" for k, v in org_counter.most_common(12)),
        "top_families": " | ".join(f"{k}:{v}" for k, v in family_counter.most_common(8)),
        "top_document_types": " | ".join(f"{k}:{v}" for k, v in dtype_counter.most_common(8)),
        "top_collections": " | ".join(f"{k}:{v}" for k, v in collection_counter.most_common(8)),
    })

with ensure_parent(OUT_PROCESSES).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "process", "process_kind", "document_count", "total_words",
        "first_date", "last_date", "person_count", "organization_count",
        "family_count", "document_type_count", "collection_count",
        "top_people", "top_organizations", "top_families",
        "top_document_types", "top_collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(process_rows, key=lambda r: (-int(r["document_count"]), r["process"])))

with ensure_parent(OUT_PROCESS_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "process", "process_kind", "document_post_id", "document_date",
        "document_title", "document_type", "primary_collection",
        "organization_families", "people_count", "organization_count",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(process_doc_rows, key=lambda r: (r["process"], r["document_date"], r["document_post_id"])))

with ensure_parent(OUT_PERSON_PROCESS).open("w", encoding="utf-8", newline="") as f:
    fields = ["person", "process", "process_kind", "document_count", "documents"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for (person, proc), count in sorted(person_process_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow({
            "person": person,
            "process": proc,
            "process_kind": process_kind(proc),
            "document_count": len(person_process_docs[(person, proc)]),
            "documents": " | ".join(sorted(person_process_docs[(person, proc)])),
        })

with ensure_parent(OUT_ORG_PROCESS).open("w", encoding="utf-8", newline="") as f:
    fields = ["organization", "process", "process_kind", "document_count", "documents"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for (org, proc), count in sorted(org_process_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow({
            "organization": org,
            "process": proc,
            "process_kind": process_kind(proc),
            "document_count": len(org_process_docs[(org, proc)]),
            "documents": " | ".join(sorted(org_process_docs[(org, proc)])),
        })

with ensure_parent(OUT_FAMILY_PROCESS).open("w", encoding="utf-8", newline="") as f:
    fields = ["organization_family", "process", "process_kind", "document_count", "documents"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for (fam, proc), count in sorted(family_process_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow({
            "organization_family": fam,
            "process": proc,
            "process_kind": process_kind(proc),
            "document_count": len(family_process_docs[(fam, proc)]),
            "documents": " | ".join(sorted(family_process_docs[(fam, proc)])),
        })

report = []
report.append("ShowTrials process layer")
report.append("")
report.append(f"Processes: {len(process_rows)}")
report.append(f"Process-document rows: {len(process_doc_rows)}")
report.append(f"Person-process rows: {len(person_process_counter)}")
report.append(f"Organization-process rows: {len(org_process_counter)}")
report.append(f"Family-process rows: {len(family_process_counter)}")
report.append("")
report.append("Processes:")
for r in sorted(process_rows, key=lambda r: (-int(r["document_count"]), r["process"])):
    report.append(
        f"{r['document_count']}\t{r['process_kind']}\t{r['process']}"
        f"\tpeople={r['person_count']}"
        f"\torgs={r['organization_count']}"
        f"\tfamilies={r['family_count']}"
        f"\tdoctypes={r['document_type_count']}"
    )

report.append("")
report.append("Outputs:")
report.append(str(OUT_PROCESSES))
report.append(str(OUT_PROCESS_DOCS))
report.append(str(OUT_PERSON_PROCESS))
report.append(str(OUT_ORG_PROCESS))
report.append(str(OUT_FAMILY_PROCESS))

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PROCESSES)
print(OUT_PROCESS_DOCS)
print(OUT_PERSON_PROCESS)
print(OUT_ORG_PROCESS)
print(OUT_FAMILY_PROCESS)
print(OUT_REPORT)
