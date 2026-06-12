#!/usr/bin/env python3
"""Package D2.1 structural samples for human review."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


csv.field_size_limit(sys.maxsize)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    STRUCTURAL_SAMPLES_D2_1_INDEX,
    STRUCTURAL_SAMPLES_D2_2_REPORT,
    STRUCTURAL_SAMPLES_D2_2_REVIEW_INDEX,
    ensure_parent,
)

INPUT_INDEX = STRUCTURAL_SAMPLES_D2_1_INDEX
OUTPUT_INDEX = STRUCTURAL_SAMPLES_D2_2_REVIEW_INDEX
OUTPUT_REPORT = STRUCTURAL_SAMPLES_D2_2_REPORT

FIELDS = [
    "document_type",
    "sample_no",
    "document_post_id",
    "content_chars",
    "primary_process",
    "document_title",
    "sample_path",
    "review_priority",
    "expected_structure",
    "review_questions",
    "suggested_chunk_unit",
    "notes",
]

STRUCTURE_POLICY = {
    "interrogation_protocol": (
        "header + question/answer blocks + signature",
        "question_answer_block",
    ),
    "confrontation_protocol": (
        "header + alternating confrontation exchanges + signature",
        "speaker_or_exchange_turn",
    ),
    "session_transcript": (
        "session header + speaker turns + procedural notes",
        "speaker_turn_or_procedural_block",
    ),
    "conversation_recording": (
        "recording header + speaker turns + pauses/notes + signature",
        "speaker_turn_or_conversation_note",
    ),
    "special_report": (
        "classification/header + recipient/sender + body + attached materials",
        "header_body_attachment_block",
    ),
    "letter": (
        "addressee/salutation + body + signature + attachments if present",
        "paragraph_or_letter_section",
    ),
    "statement": (
        "header/addressee + narrative or numbered statement + signature",
        "paragraph_or_numbered_section",
    ),
    "testimony": (
        "header + narrative testimony or Q/A remnants + signature",
        "narrative_paragraph_or_qa_block",
    ),
    "memo_note": (
        "header + memo body + attachments + signature",
        "memo_section_or_attachment_block",
    ),
    "list": (
        "list title/header + records/items",
        "list_item_group",
    ),
    "indictment": (
        "header + legal sections + charges + conclusion",
        "legal_section_or_charge_block",
    ),
    "press_summary": (
        "press/source header + report sections + paragraphs",
        "press_item_or_paragraph_block",
    ),
    "reference_note": (
        "header + factual sections + evidence extracts",
        "factual_section_or_extract",
    ),
    "biographical_article": (
        "article title + prose sections + chronology",
        "article_section_or_paragraph_block",
    ),
}

HIGH_PRIORITY = {
    "special_report",
    "session_transcript",
    "interrogation_protocol",
    "conversation_recording",
}
MEDIUM_PRIORITY = {
    "letter",
    "statement",
    "testimony",
    "confrontation_protocol",
    "memo_note",
    "list",
    "indictment",
    "reference_note",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def priority_for(document_type: str) -> str:
    if document_type in HIGH_PRIORITY:
        return "high"
    if document_type in MEDIUM_PRIORITY:
        return "medium"
    return "low"


def policy_for(document_type: str) -> tuple[str, str]:
    return STRUCTURE_POLICY.get(
        document_type,
        ("document header + prose sections or records + closing matter", "section_or_paragraph_block"),
    )


def questions_for(document_type: str) -> str:
    questions = ["Where does the true body begin?", "Can chunks preserve section boundaries?"]
    if document_type in {"session_transcript", "conversation_recording", "confrontation_protocol"}:
        questions.insert(1, "Are speaker turns explicit?")
    if document_type in {"special_report", "letter", "memo_note", "statement", "reference_note"}:
        questions.insert(1, "Are attachments embedded?")
    if document_type in {"interrogation_protocol", "testimony"}:
        questions.insert(1, "Are Q/A blocks explicit or only lexical mentions?")
    if document_type == "list":
        questions.insert(1, "Where does each record begin and end?")
    return " | ".join(dict.fromkeys(questions))


def sample_note(sample_path: str, content_chars: str) -> str:
    path = Path(sample_path)
    notes: list[str] = []
    if not path.exists():
        notes.append("sample file missing")
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        actual_chars = len(text)
        notes.append(f"sample_file_chars={actual_chars}")
        if content_chars and content_chars.isdigit() and actual_chars != int(content_chars):
            notes.append("index_char_count_differs_from_file")
    notes.append("human review aid only; do not infer structure from lexical matches alone")
    return "; ".join(notes)


def main() -> int:
    if not INPUT_INDEX.exists():
        raise SystemExit(f"Missing input: {INPUT_INDEX}")

    input_rows = read_tsv(INPUT_INDEX)
    output_rows: list[dict[str, str]] = []
    counts = Counter()

    for row in input_rows:
        document_type = row.get("document_type", "").strip()
        expected_structure, suggested_chunk_unit = policy_for(document_type)
        review_priority = priority_for(document_type)
        counts[document_type] += 1
        output_rows.append(
            {
                "document_type": document_type,
                "sample_no": row.get("sample_no", "").strip(),
                "document_post_id": row.get("document_post_id", "").strip(),
                "content_chars": row.get("content_chars", "").strip(),
                "primary_process": row.get("primary_process", "").strip(),
                "document_title": row.get("document_title", "").strip(),
                "sample_path": row.get("sample_path", "").strip(),
                "review_priority": review_priority,
                "expected_structure": expected_structure,
                "review_questions": questions_for(document_type),
                "suggested_chunk_unit": suggested_chunk_unit,
                "notes": sample_note(row.get("sample_path", "").strip(), row.get("content_chars", "").strip()),
            }
        )

    write_tsv(OUTPUT_INDEX, output_rows, FIELDS)

    priority_counts = Counter(row["review_priority"] for row in output_rows)
    report_lines = [
        "D2.2 Structural Sample Packaging Report",
        f"input_index\t{INPUT_INDEX}",
        f"review_index\t{OUTPUT_INDEX}",
        f"samples\t{len(output_rows)}",
        f"document_types\t{len(counts)}",
        f"priority_high\t{priority_counts.get('high', 0)}",
        f"priority_medium\t{priority_counts.get('medium', 0)}",
        f"priority_low\t{priority_counts.get('low', 0)}",
        "policy\thuman review aid only; no automatic structural decision",
        "samples_by_type",
    ]
    for document_type, count in sorted(counts.items()):
        report_lines.append(f"{document_type}\t{count}\t{priority_for(document_type)}")
    ensure_parent(OUTPUT_REPORT).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_INDEX)
    print(OUTPUT_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
