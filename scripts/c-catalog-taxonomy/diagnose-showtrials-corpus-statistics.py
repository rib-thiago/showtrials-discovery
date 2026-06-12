#!/usr/bin/env python3
import csv
import statistics
import sys
from pathlib import Path
from collections import defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    CORPUS_LARGEST_DOCUMENTS,
    CORPUS_SMALLEST_DOCUMENTS,
    CORPUS_STATISTICS_BY_COLLECTION,
    CORPUS_STATISTICS_BY_PROCESS,
    CORPUS_STATISTICS_BY_TAG,
    CORPUS_STATISTICS_OVERVIEW,
    CORPUS_STATISTICS_REPORT,
    MASTER_CATALOG,
    ensure_parent,
)

SRC = MASTER_CATALOG

OUT_OVERVIEW = CORPUS_STATISTICS_OVERVIEW
OUT_PROCESS = CORPUS_STATISTICS_BY_PROCESS
OUT_COLLECTION = CORPUS_STATISTICS_BY_COLLECTION
OUT_TAG = CORPUS_STATISTICS_BY_TAG
OUT_LARGEST = CORPUS_LARGEST_DOCUMENTS
OUT_SMALLEST = CORPUS_SMALLEST_DOCUMENTS
OUT_REPORT = CORPUS_STATISTICS_REPORT

def to_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

with SRC.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

for r in rows:
    r["content_words"] = to_int(r.get("content_words"))
    r["content_chars"] = to_int(r.get("content_chars"))

words = [r["content_words"] for r in rows]
chars = [r["content_chars"] for r in rows]

def stats(values):
    values = list(values)
    return {
        "count": len(values),
        "total": sum(values),
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
        "avg": round(sum(values) / len(values), 2) if values else 0,
        "median": statistics.median(values) if values else 0,
    }

word_stats = stats(words)
char_stats = stats(chars)

with ensure_parent(OUT_OVERVIEW).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["metric", "value"])
    w.writerow(["document_count", len(rows)])
    w.writerow(["total_words", word_stats["total"]])
    w.writerow(["total_chars", char_stats["total"]])
    w.writerow(["avg_words", word_stats["avg"]])
    w.writerow(["median_words", word_stats["median"]])
    w.writerow(["min_words", word_stats["min"]])
    w.writerow(["max_words", word_stats["max"]])
    w.writerow(["avg_chars", char_stats["avg"]])
    w.writerow(["median_chars", char_stats["median"]])
    w.writerow(["min_chars", char_stats["min"]])
    w.writerow(["max_chars", char_stats["max"]])

def aggregate_by(field, split=False):
    agg = defaultdict(lambda: {"docs": set(), "words": 0, "chars": 0})
    for r in rows:
        values = [r.get(field, "")]

        if split:
            values = [v.strip() for v in (r.get(field, "") or "").split(" | ") if v.strip()]

        for value in values:
            value = value or "UNSET"
            key = value
            doc_id = r["document_post_id"]
            if doc_id not in agg[key]["docs"]:
                agg[key]["docs"].add(doc_id)
                agg[key]["words"] += r["content_words"]
                agg[key]["chars"] += r["content_chars"]
    return agg

def write_agg(path, agg, label):
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow([label, "document_count", "total_words", "total_chars", "avg_words"])
        for key, data in sorted(agg.items(), key=lambda x: x[1]["words"], reverse=True):
            docs = len(data["docs"])
            avg = round(data["words"] / docs, 2) if docs else 0
            w.writerow([key, docs, data["words"], data["chars"], avg])

process_agg = aggregate_by("primary_process")
collection_agg = aggregate_by("primary_collection")
tag_agg = aggregate_by("tag_names", split=True)

write_agg(OUT_PROCESS, process_agg, "process")
write_agg(OUT_COLLECTION, collection_agg, "collection")
write_agg(OUT_TAG, tag_agg, "tag")

largest = sorted(rows, key=lambda r: r["content_words"], reverse=True)
smallest = sorted(rows, key=lambda r: r["content_words"])

def write_docs(path, docs):
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as f:
        fields = [
            "rank", "document_post_id", "document_title", "content_words",
            "content_chars", "primary_process", "primary_collection",
            "category_names", "tag_names", "document_url"
        ]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for i, r in enumerate(docs, start=1):
            w.writerow({
                "rank": i,
                "document_post_id": r["document_post_id"],
                "document_title": r["document_title"],
                "content_words": r["content_words"],
                "content_chars": r["content_chars"],
                "primary_process": r["primary_process"],
                "primary_collection": r["primary_collection"],
                "category_names": r["category_names"],
                "tag_names": r["tag_names"],
                "document_url": r["document_url"],
            })

write_docs(OUT_LARGEST, largest[:100])
write_docs(OUT_SMALLEST, smallest[:100])

report = []
report.append("ShowTrials corpus statistics diagnosis")
report.append("")
report.append(f"Documents: {len(rows)}")
report.append(f"Total words: {word_stats['total']}")
report.append(f"Total chars: {char_stats['total']}")
report.append(f"Average words/document: {word_stats['avg']}")
report.append(f"Median words/document: {word_stats['median']}")
report.append(f"Min words/document: {word_stats['min']}")
report.append(f"Max words/document: {word_stats['max']}")
report.append("")
report.append("Top processes by words:")
for key, data in sorted(process_agg.items(), key=lambda x: x[1]["words"], reverse=True):
    report.append(f"{data['words']}\t{len(data['docs'])}\t{key}")
report.append("")
report.append("Top collections by words:")
for key, data in sorted(collection_agg.items(), key=lambda x: x[1]["words"], reverse=True)[:30]:
    report.append(f"{data['words']}\t{len(data['docs'])}\t{key}")
report.append("")
report.append("Top tags by words:")
for key, data in sorted(tag_agg.items(), key=lambda x: x[1]["words"], reverse=True)[:30]:
    report.append(f"{data['words']}\t{len(data['docs'])}\t{key}")
report.append("")
report.append("Largest documents:")
for r in largest[:20]:
    report.append(f"{r['content_words']}\t{r['primary_process']}\t{r['primary_collection']}\t{r['document_title']}")
report.append("")
report.append("Smallest documents:")
for r in smallest[:20]:
    report.append(f"{r['content_words']}\t{r['primary_process']}\t{r['primary_collection']}\t{r['document_title']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_OVERVIEW)
print(OUT_PROCESS)
print(OUT_COLLECTION)
print(OUT_TAG)
print(OUT_LARGEST)
print(OUT_SMALLEST)
print(OUT_REPORT)
