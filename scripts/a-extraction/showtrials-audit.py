#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"
TEXT_CLEAN = BASE / "showtrials_text_cleanliness.tsv"

OUT_DOCS = BASE / "showtrials_corpus_audit_documents.tsv"
OUT_SUMMARY = BASE / "showtrials_corpus_audit_summary.tsv"
OUT_REPORT = BASE / "showtrials_corpus_audit_report.txt"

def split_pipe(v):
    return [x.strip() for x in (v or "").split(" | ") if x.strip()]

def to_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

clean_by_id = {}
if TEXT_CLEAN.exists():
    with TEXT_CLEAN.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            filename = r.get("filename", "")
            doc_id = filename.split("_", 1)[0]
            clean_by_id[doc_id] = r

audit_rows = []

summary = Counter()
by_process = defaultdict(lambda: Counter())
by_collection = defaultdict(lambda: Counter())

for d in docs:
    doc_id = d.get("document_post_id", "")
    words = to_int(d.get("content_words"))
    chars = to_int(d.get("content_chars"))

    processes = split_pipe(d.get("all_processes"))
    collections = split_pipe(d.get("all_collections"))
    categories = split_pipe(d.get("category_names"))
    tags = split_pipe(d.get("tag_names"))

    clean = clean_by_id.get(doc_id, {})

    flags = []

    if not d.get("primary_process"):
        flags.append("missing_primary_process")
    if not d.get("primary_collection"):
        flags.append("missing_primary_collection")
    if not categories:
        flags.append("missing_category")
    if not tags:
        flags.append("missing_tag")
    if len(processes) > 1:
        flags.append("multi_process")
    if len(categories) > 1:
        flags.append("multi_category")
    if len(tags) > 1:
        flags.append("multi_tag")
    if words == 0:
        flags.append("empty_text")
    if words < 100:
        flags.append("very_short")
    if words > 10000:
        flags.append("very_long")
    if to_int(clean.get("html_tag_like")) > 0:
        flags.append("angle_markup_present")
    if to_int(clean.get("nbsp_char")) > 0:
        flags.append("nbsp_present")
    if to_int(clean.get("footnote_marker")) > 0:
        flags.append("footnotes_present")
    if to_int(clean.get("archive_ref")) > 0:
        flags.append("archive_refs_present")
    if to_int(clean.get("stamp_marker")) > 0:
        flags.append("stamp_markers_present")

    for flag in flags:
        summary[flag] += 1
        by_process[d.get("primary_process") or "UNSET"][flag] += 1
        by_collection[d.get("primary_collection") or "UNSET"][flag] += 1

    audit_rows.append({
        "document_post_id": doc_id,
        "document_date": d.get("document_date", ""),
        "document_title": d.get("document_title", ""),
        "primary_process": d.get("primary_process", ""),
        "primary_collection": d.get("primary_collection", ""),
        "category_count": len(categories),
        "tag_count": len(tags),
        "process_count": len(processes),
        "content_words": words,
        "content_chars": chars,
        "flags": " | ".join(flags),
        "document_url": d.get("document_url", ""),
    })

with OUT_DOCS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "primary_process", "primary_collection",
        "category_count", "tag_count", "process_count",
        "content_words", "content_chars", "flags", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(audit_rows)

with OUT_SUMMARY.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["scope", "name", "flag", "count"])
    for flag, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["global", "ALL", flag, count])
    for proc, flags in sorted(by_process.items()):
        for flag, count in sorted(flags.items(), key=lambda x: (-x[1], x[0])):
            w.writerow(["process", proc, flag, count])
    for coll, flags in sorted(by_collection.items()):
        for flag, count in sorted(flags.items(), key=lambda x: (-x[1], x[0])):
            w.writerow(["collection", coll, flag, count])

report = []
report.append("ShowTrials corpus audit")
report.append("")
report.append(f"Documents loaded: {len(docs)}")
report.append(f"Text cleanliness available: {'yes' if clean_by_id else 'no'}")
report.append("")
report.append("Global flags:")
for flag, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{flag}")

report.append("")
report.append("Very long documents:")
for r in sorted(audit_rows, key=lambda x: x["content_words"], reverse=True)[:25]:
    report.append(
        f"{r['content_words']}\t{r['primary_process']}\t{r['primary_collection']}\t{r['document_title']}"
    )

report.append("")
report.append("Very short documents:")
for r in sorted(audit_rows, key=lambda x: x["content_words"])[:25]:
    report.append(
        f"{r['content_words']}\t{r['primary_process']}\t{r['primary_collection']}\t{r['document_title']}"
    )

report.append("")
report.append("Documents with multiple processes:")
for r in [x for x in audit_rows if "multi_process" in x["flags"].split(" | ")][:30]:
    report.append(
        f"{r['document_post_id']}\t{r['document_date']}\t{r['document_title']}"
    )

report.append("")
report.append("Documents with multiple tags:")
for r in [x for x in audit_rows if "multi_tag" in x["flags"].split(" | ")][:30]:
    report.append(
        f"{r['document_post_id']}\t{r['document_date']}\t{r['document_title']}"
    )

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOCS)
print(OUT_SUMMARY)
print(OUT_REPORT)
