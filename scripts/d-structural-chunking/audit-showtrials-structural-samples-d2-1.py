#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path
from collections import defaultdict

csv.field_size_limit(sys.maxsize)

BASE = Path("/srv/projects/showtrials-discovery")

CATALOG = BASE / "showtrials_master_catalog.tsv"
DOC_TYPES = BASE / "showtrials_document_types_v4.tsv"
CORPUS = BASE / "showtrials_search_corpus.tsv"
D1_DOCS = BASE / "showtrials_corpus_sizing_by_document_d1.tsv"

OUT_DIR = BASE / "structural_samples_d2_1"
OUT_INDEX = BASE / "showtrials_structural_samples_d2_1_index.tsv"
OUT_REPORT = BASE / "showtrials_structural_samples_d2_1_report.txt"

SAMPLE_TYPES = [
    "special_report",
    "interrogation_protocol",
    "session_transcript",
    "letter",
    "statement",
    "conversation_recording",
    "testimony",
    "confrontation_protocol",
    "memo_note",
    "list",
    "indictment",
    "press_summary",
    "reference_note",
    "biographical_article",
]

HEAD_CHARS = 3500
TAIL_CHARS = 2500
MAX_PER_TYPE = 8

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def clean(s):
    s = (s or "").replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{4,}", "\n\n\n", s)
    return s.strip()

def get_text(row):
    for k in ("search_text", "content_text", "text", "content", "body"):
        if k in row and row[k]:
            return row[k]
    return ""

def slug(s):
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s)
    return s.strip("_")[:80] or "sample"

def sample_body(text):
    text = clean(text)
    if len(text) <= HEAD_CHARS + TAIL_CHARS + 500:
        return text

    return (
        text[:HEAD_CHARS].rstrip()
        + "\n\n--- [MIDDLE OMITTED FOR STRUCTURAL AUDIT] ---\n\n"
        + text[-TAIL_CHARS:].lstrip()
    )

def choose_docs(rows):
    rows = sorted(rows, key=lambda r: int(r.get("content_chars") or 0))

    if len(rows) <= MAX_PER_TYPE:
        return rows

    idxs = [
        0,
        len(rows) // 4,
        len(rows) // 2,
        (len(rows) * 3) // 4,
        len(rows) - 1,
    ]

    selected = []
    seen = set()

    for i in idxs:
        if i not in seen:
            selected.append(rows[i])
            seen.add(i)

    # Complementa com grandes documentos, pois são os que mais importam para chunking.
    for r in sorted(rows, key=lambda x: -int(x.get("content_chars") or 0)):
        if len(selected) >= MAX_PER_TYPE:
            break
        doc_id = r["document_post_id"]
        if doc_id not in {x["document_post_id"] for x in selected}:
            selected.append(r)

    return selected

types = {r["document_post_id"]: r["document_type"] for r in load(DOC_TYPES)}
catalog = {r["document_post_id"]: r for r in load(CATALOG)}
d1 = {r["document_post_id"]: r for r in load(D1_DOCS)}

corpus = {}
for r in load(CORPUS):
    corpus[r["document_post_id"]] = clean(get_text(r))

by_type = defaultdict(list)

for doc_id, meta in catalog.items():
    dt = types.get(doc_id, "unknown")
    if dt not in SAMPLE_TYPES:
        continue

    d1r = d1.get(doc_id, {})
    by_type[dt].append({
        "document_post_id": doc_id,
        "document_type": dt,
        "document_title": meta.get("document_title", ""),
        "primary_process": meta.get("primary_process", ""),
        "primary_collection": meta.get("primary_collection", ""),
        "document_date": meta.get("document_date", ""),
        "document_url": meta.get("document_url", ""),
        "content_chars": d1r.get("content_chars") or meta.get("content_chars") or len(corpus.get(doc_id, "")),
        "content_words": d1r.get("content_words") or meta.get("content_words") or "",
    })

OUT_DIR.mkdir(exist_ok=True)

index_rows = []
report = []
report.append("ShowTrials D2.1 structural sample audit")
report.append("")
report.append(f"Output dir: {OUT_DIR}")
report.append(f"Sample types: {len(SAMPLE_TYPES)}")
report.append(f"Max per type: {MAX_PER_TYPE}")
report.append("")

for dt in SAMPLE_TYPES:
    selected = choose_docs(by_type.get(dt, []))
    report.append(f"{dt}\tselected={len(selected)}\ttotal={len(by_type.get(dt, []))}")

    type_dir = OUT_DIR / dt
    type_dir.mkdir(exist_ok=True)

    for n, r in enumerate(selected, start=1):
        doc_id = r["document_post_id"]
        text = corpus.get(doc_id, "")
        filename = f"{n:02d}_{doc_id}_{slug(r['document_title'])}.txt"
        path = type_dir / filename

        content = []
        content.append(f"document_post_id: {doc_id}")
        content.append(f"document_type: {r['document_type']}")
        content.append(f"document_title: {r['document_title']}")
        content.append(f"primary_process: {r['primary_process']}")
        content.append(f"primary_collection: {r['primary_collection']}")
        content.append(f"document_date: {r['document_date']}")
        content.append(f"content_chars: {r['content_chars']}")
        content.append(f"content_words: {r['content_words']}")
        content.append(f"document_url: {r['document_url']}")
        content.append("")
        content.append("=== STRUCTURAL SAMPLE START ===")
        content.append(sample_body(text))
        content.append("=== STRUCTURAL SAMPLE END ===")
        content.append("")

        path.write_text("\n".join(content), encoding="utf-8")

        index_rows.append({
            "document_type": dt,
            "sample_no": n,
            "document_post_id": doc_id,
            "content_chars": r["content_chars"],
            "content_words": r["content_words"],
            "primary_process": r["primary_process"],
            "document_title": r["document_title"],
            "sample_path": str(path),
            "document_url": r["document_url"],
        })

with OUT_INDEX.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_type", "sample_no", "document_post_id",
        "content_chars", "content_words", "primary_process",
        "document_title", "sample_path", "document_url",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(index_rows)

report.append("")
report.append("Outputs:")
report.append(str(OUT_DIR))
report.append(str(OUT_INDEX))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DIR)
print(OUT_INDEX)
print(OUT_REPORT)
