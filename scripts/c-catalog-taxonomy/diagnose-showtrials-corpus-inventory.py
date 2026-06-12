#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    COLLECTION_INVENTORY,
    CORPUS_INVENTORY_REPORT,
    DOCUMENT_COLLECTIONS,
    LARGEST_DOCUMENTS,
    PROCESS_INVENTORY,
    TIMELINE,
    ensure_parent,
)

SRC = DOCUMENT_COLLECTIONS

OUT_PROCESS = PROCESS_INVENTORY
OUT_COLLECTION = COLLECTION_INVENTORY
OUT_TIMELINE = TIMELINE
OUT_LARGEST = LARGEST_DOCUMENTS
OUT_REPORT = CORPUS_INVENTORY_REPORT

rows = []
with SRC.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for r in reader:
        r["content_words"] = int(r.get("content_words") or 0)
        rows.append(r)

# Deduplicate document records per collection relation.
# A document may appear in ГЛАВНАЯ and in a specific collection;
# for process/collection inventory, ignore the global ГЛАВНАЯ collection.
curated = [
    r for r in rows
    if not (r["process_title"] == "ГЛАВНАЯ" and r["collection_title"] == "ГЛАВНАЯ")
]

# For timeline and largest docs, deduplicate by post id.
best_by_doc = {}
for r in curated:
    doc_id = r["document_post_id"]
    if doc_id not in best_by_doc:
        best_by_doc[doc_id] = r
    else:
        # Prefer non-empty specific collections with larger word count tie-neutral.
        old = best_by_doc[doc_id]
        if old["collection_title"] == "ГЛАВНАЯ" and r["collection_title"] != "ГЛАВНАЯ":
            best_by_doc[doc_id] = r

unique_docs = list(best_by_doc.values())

# Process inventory
proc = defaultdict(lambda: {"collections": set(), "docs": set(), "words": 0})
for r in curated:
    p = r["process_title"]
    d = r["document_post_id"]
    proc[p]["collections"].add(r["collection_title"])
    proc[p]["docs"].add(d)

for r in unique_docs:
    p = r["process_title"]
    proc[p]["words"] += r["content_words"]

with ensure_parent(OUT_PROCESS).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["process_title", "collection_count", "document_count", "total_words"])
    for p, data in sorted(proc.items(), key=lambda x: len(x[1]["docs"]), reverse=True):
        w.writerow([p, len(data["collections"]), len(data["docs"]), data["words"]])

# Collection inventory
coll = defaultdict(lambda: {"docs": set(), "words": 0})
for r in curated:
    key = (r["process_title"], r["collection_title"])
    coll[key]["docs"].add(r["document_post_id"])

for r in unique_docs:
    key = (r["process_title"], r["collection_title"])
    coll[key]["words"] += r["content_words"]

with ensure_parent(OUT_COLLECTION).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["process_title", "collection_title", "document_count", "total_words"])
    for (p, c), data in sorted(coll.items(), key=lambda x: len(x[1]["docs"]), reverse=True):
        w.writerow([p, c, len(data["docs"]), data["words"]])

# Timeline
timeline = defaultdict(lambda: {"docs": 0, "words": 0})
for r in unique_docs:
    date = r.get("document_date", "")
    year = date[:4] if len(date) >= 4 else "unknown"
    timeline[year]["docs"] += 1
    timeline[year]["words"] += r["content_words"]

with ensure_parent(OUT_TIMELINE).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["year", "document_count", "total_words"])
    for year, data in sorted(timeline.items()):
        w.writerow([year, data["docs"], data["words"]])

# Largest documents
largest = sorted(unique_docs, key=lambda r: r["content_words"], reverse=True)

with ensure_parent(OUT_LARGEST).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow([
        "rank", "document_post_id", "document_title", "content_words",
        "process_title", "collection_title", "document_url"
    ])
    for idx, r in enumerate(largest[:100], start=1):
        w.writerow([
            idx,
            r["document_post_id"],
            r["document_title"],
            r["content_words"],
            r["process_title"],
            r["collection_title"],
            r["document_url"],
        ])

# Report
report = []
report.append("ShowTrials corpus inventory diagnosis")
report.append("")
report.append(f"Source rows: {len(rows)}")
report.append(f"Curated rows, excluding global home index: {len(curated)}")
report.append(f"Unique documents in curated inventory: {len(unique_docs)}")
report.append("")
report.append("Top processes by document count:")
for p, data in sorted(proc.items(), key=lambda x: len(x[1]["docs"]), reverse=True)[:20]:
    report.append(f"{len(data['docs'])}\t{data['words']}\t{p}")
report.append("")
report.append("Top collections by document count:")
for (p, c), data in sorted(coll.items(), key=lambda x: len(x[1]["docs"]), reverse=True)[:30]:
    report.append(f"{len(data['docs'])}\t{data['words']}\t{p}\t{c}")
report.append("")
report.append("Top years by document count:")
for year, data in sorted(timeline.items(), key=lambda x: x[1]["docs"], reverse=True)[:20]:
    report.append(f"{data['docs']}\t{data['words']}\t{year}")
report.append("")
report.append("Largest documents:")
for r in largest[:20]:
    report.append(f"{r['content_words']}\t{r['process_title']}\t{r['collection_title']}\t{r['document_title']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PROCESS)
print(OUT_COLLECTION)
print(OUT_TIMELINE)
print(OUT_LARGEST)
print(OUT_REPORT)
