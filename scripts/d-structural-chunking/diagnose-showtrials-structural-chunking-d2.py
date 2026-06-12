#!/usr/bin/env python3
import csv
import sys
import re

csv.field_size_limit(sys.maxsize)
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    CORPUS_SIZING_BY_DOCUMENT_D1,
    DOCUMENT_TYPES_V4,
    MASTER_CATALOG,
    SEARCH_CORPUS,
    STRUCTURAL_CHUNKING_D2_BY_DOCUMENT,
    STRUCTURAL_CHUNKING_D2_BY_TYPE,
    STRUCTURAL_CHUNKING_D2_EXAMPLES,
    STRUCTURAL_CHUNKING_D2_REPORT,
    ensure_parent,
)

CATALOG = MASTER_CATALOG
DOC_TYPES = DOCUMENT_TYPES_V4
CORPUS = SEARCH_CORPUS
D1_DOCS = CORPUS_SIZING_BY_DOCUMENT_D1

OUT_DOCS = STRUCTURAL_CHUNKING_D2_BY_DOCUMENT
OUT_TYPES = STRUCTURAL_CHUNKING_D2_BY_TYPE
OUT_EXAMPLES = STRUCTURAL_CHUNKING_D2_EXAMPLES
REPORT = STRUCTURAL_CHUNKING_D2_REPORT

PATTERNS = {
    "question_answer_markers": re.compile(r"\b(Вопрос|Ответ|В\.|О\.|В:|О:)\b", re.I),
    "speaker_turn_markers": re.compile(r"(^|\n)\s*[А-ЯЁA-Z][А-ЯЁа-яёA-Za-z.\- ]{1,60}\s*[:—-]\s+"),
    "date_headers": re.compile(r"\b\d{1,2}\s+[А-Яа-яёЁ]+\s+\d{4}\s*г\.?"),
    "numbered_points": re.compile(r"(^|\n)\s*(\d+[\).]|[IVXLC]+\.|[а-яё]\))\s+"),
    "signature_markers": re.compile(r"\b(Подпись|подпись|Секретарь|Председатель|Прокурор|Следователь)\b"),
    "attachment_markers": re.compile(r"\b(Приложение|приложением|прилагается|справка|список)\b", re.I),
    "salutation_markers": re.compile(r"\b(Уважаемый|Дорогой|Товарищ)\b", re.I),
    "list_density": re.compile(r"(^|\n)\s*[-–—•]?\s*[А-ЯЁ][А-ЯЁа-яё\-]+(?:\s+[А-ЯЁ]\.[А-ЯЁ]\.)?"),
}

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def clean(s):
    return re.sub(r"\n{3,}", "\n\n", (s or "").replace("\r\n", "\n")).strip()

def get_text(row):
    for k in ("search_text", "content_text", "text", "content", "body"):
        if k in row and row[k]:
            return row[k]
    return ""

def paragraph_count(text):
    if not text:
        return 0
    return len([p for p in re.split(r"\n\s*\n+", text) if p.strip()])

def line_count(text):
    return len([ln for ln in text.splitlines() if ln.strip()])

def sample_match(pattern, text):
    m = pattern.search(text)
    if not m:
        return ""
    start = max(0, m.start() - 80)
    end = min(len(text), m.end() + 160)
    return re.sub(r"\s+", " ", text[start:end]).strip()

doctypes = {r["document_post_id"]: r["document_type"] for r in load(DOC_TYPES)}
catalog = {r["document_post_id"]: r for r in load(CATALOG)}
d1 = {r["document_post_id"]: r for r in load(D1_DOCS)}

corpus = {}
for r in load(CORPUS):
    doc_id = r["document_post_id"]
    corpus[doc_id] = clean(get_text(r))

doc_rows = []
examples = []
by_type = defaultdict(list)

for doc_id, meta in catalog.items():
    text = corpus.get(doc_id, "")
    dt = doctypes.get(doc_id, "unknown")
    d1r = d1.get(doc_id, {})

    counts = {}
    samples = {}
    for name, pat in PATTERNS.items():
        counts[name] = len(pat.findall(text))
        samples[name] = sample_match(pat, text)

    paras = paragraph_count(text)
    lines = line_count(text)
    chars = int(meta.get("content_chars") or d1r.get("content_chars") or len(text) or 0)

    if counts["question_answer_markers"] >= 2:
        recommended_unit = "question_answer_blocks"
        confidence = "high"
    elif counts["speaker_turn_markers"] >= 3:
        recommended_unit = "speaker_turns"
        confidence = "high"
    elif counts["numbered_points"] >= 3:
        recommended_unit = "numbered_sections_or_points"
        confidence = "medium"
    elif counts["attachment_markers"] >= 2:
        recommended_unit = "header_body_attachments"
        confidence = "medium"
    elif paras >= 4:
        recommended_unit = "paragraph_blocks"
        confidence = "medium"
    elif lines >= 8 and dt in {"list", "data_extract"}:
        recommended_unit = "line_or_record_groups"
        confidence = "medium"
    else:
        recommended_unit = "whole_or_light_paragraph_chunks"
        confidence = "low"

    row = {
        "document_post_id": doc_id,
        "document_type": dt,
        "primary_process": meta.get("primary_process", ""),
        "document_title": meta.get("document_title", ""),
        "content_chars": chars,
        "paragraphs": paras,
        "lines": lines,
        "recommended_unit": recommended_unit,
        "confidence": confidence,
        **counts,
    }
    doc_rows.append(row)
    by_type[dt].append(row)

    for name, sample in samples.items():
        if sample:
            examples.append({
                "document_post_id": doc_id,
                "document_type": dt,
                "pattern": name,
                "document_title": meta.get("document_title", ""),
                "sample": sample,
            })

fields_doc = [
    "document_post_id", "document_type", "primary_process", "document_title",
    "content_chars", "paragraphs", "lines", "recommended_unit", "confidence",
    *PATTERNS.keys(),
]

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields_doc, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(doc_rows, key=lambda r: (-int(r["content_chars"]), r["document_post_id"])))

type_rows = []
for dt, rows in by_type.items():
    unit_counts = Counter(r["recommended_unit"] for r in rows)
    conf_counts = Counter(r["confidence"] for r in rows)
    chars = sum(int(r["content_chars"]) for r in rows)

    dominant_unit, dominant_count = unit_counts.most_common(1)[0]
    type_rows.append({
        "document_type": dt,
        "documents": len(rows),
        "chars": chars,
        "dominant_recommended_unit": dominant_unit,
        "dominant_unit_docs": dominant_count,
        "high_confidence_docs": conf_counts["high"],
        "medium_confidence_docs": conf_counts["medium"],
        "low_confidence_docs": conf_counts["low"],
        "qa_docs": sum(1 for r in rows if r["question_answer_markers"] >= 2),
        "speaker_turn_docs": sum(1 for r in rows if r["speaker_turn_markers"] >= 3),
        "numbered_docs": sum(1 for r in rows if r["numbered_points"] >= 3),
        "attachment_docs": sum(1 for r in rows if r["attachment_markers"] >= 2),
        "avg_paragraphs": round(sum(r["paragraphs"] for r in rows) / len(rows), 2),
        "avg_lines": round(sum(r["lines"] for r in rows) / len(rows), 2),
    })

with ensure_parent(OUT_TYPES).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_type", "documents", "chars",
        "dominant_recommended_unit", "dominant_unit_docs",
        "high_confidence_docs", "medium_confidence_docs", "low_confidence_docs",
        "qa_docs", "speaker_turn_docs", "numbered_docs", "attachment_docs",
        "avg_paragraphs", "avg_lines",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(type_rows, key=lambda r: (-r["chars"], r["document_type"])))

with ensure_parent(OUT_EXAMPLES).open("w", encoding="utf-8", newline="") as f:
    fields = ["document_post_id", "document_type", "pattern", "document_title", "sample"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(examples[:1000])

report = []
report.append("ShowTrials D2 structural chunking discovery")
report.append("")
report.append(f"Documents: {len(doc_rows)}")
report.append(f"Document types: {len(type_rows)}")
report.append(f"Examples captured: {len(examples[:1000])}")
report.append("")
report.append("Top document types:")
for r in sorted(type_rows, key=lambda x: (-x["chars"], x["document_type"]))[:20]:
    report.append(
        f"{r['document_type']}\tdocs={r['documents']}\tchars={r['chars']}\t"
        f"unit={r['dominant_recommended_unit']}\thigh={r['high_confidence_docs']}\t"
        f"medium={r['medium_confidence_docs']}\tlow={r['low_confidence_docs']}"
    )
report.append("")
report.append("Outputs:")
report.append(str(OUT_DOCS))
report.append(str(OUT_TYPES))
report.append(str(OUT_EXAMPLES))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOCS)
print(OUT_TYPES)
print(OUT_EXAMPLES)
print(REPORT)
