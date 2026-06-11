#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"

OUT_DOCS = BASE / "showtrials_document_types.tsv"
OUT_SUMMARY = BASE / "showtrials_document_type_summary.tsv"
OUT_REPORT = BASE / "showtrials_document_types_report.txt"

RULES = [
    ("interrogation_protocol", r"протокол допроса"),
    ("confrontation_protocol", r"очная ставка|протокол очной ставки"),
    ("letter", r"письмо"),
    ("statement", r"заявлени[ея]"),
    ("special_report", r"спецсообщение"),
    ("memo_note", r"записка"),
    ("session_transcript", r"стенограмма|заседани[ея]"),
    ("indictment", r"обвинительное заключение"),
    ("verdict_or_sentence", r"приговор"),
    ("plea_pardon", r"помиловани[ея]"),
    ("autobiography", r"автобиография"),
    ("reference_note", r"справка"),
    ("conversation_recording", r"запись разговоров"),
    ("article", r"статья|очерк"),
]

def classify(title):
    t = (title or "").casefold()
    matches = []
    for dtype, pattern in RULES:
        if re.search(pattern, t, re.I):
            matches.append(dtype)
    if matches:
        return matches[0], " | ".join(matches), "rule_title"
    return "unknown", "", "unmatched"

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

rows = []
summary = Counter()
by_process = defaultdict(Counter)
by_collection = defaultdict(Counter)

for d in docs:
    dtype, matches, reason = classify(d.get("document_title", ""))
    words = int(d.get("content_words") or 0)

    rows.append({
        "document_post_id": d.get("document_post_id", ""),
        "document_date": d.get("document_date", ""),
        "document_title": d.get("document_title", ""),
        "document_type": dtype,
        "matched_types": matches,
        "reason": reason,
        "primary_process": d.get("primary_process", ""),
        "primary_collection": d.get("primary_collection", ""),
        "category_names": d.get("category_names", ""),
        "tag_names": d.get("tag_names", ""),
        "content_words": d.get("content_words", ""),
        "document_url": d.get("document_url", ""),
    })

    summary[dtype] += 1
    by_process[d.get("primary_process") or "UNSET"][dtype] += 1
    by_collection[d.get("primary_collection") or "UNSET"][dtype] += 1

with OUT_DOCS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "document_type", "matched_types", "reason",
        "primary_process", "primary_collection",
        "category_names", "tag_names",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

with OUT_SUMMARY.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["scope", "name", "document_type", "count"])
    for dtype, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["global", "ALL", dtype, count])
    for proc, c in sorted(by_process.items()):
        for dtype, count in sorted(c.items(), key=lambda x: (-x[1], x[0])):
            w.writerow(["process", proc, dtype, count])
    for coll, c in sorted(by_collection.items()):
        for dtype, count in sorted(c.items(), key=lambda x: (-x[1], x[0])):
            w.writerow(["collection", coll, dtype, count])

report = []
report.append("ShowTrials document type diagnosis")
report.append("")
report.append(f"Documents: {len(docs)}")
report.append("")
report.append("Document types:")
for dtype, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{dtype}")

report.append("")
report.append("Unknown examples:")
for r in [x for x in rows if x["document_type"] == "unknown"][:80]:
    report.append(f"{r['document_post_id']}\t{r['document_title']}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOCS)
print(OUT_SUMMARY)
print(OUT_REPORT)
