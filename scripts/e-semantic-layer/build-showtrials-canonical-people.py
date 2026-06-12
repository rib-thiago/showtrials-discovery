#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict, Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    CANONICAL_PEOPLE,
    CANONICAL_PEOPLE_REPORT,
    CANONICAL_PERSON_DOCUMENTS,
    CANONICAL_PERSON_PAIRS,
    PERSON_DOCUMENTS,
    PERSON_NORMALIZATION_CANDIDATES,
    PERSON_PAIRS as PERSON_PAIRS_PATH,
    ensure_parent,
)

MAP = PERSON_NORMALIZATION_CANDIDATES
PERSON_DOCS = PERSON_DOCUMENTS
PERSON_PAIRS = PERSON_PAIRS_PATH

OUT_PEOPLE = CANONICAL_PEOPLE
OUT_DOCS = CANONICAL_PERSON_DOCUMENTS
OUT_PAIRS = CANONICAL_PERSON_PAIRS
OUT_REPORT = CANONICAL_PEOPLE_REPORT

raw_to_canon = {}
with MAP.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        raw_to_canon[r["raw_person"]] = r["canonical_person"]

person_docs = defaultdict(dict)
person_processes = defaultdict(set)
person_collections = defaultdict(set)
person_words = Counter()
person_dates = defaultdict(list)
raw_forms = defaultdict(set)

with PERSON_DOCS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        raw = r["person"]
        canon = raw_to_canon.get(raw, raw)

        doc_id = r["document_post_id"]
        person_docs[canon][doc_id] = r
        raw_forms[canon].add(raw)

for canon, docs in person_docs.items():
    for doc_id, r in docs.items():
        words = int(r.get("content_words") or 0)
        person_words[canon] += words
        if r.get("document_date"):
            person_dates[canon].append(r["document_date"])
        if r.get("primary_process"):
            person_processes[canon].add(r["primary_process"])
        if r.get("primary_collection"):
            person_collections[canon].add(r["primary_collection"])

with ensure_parent(OUT_PEOPLE).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "canonical_person", "raw_forms", "document_count", "total_words",
        "first_date", "last_date", "process_count", "processes",
        "collection_count", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for canon, docs in sorted(person_docs.items(), key=lambda x: len(x[1]), reverse=True):
        dates = sorted(person_dates[canon])
        w.writerow({
            "canonical_person": canon,
            "raw_forms": " | ".join(sorted(raw_forms[canon])),
            "document_count": len(docs),
            "total_words": person_words[canon],
            "first_date": dates[0] if dates else "",
            "last_date": dates[-1] if dates else "",
            "process_count": len(person_processes[canon]),
            "processes": " | ".join(sorted(person_processes[canon])),
            "collection_count": len(person_collections[canon]),
            "collections": " | ".join(sorted(person_collections[canon])),
        })

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "canonical_person", "raw_person", "document_post_id", "document_date",
        "document_title", "primary_process", "primary_collection",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    with PERSON_DOCS.open("r", encoding="utf-8", newline="") as f_in:
        for r in csv.DictReader(f_in, delimiter="\t"):
            raw = r["person"]
            canon = raw_to_canon.get(raw, raw)
            w.writerow({
                "canonical_person": canon,
                "raw_person": raw,
                "document_post_id": r["document_post_id"],
                "document_date": r["document_date"],
                "document_title": r["document_title"],
                "primary_process": r["primary_process"],
                "primary_collection": r["primary_collection"],
                "content_words": r["content_words"],
                "document_url": r["document_url"],
            })

pair_counts = Counter()
with PERSON_PAIRS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        a = raw_to_canon.get(r["person_a"], r["person_a"])
        b = raw_to_canon.get(r["person_b"], r["person_b"])
        if a == b:
            continue
        key = tuple(sorted([a, b]))
        pair_counts[key] += int(r.get("document_count") or 0)

with ensure_parent(OUT_PAIRS).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["canonical_person_a", "canonical_person_b", "document_count"])
    for (a, b), count in sorted(pair_counts.items(), key=lambda x: x[1], reverse=True):
        w.writerow([a, b, count])

report = []
report.append("ShowTrials canonical people index")
report.append("")
report.append(f"Canonical people: {len(person_docs)}")
report.append("")
report.append("Top canonical people:")
for canon, docs in sorted(person_docs.items(), key=lambda x: len(x[1]), reverse=True)[:100]:
    dates = sorted(person_dates[canon])
    report.append(
        f"{len(docs)}\t{person_words[canon]}\t{dates[0] if dates else ''}\t{dates[-1] if dates else ''}\t{canon}\tRAW={'; '.join(sorted(raw_forms[canon]))}"
    )

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PEOPLE)
print(OUT_DOCS)
print(OUT_PAIRS)
print(OUT_REPORT)
