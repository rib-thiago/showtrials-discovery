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
    DOCUMENT_TYPES_V4,
    MASTER_CATALOG,
    TRANSLATION_COST_BY_DOCUMENT,
    TRANSLATION_COST_BY_DOCUMENT_TYPE,
    TRANSLATION_COST_BY_PROCESS,
    TRANSLATION_COST_REPORT,
    ensure_parent,
)

CATALOG = MASTER_CATALOG
DOC_TYPES = DOCUMENT_TYPES_V4

OUT_DOCS = TRANSLATION_COST_BY_DOCUMENT
OUT_PROCESS = TRANSLATION_COST_BY_PROCESS
OUT_DOCTYPE = TRANSLATION_COST_BY_DOCUMENT_TYPE
OUT_REPORT = TRANSLATION_COST_REPORT

FREE_CHARS_MONTHLY = 500_000
NMT_USD_PER_MILLION = 20.0

def load_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def cost(chars, targets=1, apply_free=False):
    billable = chars * targets
    if apply_free:
        billable = max(0, billable - FREE_CHARS_MONTHLY)
    return billable / 1_000_000 * NMT_USD_PER_MILLION

types = {
    r["document_post_id"]: r.get("document_type", "unknown")
    for r in load_tsv(DOC_TYPES)
}

catalog = load_tsv(CATALOG)

doc_rows = []
by_process = defaultdict(lambda: {"docs": 0, "chars": 0, "words": 0})
by_type = defaultdict(lambda: {"docs": 0, "chars": 0, "words": 0})

chars_all = []
words_all = []

for r in catalog:
    doc_id = r["document_post_id"]
    chars = int(r.get("content_chars") or 0)
    words = int(r.get("content_words") or 0)
    process = r.get("primary_process") or "UNSET"
    doctype = types.get(doc_id, "unknown")

    chars_all.append(chars)
    words_all.append(words)

    by_process[process]["docs"] += 1
    by_process[process]["chars"] += chars
    by_process[process]["words"] += words

    by_type[doctype]["docs"] += 1
    by_type[doctype]["chars"] += chars
    by_type[doctype]["words"] += words

    doc_rows.append({
        "document_post_id": doc_id,
        "document_date": r.get("document_date", ""),
        "document_title": r.get("document_title", ""),
        "primary_process": process,
        "primary_collection": r.get("primary_collection", ""),
        "document_type": doctype,
        "content_chars": chars,
        "content_words": words,
        "estimated_nmt_ru_en_usd": f"{cost(chars):.4f}",
        "estimated_nmt_ru_en_pt_usd": f"{cost(chars, targets=2):.4f}",
        "document_url": r.get("document_url", ""),
    })

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "primary_process", "primary_collection", "document_type",
        "content_chars", "content_words",
        "estimated_nmt_ru_en_usd", "estimated_nmt_ru_en_pt_usd",
        "document_url",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(doc_rows, key=lambda x: (-int(x["content_chars"]), x["document_post_id"])))

def write_group(path, rows, key_name):
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as f:
        fields = [
            key_name, "documents", "chars", "words",
            "avg_chars_per_doc", "estimated_nmt_ru_en_usd",
            "estimated_nmt_ru_en_pt_usd",
        ]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for key, v in sorted(rows.items(), key=lambda x: (-x[1]["chars"], x[0])):
            docs = v["docs"]
            chars = v["chars"]
            w.writerow({
                key_name: key,
                "documents": docs,
                "chars": chars,
                "words": v["words"],
                "avg_chars_per_doc": round(chars / docs, 2) if docs else 0,
                "estimated_nmt_ru_en_usd": f"{cost(chars):.2f}",
                "estimated_nmt_ru_en_pt_usd": f"{cost(chars, targets=2):.2f}",
            })

write_group(OUT_PROCESS, by_process, "primary_process")
write_group(OUT_DOCTYPE, by_type, "document_type")

total_chars = sum(chars_all)
total_words = sum(words_all)

def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    idx = int(round((len(values) - 1) * p))
    return values[idx]

report = []
report.append("ShowTrials translation cost diagnosis")
report.append("")
report.append(f"Documents: {len(catalog)}")
report.append(f"Total chars: {total_chars}")
report.append(f"Total words: {total_words}")
report.append("")
report.append("Document size distribution:")
report.append(f"min_chars: {min(chars_all) if chars_all else 0}")
report.append(f"median_chars: {int(statistics.median(chars_all)) if chars_all else 0}")
report.append(f"avg_chars: {round(total_chars / len(chars_all), 2) if chars_all else 0}")
report.append(f"p90_chars: {percentile(chars_all, 0.90)}")
report.append(f"p95_chars: {percentile(chars_all, 0.95)}")
report.append(f"p99_chars: {percentile(chars_all, 0.99)}")
report.append(f"max_chars: {max(chars_all) if chars_all else 0}")
report.append("")
report.append("NMT cost estimates:")
report.append(f"RU->EN before free credit: ${cost(total_chars):.2f}")
report.append(f"RU->EN after monthly 500k free credit: ${cost(total_chars, apply_free=True):.2f}")
report.append(f"RU->EN+PT before free credit: ${cost(total_chars, targets=2):.2f}")
report.append(f"RU->EN+PT after monthly 500k free credit: ${cost(total_chars, targets=2, apply_free=True):.2f}")
report.append("")
report.append("Top processes by chars:")
for key, v in sorted(by_process.items(), key=lambda x: (-x[1]["chars"], x[0]))[:20]:
    report.append(f"{v['chars']}\tdocs={v['docs']}\t${cost(v['chars']):.2f}\t{key}")
report.append("")
report.append("Top document types by chars:")
for key, v in sorted(by_type.items(), key=lambda x: (-x[1]["chars"], x[0]))[:30]:
    report.append(f"{v['chars']}\tdocs={v['docs']}\t${cost(v['chars']):.2f}\t{key}")
report.append("")
report.append("Outputs:")
report.append(str(OUT_DOCS))
report.append(str(OUT_PROCESS))
report.append(str(OUT_DOCTYPE))

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOCS)
print(OUT_PROCESS)
print(OUT_DOCTYPE)
print(OUT_REPORT)
