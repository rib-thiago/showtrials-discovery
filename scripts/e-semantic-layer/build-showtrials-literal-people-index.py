#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/tmp/showtrials-discovery")

ALIASES = BASE / "showtrials_person_aliases.tsv"
PERSON_DOCS = BASE / "showtrials_person_documents.tsv"
PERSON_PAIRS = BASE / "showtrials_person_pairs.tsv"

OUT_PEOPLE = BASE / "showtrials_literal_people.tsv"
OUT_DOCS = BASE / "showtrials_literal_person_documents.tsv"
OUT_PAIRS = BASE / "showtrials_literal_person_pairs.tsv"
OUT_REPORT = BASE / "showtrials_literal_people_report.txt"

raw_to_canon = {}
with ALIASES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        raw_to_canon[r["raw_person"]] = r["canonical_person"]

person_docs = defaultdict(dict)
person_words = Counter()
person_dates = defaultdict(list)
person_processes = defaultdict(set)
person_collections = defaultdict(set)
raw_forms = defaultdict(set)

with PERSON_DOCS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        raw = r["person"]
        canon = raw_to_canon.get(raw, raw)
        doc_id = r["document_post_id"]

        person_docs[canon][doc_id] = r
        raw_forms[canon].add(raw)

for canon, docs in person_docs.items():
    for r in docs.values():
        person_words[canon] += int(r.get("content_words") or 0)
        if r.get("document_date"):
            person_dates[canon].append(r["document_date"])
        if r.get("primary_process"):
            person_processes[canon].add(r["primary_process"])
        if r.get("primary_collection"):
            person_collections[canon].add(r["primary_collection"])

with OUT_PEOPLE.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "raw_forms", "document_count", "total_words",
        "first_date", "last_date", "process_count", "processes",
        "collection_count", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    for person, docs in sorted(person_docs.items(), key=lambda x: len(x[1]), reverse=True):
        dates = sorted(person_dates[person])
        w.writerow({
            "person": person,
            "raw_forms": " | ".join(sorted(raw_forms[person])),
            "document_count": len(docs),
            "total_words": person_words[person],
            "first_date": dates[0] if dates else "",
            "last_date": dates[-1] if dates else "",
            "process_count": len(person_processes[person]),
            "processes": " | ".join(sorted(person_processes[person])),
            "collection_count": len(person_collections[person]),
            "collections": " | ".join(sorted(person_collections[person])),
        })

with OUT_DOCS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "raw_person", "document_post_id", "document_date",
        "document_title", "primary_process", "primary_collection",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()

    with PERSON_DOCS.open("r", encoding="utf-8", newline="") as f_in:
        for r in csv.DictReader(f_in, delimiter="\t"):
            raw = r["person"]
            w.writerow({
                "person": raw_to_canon.get(raw, raw),
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
        pair_counts[tuple(sorted([a, b]))] += int(r.get("document_count") or 0)

with OUT_PAIRS.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["person_a", "person_b", "document_count"])
    for (a, b), count in sorted(pair_counts.items(), key=lambda x: x[1], reverse=True):
        w.writerow([a, b, count])

report = []
report.append("ShowTrials literal people index")
report.append("")
report.append(f"People: {len(person_docs)}")
report.append("")
report.append("Top people:")
for person, docs in sorted(person_docs.items(), key=lambda x: len(x[1]), reverse=True)[:100]:
    dates = sorted(person_dates[person])
    report.append(
        f"{len(docs)}\t{person_words[person]}\t{dates[0] if dates else ''}\t{dates[-1] if dates else ''}\t{person}\tRAW={'; '.join(sorted(raw_forms[person]))}"
    )

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PEOPLE)
print(OUT_DOCS)
print(OUT_PAIRS)
print(OUT_REPORT)
