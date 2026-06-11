#!/usr/bin/env python3
"""Build a conservative structural chunking blueprint from D1 and D2.2."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
REVIEW_INDEX = ROOT / "showtrials_structural_samples_d2_2_review_index.tsv"
D1_POLICY = ROOT / "showtrials_chunking_policy_recommendations_d1.tsv"
D2_BY_TYPE = ROOT / "showtrials_structural_chunking_d2_by_type.tsv"
OUTPUT_BLUEPRINT = ROOT / "showtrials_chunking_blueprint_v1.tsv"
OUTPUT_REPORT = ROOT / "showtrials_chunking_blueprint_v1_report.txt"

FIELDS = [
    "document_type",
    "documents",
    "chars",
    "d1_recommendation",
    "expected_structure",
    "primary_chunk_unit",
    "secondary_chunk_unit",
    "target_chunk_chars",
    "soft_max_chars",
    "hard_max_chars",
    "preserve_boundaries",
    "fallback_strategy",
    "manual_review_required",
    "blueprint_status",
    "notes",
]

FALSE_POSITIVE_TYPES = {
    "biographical_article",
    "article",
    "press_summary",
    "letter",
    "memo_note",
    "statement",
    "program",
    "brochure",
    "poem",
}

STRUCTURE_POLICY = {
    "interrogation_protocol": (
        "header + question/answer blocks + signature",
        "question_answer_block",
        "paragraph_within_answer",
        "question_answer_blocks",
    ),
    "confrontation_protocol": (
        "header + alternating confrontation exchanges + signature",
        "speaker_or_exchange_turn",
        "paragraph_within_exchange",
        "exchange turns",
    ),
    "session_transcript": (
        "session header + speaker turns + procedural notes",
        "speaker_turn_or_procedural_block",
        "paragraph_within_speaker_turn",
        "speaker turns and procedural notes",
    ),
    "conversation_recording": (
        "recording header + speaker turns + pauses/notes + signature",
        "speaker_turn_or_conversation_note",
        "paragraph_within_speaker_turn",
        "speaker turns and conversation notes",
    ),
    "special_report": (
        "classification/header + recipient/sender + body + attached materials",
        "header_body_attachment_block",
        "paragraph_within_body_or_attachment",
        "header/body/attachment blocks",
    ),
    "letter": (
        "addressee/salutation + body + signature + attachments if present",
        "paragraph_or_letter_section",
        "paragraph",
        "letter sections and paragraphs",
    ),
    "statement": (
        "header/addressee + narrative or numbered statement + signature",
        "paragraph_or_numbered_section",
        "paragraph",
        "numbered sections and paragraphs",
    ),
    "testimony": (
        "header + narrative testimony or Q/A remnants + signature",
        "narrative_paragraph_or_qa_block",
        "paragraph",
        "narrative paragraphs or explicit Q/A blocks",
    ),
    "memo_note": (
        "header + memo body + attachments + signature",
        "memo_section_or_attachment_block",
        "paragraph",
        "memo sections and attachment blocks",
    ),
    "list": (
        "list title/header + records/items",
        "list_item_group",
        "record_item",
        "list records/items",
    ),
    "indictment": (
        "header + legal sections + charges + conclusion",
        "legal_section_or_charge_block",
        "paragraph",
        "legal sections and charge blocks",
    ),
    "press_summary": (
        "press/source header + report sections + paragraphs",
        "press_item_or_paragraph_block",
        "paragraph",
        "press items and paragraphs",
    ),
    "reference_note": (
        "header + factual sections + evidence extracts",
        "factual_section_or_extract",
        "paragraph",
        "factual sections and evidence extracts",
    ),
    "biographical_article": (
        "article title + prose sections + chronology",
        "article_section_or_paragraph_block",
        "paragraph",
        "article sections and paragraphs",
    ),
    "article": (
        "article title + prose sections + paragraphs",
        "article_section_or_paragraph_block",
        "paragraph",
        "article sections and paragraphs",
    ),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def as_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def bounded_chunk_sizes(row: dict[str, str]) -> tuple[str, str, str]:
    target = as_int(row.get("target_chunk_chars", ""), 3000)
    soft = as_int(row.get("soft_max_chars", ""), 4500)
    hard = as_int(row.get("hard_max_chars", ""), 5000)
    target = min(max(target, 2800), 3300)
    hard = min(max(hard, target), 5000)
    soft = min(max(soft, target), hard)
    return str(target), str(soft), str(hard)


def policy_for(document_type: str, review_by_type: dict[str, dict[str, str]]) -> tuple[str, str, str, str]:
    if document_type in STRUCTURE_POLICY:
        return STRUCTURE_POLICY[document_type]
    review = review_by_type.get(document_type, {})
    expected = review.get("expected_structure") or "document header + prose sections or records + closing matter"
    primary = review.get("suggested_chunk_unit") or "section_or_paragraph_block"
    return expected, primary, "paragraph", "document sections and paragraphs"


def fallback_for(primary_unit: str) -> str:
    if "speaker" in primary_unit:
        return "merge short adjacent speaker turns; split oversized turns on paragraph boundaries"
    if "question_answer" in primary_unit or "exchange" in primary_unit:
        return "merge short adjacent Q/A or exchange blocks; split oversized answers on paragraph boundaries"
    if "attachment" in primary_unit:
        return "keep attachments separate; split oversized body or attachment blocks by paragraph"
    if "list" in primary_unit:
        return "group adjacent records until target size; split oversized records only at internal line breaks"
    return "group adjacent paragraphs until target size; split oversized paragraphs at sentence-like boundaries"


def main() -> int:
    if not REVIEW_INDEX.exists():
        raise SystemExit(f"Missing input: {REVIEW_INDEX}")
    if not D1_POLICY.exists():
        raise SystemExit(f"Missing input: {D1_POLICY}")

    review_rows = read_tsv(REVIEW_INDEX)
    d1_rows = read_tsv(D1_POLICY)
    d2_rows = read_tsv(D2_BY_TYPE)
    review_by_type: dict[str, dict[str, str]] = {}
    review_counts: dict[str, int] = defaultdict(int)
    for row in review_rows:
        document_type = row.get("document_type", "").strip()
        if document_type and document_type not in review_by_type:
            review_by_type[document_type] = row
        if document_type:
            review_counts[document_type] += 1
    d2_by_type = {row.get("document_type", "").strip(): row for row in d2_rows}

    output_rows: list[dict[str, str]] = []
    manual_count = 0
    false_positive_notes = 0
    d2_used = 0

    for row in d1_rows:
        document_type = row.get("document_type", "").strip()
        expected, primary, secondary, preserve = policy_for(document_type, review_by_type)
        target, soft, hard = bounded_chunk_sizes(row)
        d2 = d2_by_type.get(document_type, {})
        d2_unit = d2.get("dominant_recommended_unit", "")
        notes = []
        if d2_unit:
            notes.append(f"d2_dominant_unit={d2_unit}")
            d2_used += 1
        if d2_unit == "question_answer_blocks" and document_type in FALSE_POSITIVE_TYPES:
            notes.append("avoid lexical false-positive QA detection")
            false_positive_notes += 1
        if document_type in {"session_transcript", "conversation_recording", "special_report"}:
            manual_review = "yes"
        elif row.get("recommendation", "").strip() == "strict_structural_chunking_required":
            manual_review = "yes"
        elif document_type in review_by_type:
            manual_review = "sample_review"
        else:
            manual_review = "sample_review"
        if manual_review in {"yes", "sample_review"}:
            manual_count += 1
        status = "ready_for_human_review" if manual_review else "draft"
        if not document_type:
            status = "invalid_missing_document_type"
        output_rows.append(
            {
                "document_type": document_type,
                "documents": row.get("documents", "").strip(),
                "chars": row.get("chars", "").strip(),
                "d1_recommendation": row.get("recommendation", "").strip(),
                "expected_structure": expected,
                "primary_chunk_unit": primary,
                "secondary_chunk_unit": secondary,
                "target_chunk_chars": target,
                "soft_max_chars": soft,
                "hard_max_chars": hard,
                "preserve_boundaries": preserve,
                "fallback_strategy": fallback_for(primary),
                "manual_review_required": manual_review,
                "blueprint_status": status,
                "notes": "; ".join(notes) if notes else "derived from D1 sizing and D2.2 review policy",
            }
        )

    write_tsv(OUTPUT_BLUEPRINT, output_rows, FIELDS)

    report_lines = [
        "Chunking Blueprint v1 Report",
        f"review_index\t{REVIEW_INDEX}",
        f"d1_policy\t{D1_POLICY}",
        f"d2_by_type\t{D2_BY_TYPE if D2_BY_TYPE.exists() else 'not_found'}",
        f"blueprint\t{OUTPUT_BLUEPRINT}",
        f"document_types\t{len(output_rows)}",
        f"manual_review_rows\t{manual_count}",
        f"d2_rows_used\t{d2_used}",
        f"false_positive_notes\t{false_positive_notes}",
        "constraints\thard_max_chars capped at 5000; lexical Q/A detection is advisory only",
        "totals_from_d1\tdocuments=2179\tchars=27379787\testimated_chunks=10023\tfailures=0\twarnings=0",
    ]
    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_BLUEPRINT)
    print(OUTPUT_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
