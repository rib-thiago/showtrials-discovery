#!/usr/bin/env python3
"""Consolidate ShowTrials chunking blueprint v1.1 from discovery outputs."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


csv.field_size_limit(sys.maxsize)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    ATTACHMENT_TAXONOMY_D3_1B,
    ATTACHMENT_TAXONOMY_REFINEMENT_D3_1B,
    CHUNKING_BLUEPRINT_V1,
    CHUNKING_BLUEPRINT_V1_1,
    CHUNKING_BLUEPRINT_V1_1_REPORT,
    CHUNKING_BLUEPRINT_V1_REPORT,
    CHUNKING_POLICY_V1_1,
    STRUCTURAL_CHUNKING_D2_BY_TYPE,
    ensure_parent,
)

BLUEPRINT_V1 = CHUNKING_BLUEPRINT_V1
D2_BY_TYPE = STRUCTURAL_CHUNKING_D2_BY_TYPE
ATTACHMENT_TAXONOMY = ATTACHMENT_TAXONOMY_D3_1B
ATTACHMENT_REFINEMENT = ATTACHMENT_TAXONOMY_REFINEMENT_D3_1B
BLUEPRINT_V1_REPORT = CHUNKING_BLUEPRINT_V1_REPORT

OUTPUT_BLUEPRINT = CHUNKING_BLUEPRINT_V1_1
OUTPUT_POLICY = CHUNKING_POLICY_V1_1
OUTPUT_REPORT = CHUNKING_BLUEPRINT_V1_1_REPORT

FIELDS = [
    "document_type",
    "documents",
    "chars",
    "primary_chunk_unit",
    "secondary_chunk_unit",
    "target_chunk_chars",
    "soft_max_chars",
    "hard_max_chars",
    "preserve_boundaries",
    "package_detection_required",
    "attachment_first_strategy",
    "manual_review_required",
    "translation_ready",
    "chunking_confidence",
    "policy_version",
    "notes",
]

POLICY_VERSION = "v1.1"

OVERRIDES = {
    "interrogation_protocol": {
        "primary_chunk_unit": "question_answer_block",
        "preserve_boundaries": "question_answer_pairs",
        "translation_ready": "yes",
        "chunking_confidence": "high",
        "manual_review_required": "sample_review",
        "notes": "D2/D2.2 confirmed interrogation_protocol as Q/A unit",
    },
    "confrontation_protocol": {
        "primary_chunk_unit": "confrontation_exchange",
        "secondary_chunk_unit": "speaker_or_exchange_turn",
        "preserve_boundaries": "exchange_boundaries",
        "translation_ready": "yes",
        "chunking_confidence": "high",
        "manual_review_required": "sample_review",
        "notes": "D3.1B distinguishes confrontation_protocol from ordinary interrogation attachments",
    },
    "session_transcript": {
        "primary_chunk_unit": "speaker_turn",
        "secondary_chunk_unit": "speaker_turn_group",
        "preserve_boundaries": "speaker_boundaries",
        "translation_ready": "yes",
        "chunking_confidence": "high",
        "manual_review_required": "yes",
        "notes": "D2/D2.2 confirmed session transcript speaker turns",
    },
    "conversation_recording": {
        "primary_chunk_unit": "conversation_segment",
        "secondary_chunk_unit": "speaker_turn",
        "preserve_boundaries": "timestamp_and_event_boundaries",
        "translation_ready": "yes",
        "chunking_confidence": "high",
        "manual_review_required": "yes",
        "notes": "D2/D2.2 confirmed timestamp, speaker, and event boundaries",
    },
    "special_report": {
        "primary_chunk_unit": "document_package",
        "secondary_chunk_unit": "attachment",
        "preserve_boundaries": "attachment_boundaries",
        "package_detection_required": "yes",
        "attachment_first_strategy": "yes",
        "manual_review_required": "yes",
        "translation_ready": "conditional",
        "chunking_confidence": "high",
        "notes": "special_report acts as documentary container",
    },
    "letter": {
        "primary_chunk_unit": "letter_section",
        "secondary_chunk_unit": "paragraph",
        "preserve_boundaries": "salutation_body_signature",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B attachment taxonomy added letter as explicit attached document type",
    },
    "statement": {
        "primary_chunk_unit": "statement_section",
        "secondary_chunk_unit": "paragraph",
        "preserve_boundaries": "statement_sections",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B attachment taxonomy added statement as explicit attached document type",
    },
    "memo_note": {
        "primary_chunk_unit": "memo_section",
        "secondary_chunk_unit": "paragraph",
        "preserve_boundaries": "memo_sections",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B refined zapisка attachments to memo_note",
    },
    "reference_note": {
        "primary_chunk_unit": "reference_section",
        "secondary_chunk_unit": "paragraph",
        "preserve_boundaries": "reference_sections",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B confirmed reference_note attachments",
    },
    "list": {
        "primary_chunk_unit": "list_item_group",
        "secondary_chunk_unit": "list_item",
        "preserve_boundaries": "list_item_boundaries",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B confirmed list attachments",
    },
    "diary": {
        "primary_chunk_unit": "diary_entry",
        "secondary_chunk_unit": "paragraph",
        "preserve_boundaries": "diary_entry_boundaries",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B confirmed diary attachments inside special_report packages",
    },
    "theses": {
        "primary_chunk_unit": "thesis_block",
        "secondary_chunk_unit": "paragraph",
        "preserve_boundaries": "thesis_boundaries",
        "translation_ready": "yes",
        "chunking_confidence": "medium",
        "notes": "D3.1B confirmed theses attachments inside special_report packages",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing input: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cap_hard(value: str) -> str:
    try:
        return str(min(int(value), 5000))
    except (TypeError, ValueError):
        return "5000"


def base_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "document_type": row.get("document_type", "").strip(),
        "documents": row.get("documents", "").strip(),
        "chars": row.get("chars", "").strip(),
        "primary_chunk_unit": row.get("primary_chunk_unit", "").strip(),
        "secondary_chunk_unit": row.get("secondary_chunk_unit", "").strip(),
        "target_chunk_chars": row.get("target_chunk_chars", "").strip(),
        "soft_max_chars": row.get("soft_max_chars", "").strip(),
        "hard_max_chars": cap_hard(row.get("hard_max_chars", "")),
        "preserve_boundaries": row.get("preserve_boundaries", "").strip(),
        "package_detection_required": "no",
        "attachment_first_strategy": "no",
        "manual_review_required": row.get("manual_review_required", "").strip() or "sample_review",
        "translation_ready": "review_required",
        "chunking_confidence": "medium" if row.get("blueprint_status", "").strip() == "ready_for_human_review" else "low",
        "policy_version": POLICY_VERSION,
        "notes": row.get("notes", "").strip() or "carried forward from blueprint v1",
    }


def apply_overrides(output: dict[str, str], taxonomy_types: set[str]) -> dict[str, str]:
    document_type = output["document_type"]
    override = OVERRIDES.get(document_type)
    if not override and document_type == "draft_project" and "draft_project" in taxonomy_types:
        override = {
            "primary_chunk_unit": "draft_project_section",
            "secondary_chunk_unit": "paragraph",
            "preserve_boundaries": "draft_project_sections",
            "translation_ready": "yes",
            "chunking_confidence": "medium",
            "notes": "D3.1B confirmed draft_project attachments inside special_report packages",
        }
    if override:
        output.update(override)
    return output


def write_policy(path: Path, taxonomy_rows: list[dict[str, str]], refinement_rows: list[dict[str, str]]) -> None:
    taxonomy_summary = ", ".join(
        f"{row.get('attachment_type')}={row.get('documents')}"
        for row in taxonomy_rows
        if row.get("attachment_type")
    )
    text = f"""ShowTrials Chunking Policy v1.1

1. Semantic unit
A semantic unit is the smallest document-native block that should remain intact for translation and retrieval. It is not just a character window. It can be a question/answer pair, a confrontation exchange, a speaker turn, a conversation event segment, a letter section, or an attachment inside a documentary package.

2. Why chunking is not size-only
Size-only chunking can split a question from its answer, a speaker label from the utterance, a list item from its record, or a cover note from the attachment it introduces. v1.1 still keeps hard_max_chars <= 5000, but size limits are applied after structural boundaries are identified.

3. Core document differences
interrogation_protocol uses question_answer_block because the stable semantic unit is the Q/A pair.
confrontation_protocol uses confrontation_exchange because the exchange boundary between confronted participants is more important than a generic Q/A token.
session_transcript uses speaker_turn because courtroom/session meaning follows speaker boundaries and procedural notes.
conversation_recording uses conversation_segment because timestamps, speakers, and event notes define the record.
special_report uses document_package because it often contains a cover communication plus one or more attached documentary units.

4. Why special_report is document_package
D3.1A and D3.1B showed that special_report is usually a container: interrogation_protocol=448, memo_note=51, theses=42, list=40, reference_note=37, statement=30, confrontation_protocol=17, letter=10, diary=8, draft_project=1. Treating this as a simple document would mix cover note and attachments.

5. Attachment detection before chunking
Attachment detection runs before chunking so the builder can first separate cover material from attached protocols, statements, letters, lists, notes, diaries, theses, and draft projects. Each attachment can then use its own structural policy.

6. Translation cost control
Structural chunking reduces translation cost by avoiding duplicated context padding, preventing failed oversize translation units, and allowing short cover notes or lists to be translated only as needed. It also prevents paying to translate incoherent fragments that must be reprocessed later.

7. Future RAG support
Future retrieval should cite coherent documentary units, not arbitrary character spans. v1.1 makes future RAG evidence cleaner by keeping Q/A pairs, speaker turns, exchanges, attachments, list records, and document package boundaries available as metadata.

Discovery basis
D1 sizing established corpus scale. D2/D2.2 separated real structural units from lexical false positives. D3.1A normalized special_report attachments. D3.1B refined the taxonomy before this consolidation.
Attachment taxonomy v1.1: {taxonomy_summary}
Refinement changes recorded: {len(refinement_rows)}
"""
    ensure_parent(path).write_text(text, encoding="utf-8")


def main() -> int:
    v1_rows = read_tsv(BLUEPRINT_V1)
    read_tsv(D2_BY_TYPE)
    taxonomy_rows = read_tsv(ATTACHMENT_TAXONOMY)
    refinement_rows = read_tsv(ATTACHMENT_REFINEMENT)
    if not BLUEPRINT_V1_REPORT.exists():
        raise SystemExit(f"Missing input: {BLUEPRINT_V1_REPORT}")

    taxonomy_types = {row.get("attachment_type", "").strip() for row in taxonomy_rows}
    output_rows: list[dict[str, str]] = []
    revised_types = set()
    for row in v1_rows:
        output = base_row(row)
        before = dict(output)
        output = apply_overrides(output, taxonomy_types)
        if output != before:
            revised_types.add(output["document_type"])
        output_rows.append(output)

    write_tsv(OUTPUT_BLUEPRINT, output_rows, FIELDS)
    write_policy(OUTPUT_POLICY, taxonomy_rows, refinement_rows)

    counts = Counter(row["translation_ready"] for row in output_rows)
    confidence_counts = Counter(row["chunking_confidence"] for row in output_rows)
    future_review = sum(
        1
        for row in output_rows
        if row["translation_ready"] == "review_required" or row["chunking_confidence"] in {"low", "medium"}
    )
    report_lines = [
        "Chunking Blueprint v1.1 Consolidation Report",
        f"blueprint_v1\t{BLUEPRINT_V1}",
        f"d2_by_type\t{D2_BY_TYPE}",
        f"attachment_taxonomy_d3_1b\t{ATTACHMENT_TAXONOMY}",
        f"attachment_refinement_d3_1b\t{ATTACHMENT_REFINEMENT}",
        f"blueprint_v1_1\t{OUTPUT_BLUEPRINT}",
        f"policy_doc\t{OUTPUT_POLICY}",
        f"document_types_total\t{len(output_rows)}",
        f"document_types_revised\t{len(revised_types)}",
        f"translation_ready_yes\t{counts.get('yes', 0)}",
        f"translation_ready_conditional\t{counts.get('conditional', 0)}",
        f"translation_ready_review_required\t{counts.get('review_required', 0)}",
        f"chunking_confidence_high\t{confidence_counts.get('high', 0)}",
        f"future_review_dependent\t{future_review}",
        f"policy_version\t{POLICY_VERSION}",
    ]
    ensure_parent(OUTPUT_REPORT).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_BLUEPRINT)
    print(OUTPUT_POLICY)
    print(OUTPUT_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
