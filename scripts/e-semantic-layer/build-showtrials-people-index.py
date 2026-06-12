#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict, Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ENTITY_CANDIDATES,
    MASTER_CATALOG,
    PEOPLE,
    PEOPLE_INDEX_REPORT,
    PERSON_DOCUMENTS,
    PERSON_PAIRS,
    TITLE_DOCUMENT_ENTITIES,
    TITLE_ENTITY_PAIRS,
    ensure_parent,
)

CANDIDATES = ENTITY_CANDIDATES
DOC_ENTITIES = TITLE_DOCUMENT_ENTITIES
CATALOG = MASTER_CATALOG
PAIRS = TITLE_ENTITY_PAIRS

OUT_PEOPLE = PEOPLE
OUT_PERSON_DOCS = PERSON_DOCUMENTS
OUT_PERSON_PAIRS = PERSON_PAIRS
OUT_REPORT = PEOPLE_INDEX_REPORT

def split_pipe(v):
    return [x.strip() for x in (v or "").split(" | ") if x.strip()]

people = set()
with CANDIDATES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["entity_type"] == "PERSON" and r["confidence"] in {"high", "medium"}:
            people.add(r["entity"])

catalog = {}
with CATALOG.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        catalog[r["document_post_id"]] = r

person_docs = defaultdict(list)
person_processes = defaultdict(set)
person_collections = defaultdict(set)
person_words = Counter()
person_dates = defaultdict(list)

with DOC_ENTITIES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        doc_id = r["document_post_id"]
        meta = catalog.get(doc_id, {})
        words = int(meta.get("content_words") or 0)

        for e in split_pipe(r.get("entities")):
            if e not in people:
                continue

            person_docs[e].append(doc_id)
            person_words[e] += words

            if meta.get("primary_process"):
                person_processes[e].add(meta["primary_process"])
            if meta.get("primary_collection"):
                person_collections[e].add(meta["primary_collection"])
            if meta.get("document_date"):
                person_dates[e].append(meta["document_date"])

with ensure_parent(OUT_PEOPLE).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "document_count", "total_words", "first_date", "last_date",
        "process_count", "processes", "collection_count", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for person, ids in sorted(person_docs.items(), key=lambda x: len(set(x[1])), reverse=True):
        dates = sorted(person_dates[person])
        w.writerow({
            "person": person,
            "document_count": len(set(ids)),
            "total_words": person_words[person],
            "first_date": dates[0] if dates else "",
            "last_date": dates[-1] if dates else "",
            "process_count": len(person_processes[person]),
            "processes": " | ".join(sorted(person_processes[person])),
            "collection_count": len(person_collections[person]),
            "collections": " | ".join(sorted(person_collections[person])),
        })

with ensure_parent(OUT_PERSON_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "document_post_id", "document_date", "document_title",
        "primary_process", "primary_collection", "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for person, ids in sorted(person_docs.items()):
        for doc_id in sorted(set(ids), key=lambda x: catalog.get(x, {}).get("document_date", "")):
            meta = catalog.get(doc_id, {})
            w.writerow({
                "person": person,
                "document_post_id": doc_id,
                "document_date": meta.get("document_date", ""),
                "document_title": meta.get("document_title", ""),
                "primary_process": meta.get("primary_process", ""),
                "primary_collection": meta.get("primary_collection", ""),
                "content_words": meta.get("content_words", ""),
                "document_url": meta.get("document_url", ""),
            })

with ensure_parent(OUT_PERSON_PAIRS).open("w", encoding="utf-8", newline="") as f_out, PAIRS.open("r", encoding="utf-8", newline="") as f_in:
    reader = csv.DictReader(f_in, delimiter="\t")
    fields = ["person_a", "person_b", "document_count"]
    w = csv.DictWriter(f_out, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for r in reader:
        a = r["entity_a"]
        b = r["entity_b"]
        if a in people and b in people:
            w.writerow({
                "person_a": a,
                "person_b": b,
                "document_count": r["document_count"],
            })

report = []
report.append("ShowTrials people index")
report.append("")
report.append(f"People candidates accepted: {len(people)}")
report.append(f"People with documents: {len(person_docs)}")
report.append("")
report.append("Top people:")
for person, ids in sorted(person_docs.items(), key=lambda x: len(set(x[1])), reverse=True)[:80]:
    dates = sorted(person_dates[person])
    report.append(
        f"{len(set(ids))}\t{person_words[person]}\t{dates[0] if dates else ''}\t{dates[-1] if dates else ''}\t{person}"
    )

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PEOPLE)
print(OUT_PERSON_DOCS)
print(OUT_PERSON_PAIRS)
print(OUT_REPORT)
