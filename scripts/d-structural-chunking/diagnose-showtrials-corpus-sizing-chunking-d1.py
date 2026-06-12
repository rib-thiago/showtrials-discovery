#!/usr/bin/env python3
import csv
import statistics
from pathlib import Path
from collections import defaultdict, Counter
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    CHUNKING_POLICY_RECOMMENDATIONS_D1,
    CORPUS_SIZING_BY_DOCUMENT_D1,
    CORPUS_SIZING_BY_DOCUMENT_TYPE_D1,
    CORPUS_SIZING_BY_PROCESS_D1,
    CORPUS_SIZING_CHUNKING_D1_REPORT,
    DOCUMENT_TYPES_V4,
    MASTER_CATALOG,
    TRANSLATION_PROFILES_V1,
    TRANSLATION_PROFILES_V1_1,
    ensure_parent,
)

CATALOG = MASTER_CATALOG
DOC_TYPES = DOCUMENT_TYPES_V4
PROFILES = TRANSLATION_PROFILES_V1_1
if not PROFILES.exists():
    PROFILES = TRANSLATION_PROFILES_V1

OUT_DOCS = CORPUS_SIZING_BY_DOCUMENT_D1
OUT_TYPES = CORPUS_SIZING_BY_DOCUMENT_TYPE_D1
OUT_PROCESSES = CORPUS_SIZING_BY_PROCESS_D1
OUT_POLICY = CHUNKING_POLICY_RECOMMENDATIONS_D1
REPORT = CORPUS_SIZING_CHUNKING_D1_REPORT

NMT_USD_PER_MILLION = 20.0

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def as_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

def cost(chars):
    return chars / 1_000_000 * NMT_USD_PER_MILLION

def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    idx = round((len(values) - 1) * p)
    return values[int(idx)]

def size_class(chars):
    if chars <= 2_000:
        return "small_whole_document"
    if chars <= 8_000:
        return "medium_maybe_whole_or_light_chunk"
    if chars <= 32_000:
        return "large_needs_chunking"
    return "very_large_needs_structural_chunking"

def chunk_need(chars):
    if chars <= 4_500:
        return "whole_document_likely_ok"
    if chars <= 8_000:
        return "light_chunking_or_two_chunks"
    if chars <= 32_000:
        return "chunking_required"
    return "structural_chunking_required"

types = {r["document_post_id"]: r["document_type"] for r in load(DOC_TYPES)}
profiles = {r["document_type"]: r for r in load(PROFILES)}
catalog = load(CATALOG)

doc_rows = []
by_type = defaultdict(list)
by_process = defaultdict(list)

for r in catalog:
    doc_id = r["document_post_id"]
    chars = as_int(r.get("content_chars"))
    words = as_int(r.get("content_words"))
    dt = types.get(doc_id, "unknown")
    process = r.get("primary_process") or "UNSET"

    profile = profiles.get(dt, {})
    hard_max = as_int(profile.get("hard_max_chars")) or 5000
    target = as_int(profile.get("target_chunk_chars")) or 3000

    estimated_chunks = max(1, (chars + target - 1) // target) if chars else 0

    row = {
        "document_post_id": doc_id,
        "document_date": r.get("document_date", ""),
        "document_title": r.get("document_title", ""),
        "primary_process": process,
        "primary_collection": r.get("primary_collection", ""),
        "document_type": dt,
        "content_chars": chars,
        "content_words": words,
        "size_class": size_class(chars),
        "chunk_need": chunk_need(chars),
        "profile_target_chunk_chars": target,
        "profile_hard_max_chars": hard_max,
        "estimated_chunks_by_profile_target": estimated_chunks,
        "estimated_nmt_ru_en_usd": f"{cost(chars):.4f}",
        "document_url": r.get("document_url", ""),
    }
    doc_rows.append(row)
    by_type[dt].append(row)
    by_process[process].append(row)

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "primary_process", "primary_collection", "document_type",
        "content_chars", "content_words", "size_class", "chunk_need",
        "profile_target_chunk_chars", "profile_hard_max_chars",
        "estimated_chunks_by_profile_target", "estimated_nmt_ru_en_usd",
        "document_url",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(doc_rows, key=lambda x: (-x["content_chars"], x["document_post_id"])))

def write_group(path, groups, key_name):
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as f:
        fields = [
            key_name, "documents", "chars", "words",
            "avg_chars", "median_chars", "p90_chars", "p95_chars", "p99_chars", "max_chars",
            "small_docs", "medium_docs", "large_docs", "very_large_docs",
            "whole_document_likely_ok", "light_chunking_or_two_chunks",
            "chunking_required", "structural_chunking_required",
            "estimated_chunks", "estimated_nmt_ru_en_usd",
        ]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()

        for key, rows in sorted(groups.items(), key=lambda x: (-sum(r["content_chars"] for r in x[1]), x[0])):
            chars_list = [r["content_chars"] for r in rows]
            words_sum = sum(r["content_words"] for r in rows)
            class_counts = Counter(r["size_class"] for r in rows)
            need_counts = Counter(r["chunk_need"] for r in rows)
            chars_sum = sum(chars_list)
            w.writerow({
                key_name: key,
                "documents": len(rows),
                "chars": chars_sum,
                "words": words_sum,
                "avg_chars": round(chars_sum / len(rows), 2) if rows else 0,
                "median_chars": int(statistics.median(chars_list)) if chars_list else 0,
                "p90_chars": percentile(chars_list, 0.90),
                "p95_chars": percentile(chars_list, 0.95),
                "p99_chars": percentile(chars_list, 0.99),
                "max_chars": max(chars_list) if chars_list else 0,
                "small_docs": class_counts["small_whole_document"],
                "medium_docs": class_counts["medium_maybe_whole_or_light_chunk"],
                "large_docs": class_counts["large_needs_chunking"],
                "very_large_docs": class_counts["very_large_needs_structural_chunking"],
                "whole_document_likely_ok": need_counts["whole_document_likely_ok"],
                "light_chunking_or_two_chunks": need_counts["light_chunking_or_two_chunks"],
                "chunking_required": need_counts["chunking_required"],
                "structural_chunking_required": need_counts["structural_chunking_required"],
                "estimated_chunks": sum(r["estimated_chunks_by_profile_target"] for r in rows),
                "estimated_nmt_ru_en_usd": f"{cost(chars_sum):.2f}",
            })

write_group(OUT_TYPES, by_type, "document_type")
write_group(OUT_PROCESSES, by_process, "primary_process")

policy_rows = []
for dt, rows in by_type.items():
    chars_list = [r["content_chars"] for r in rows]
    p95 = percentile(chars_list, 0.95)
    med = int(statistics.median(chars_list)) if chars_list else 0
    maxc = max(chars_list) if chars_list else 0
    need_counts = Counter(r["chunk_need"] for r in rows)
    profile = profiles.get(dt, {})

    if maxc <= 4500 and need_counts["whole_document_likely_ok"] == len(rows):
        rec = "translate_whole_document"
    elif p95 <= 8000:
        rec = "light_chunking_by_paragraph_or_section"
    elif p95 <= 32000:
        rec = "standard_structural_chunking"
    else:
        rec = "strict_structural_chunking_required"

    policy_rows.append({
        "document_type": dt,
        "documents": len(rows),
        "chars": sum(chars_list),
        "median_chars": med,
        "p95_chars": p95,
        "max_chars": maxc,
        "whole_document_likely_ok": need_counts["whole_document_likely_ok"],
        "chunking_required_docs": need_counts["chunking_required"] + need_counts["structural_chunking_required"],
        "profile_strategy": profile.get("segmentation_strategy", "missing_profile"),
        "target_chunk_chars": profile.get("target_chunk_chars", "3000"),
        "soft_max_chars": profile.get("soft_max_chars", "4500"),
        "hard_max_chars": profile.get("hard_max_chars", "5000"),
        "recommendation": rec,
    })

with ensure_parent(OUT_POLICY).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_type", "documents", "chars", "median_chars", "p95_chars", "max_chars",
        "whole_document_likely_ok", "chunking_required_docs",
        "profile_strategy", "target_chunk_chars", "soft_max_chars", "hard_max_chars",
        "recommendation",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(policy_rows, key=lambda x: (-x["chars"], x["document_type"])))

total_chars = sum(r["content_chars"] for r in doc_rows)
total_chunks = sum(r["estimated_chunks_by_profile_target"] for r in doc_rows)
need_counts = Counter(r["chunk_need"] for r in doc_rows)
class_counts = Counter(r["size_class"] for r in doc_rows)

report = []
report.append("ShowTrials D1 corpus sizing + chunking diagnostic")
report.append("")
report.append(f"Documents: {len(doc_rows)}")
report.append(f"Total chars: {total_chars}")
report.append(f"Estimated NMT RU->EN cost: ${cost(total_chars):.2f}")
report.append(f"Estimated chunks by profile target: {total_chunks}")
report.append("")
report.append("Size classes:")
for k, v in class_counts.most_common():
    report.append(f"{k}\t{v}")
report.append("")
report.append("Chunk need:")
for k, v in need_counts.most_common():
    report.append(f"{k}\t{v}")
report.append("")
report.append("Top document types by chars:")
for dt, rows in sorted(by_type.items(), key=lambda x: (-sum(r["content_chars"] for r in x[1]), x[0]))[:20]:
    chars_sum = sum(r["content_chars"] for r in rows)
    report.append(f"{chars_sum}\tdocs={len(rows)}\t${cost(chars_sum):.2f}\t{dt}")
report.append("")
report.append("Outputs:")
report.append(str(OUT_DOCS))
report.append(str(OUT_TYPES))
report.append(str(OUT_PROCESSES))
report.append(str(OUT_POLICY))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOCS)
print(OUT_TYPES)
print(OUT_PROCESSES)
print(OUT_POLICY)
print(REPORT)
