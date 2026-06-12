#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    MASTER_CATALOG,
    TAXONOMY_DOCUMENT_MATRIX,
    TAXONOMY_REPORT,
    TAXONOMY_TERMS,
    ensure_parent,
)

CATALOG = MASTER_CATALOG

OUT_TERMS = TAXONOMY_TERMS
OUT_DOCS = TAXONOMY_DOCUMENT_MATRIX
OUT_REPORT = TAXONOMY_REPORT

def split_pipe(v):
    return [x.strip() for x in (v or "").split(" | ") if x.strip()]

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

terms = defaultdict(Counter)
term_words = defaultdict(Counter)

doc_rows = []

for d in docs:
    words = int(d.get("content_words") or 0)

    fields = {
        "process": split_pipe(d.get("all_processes")) or ([d.get("primary_process")] if d.get("primary_process") else []),
        "collection": split_pipe(d.get("all_collections")) or ([d.get("primary_collection")] if d.get("primary_collection") else []),
        "category": split_pipe(d.get("category_names")),
        "tag": split_pipe(d.get("tag_names")),
    }

    for scope, values in fields.items():
        for v in values:
            terms[scope][v] += 1
            term_words[scope][v] += words

    doc_rows.append({
        "document_post_id": d.get("document_post_id", ""),
        "document_date": d.get("document_date", ""),
        "document_title": d.get("document_title", ""),
        "processes": " | ".join(fields["process"]),
        "collections": " | ".join(fields["collection"]),
        "categories": " | ".join(fields["category"]),
        "tags": " | ".join(fields["tag"]),
        "process_count": len(fields["process"]),
        "collection_count": len(fields["collection"]),
        "category_count": len(fields["category"]),
        "tag_count": len(fields["tag"]),
        "content_words": d.get("content_words", ""),
        "document_url": d.get("document_url", ""),
    })

with ensure_parent(OUT_TERMS).open("w", encoding="utf-8", newline="") as f:
    fields = ["scope", "term", "document_count", "total_words"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for scope in ["process", "collection", "category", "tag"]:
        for term, count in sorted(terms[scope].items(), key=lambda x: (-x[1], x[0])):
            w.writerow({
                "scope": scope,
                "term": term,
                "document_count": count,
                "total_words": term_words[scope][term],
            })

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "processes", "collections", "categories", "tags",
        "process_count", "collection_count", "category_count", "tag_count",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(doc_rows)

report = []
report.append("ShowTrials taxonomy diagnosis")
report.append("")
report.append(f"Documents: {len(docs)}")
report.append("")
for scope in ["process", "collection", "category", "tag"]:
    report.append(f"{scope.title()} terms: {len(terms[scope])}")
    for term, count in sorted(terms[scope].items(), key=lambda x: (-x[1], x[0]))[:30]:
        report.append(f"{count}\t{term}")
    report.append("")

report.append("Documents with multiple taxonomy values:")
for key in ["process_count", "collection_count", "category_count", "tag_count"]:
    count = sum(1 for r in doc_rows if int(r[key]) > 1)
    report.append(f"{count}\t{key}>1")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TERMS)
print(OUT_DOCS)
print(OUT_REPORT)
