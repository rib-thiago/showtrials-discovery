#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    EXPORT_TXT_DIR,
    MASTER_CATALOG,
    SEARCH_CORPUS,
    SEARCH_CORPUS_REPORT,
    ensure_parent,
)

CATALOG = MASTER_CATALOG
TXT_DIR = EXPORT_TXT_DIR
OUT_TSV = SEARCH_CORPUS
OUT_REPORT = SEARCH_CORPUS_REPORT

def normalize_space(s):
    return re.sub(r"\s+", " ", s or "").strip()

def find_text_file(doc_id):
    matches = list(TXT_DIR.glob(f"{doc_id}_*.txt"))
    return matches[0] if matches else None

rows = []

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        doc_id = r["document_post_id"]
        text_file = find_text_file(doc_id)
        text = text_file.read_text(encoding="utf-8", errors="replace") if text_file else ""

        metadata_text = " ".join([
            r.get("document_title", ""),
            r.get("primary_process", ""),
            r.get("primary_collection", ""),
            r.get("category_names", ""),
            r.get("tag_names", ""),
            r.get("document_date", ""),
            r.get("slug", ""),
        ])

        search_text = normalize_space(metadata_text + " " + text)

        rows.append({
            "document_post_id": doc_id,
            "document_date": r.get("document_date", ""),
            "document_title": r.get("document_title", ""),
            "primary_process": r.get("primary_process", ""),
            "primary_collection": r.get("primary_collection", ""),
            "category_names": r.get("category_names", ""),
            "tag_names": r.get("tag_names", ""),
            "content_words": r.get("content_words", ""),
            "document_url": r.get("document_url", ""),
            "text_file": str(text_file) if text_file else "",
            "search_text": search_text,
        })

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
    fields = list(rows[0].keys())
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

missing = [r for r in rows if not r["text_file"]]
empty = [r for r in rows if not r["search_text"]]

report = [
    "ShowTrials search corpus diagnosis",
    "",
    f"Rows: {len(rows)}",
    f"Missing text files: {len(missing)}",
    f"Empty search_text: {len(empty)}",
    f"Output TSV: {OUT_TSV}",
    "",
    "Largest search_text rows:",
]

for r in sorted(rows, key=lambda x: len(x["search_text"]), reverse=True)[:20]:
    report.append(f"{len(r['search_text'])}\t{r['document_post_id']}\t{r['document_title']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
