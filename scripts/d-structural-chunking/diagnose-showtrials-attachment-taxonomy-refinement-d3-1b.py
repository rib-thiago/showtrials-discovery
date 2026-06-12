#!/usr/bin/env python3
"""Refine D3.1A attachment taxonomy using explicit Russian document markers."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


csv.field_size_limit(sys.maxsize)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    ATTACHMENT_TAXONOMY_D3_1A,
    ATTACHMENT_TAXONOMY_D3_1B,
    ATTACHMENT_TAXONOMY_REFINEMENT_D3_1B,
    ATTACHMENT_TAXONOMY_REFINEMENT_D3_1B_REPORT,
    SPECIAL_REPORT_ATTACHMENT_MATRIX,
    SPECIAL_REPORT_PACKAGES_D3_1,
    ensure_parent,
)

PACKAGES = SPECIAL_REPORT_PACKAGES_D3_1
MATRIX = SPECIAL_REPORT_ATTACHMENT_MATRIX
OLD_TAXONOMY = ATTACHMENT_TAXONOMY_D3_1A

OUTPUT_TAXONOMY = ATTACHMENT_TAXONOMY_D3_1B
OUTPUT_REFINEMENT = ATTACHMENT_TAXONOMY_REFINEMENT_D3_1B
OUTPUT_REPORT = ATTACHMENT_TAXONOMY_REFINEMENT_D3_1B_REPORT

ALLOWED_TYPES = {
    "interrogation_protocol",
    "confrontation_protocol",
    "statement",
    "letter",
    "memo",
    "memo_note",
    "reference_note",
    "list",
    "diary",
    "theses",
    "draft_project",
    "unknown_attachment",
}

PRIORITY = [
    "interrogation_protocol",
    "confrontation_protocol",
    "statement",
    "letter",
    "memo",
    "memo_note",
    "reference_note",
    "list",
    "diary",
    "theses",
    "draft_project",
    "unknown_attachment",
]

REFINEMENT_PATTERNS = [
    ("confrontation_protocol", "explicit очная ставка marker", r"\b(?:протокол[а-я]*\s+очной\s+ставк[а-я]*|очн[а-я]*\s+ставк[а-я]*)\b"),
    ("interrogation_protocol", "explicit допрос marker", r"\b(?:протокол[а-я]*\s+допрос[а-я]*|допрос[а-я]*)\b"),
    ("statement", "explicit заявление marker", r"\bзаявлени[а-я]*\b"),
    ("letter", "explicit письмо marker", r"\bпис(?:ьмо|ьма|ем|ьму|ьмом|ьмах|ем)\b"),
    ("memo_note", "explicit записка marker", r"\bзаписк[а-я]*\b"),
    ("memo", "explicit меморандум marker", r"\bмеморандум[а-я]*\b"),
    ("reference_note", "explicit справка marker", r"\bсправк[а-я]*\b"),
    ("list", "explicit list/opis marker", r"\b(?:спис(?:ок|ки|ка|ков|ком|ке)|опис[ьиьюя])\b"),
    ("diary", "explicit дневник marker", r"\bдневник[а-я]*\b"),
    ("theses", "explicit тезисы marker", r"\bтезис[а-я]*\b"),
    ("draft_project", "explicit draft project marker", r"\bпроект\s+(?:постановлени[а-я]*|решени[а-я]*)\b"),
]

TAXONOMY_FIELDS = ["attachment_type", "documents", "percentage_of_special_reports"]
REFINEMENT_FIELDS = [
    "document_post_id",
    "document_title",
    "old_attachment_type",
    "new_attachment_type",
    "refinement_reason",
]


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


def sorted_types(values: set[str]) -> list[str]:
    return sorted(values, key=lambda item: (PRIORITY.index(item) if item in PRIORITY else len(PRIORITY), item))


def joined(values: set[str]) -> str:
    return "|".join(sorted_types(values)) if values else ""


def percentage(count: int, total: int) -> str:
    if total <= 0:
        return "0.00"
    return f"{(count / total) * 100:.2f}"


def detect_refinements(text: str) -> tuple[set[str], list[str]]:
    found: set[str] = set()
    reasons: list[str] = []
    for attachment_type, reason, pattern in REFINEMENT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.add(attachment_type)
            reasons.append(reason)
    return found, reasons


def old_types_by_document(matrix_rows: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in matrix_rows:
        document_post_id = row.get("document_post_id", "").strip()
        attachment_type = row.get("attachment_type", "").strip()
        if document_post_id and attachment_type:
            grouped[document_post_id].add(attachment_type)
    return grouped


def main() -> int:
    package_rows = read_tsv(PACKAGES)
    matrix_rows = read_tsv(MATRIX)
    old_taxonomy_rows = read_tsv(OLD_TAXONOMY)
    total_special_reports = len(package_rows)
    old_by_doc = old_types_by_document(matrix_rows)
    old_taxonomy_types = {row.get("attachment_type", "").strip() for row in old_taxonomy_rows if row.get("attachment_type", "").strip()}

    refined_by_doc: dict[str, set[str]] = {}
    refinement_rows: list[dict[str, str]] = []
    unknown_resolved = 0

    for row in package_rows:
        document_post_id = row.get("document_post_id", "").strip()
        title = row.get("document_title", "").strip()
        markers = row.get("detected_markers", "").strip()
        raw_types = row.get("detected_attachment_types", "").strip()
        evidence_text = " ".join([title, markers, raw_types])

        old_types = set(old_by_doc.get(document_post_id, set()))
        detected_types, reasons = detect_refinements(evidence_text)
        new_types = {value for value in old_types if value != "unknown_attachment"}

        if "memo_note" in detected_types and "memo" in new_types and "memo" not in detected_types:
            new_types.remove("memo")
        if "confrontation_protocol" in detected_types and re.search(r"очн[а-я]*\s+ставк[а-я]*", title, flags=re.IGNORECASE):
            new_types.discard("interrogation_protocol")

        new_types.update(detected_types)
        if not new_types and old_types:
            new_types.add("unknown_attachment")
        refined_by_doc[document_post_id] = new_types

        if old_types != new_types:
            if "unknown_attachment" in old_types and "unknown_attachment" not in new_types:
                unknown_resolved += 1
            refinement_rows.append(
                {
                    "document_post_id": document_post_id,
                    "document_title": title,
                    "old_attachment_type": joined(old_types),
                    "new_attachment_type": joined(new_types),
                    "refinement_reason": "; ".join(reasons) if reasons else "normalized generic/unknown attachment",
                }
            )

    type_to_docs: dict[str, set[str]] = defaultdict(set)
    for document_post_id, attachment_types in refined_by_doc.items():
        for attachment_type in attachment_types:
            type_to_docs[attachment_type].add(document_post_id)

    taxonomy_rows = [
        {
            "attachment_type": attachment_type,
            "documents": str(len(document_ids)),
            "percentage_of_special_reports": percentage(len(document_ids), total_special_reports),
        }
        for attachment_type, document_ids in type_to_docs.items()
    ]
    taxonomy_rows.sort(
        key=lambda row: (
            -int(row["documents"]),
            PRIORITY.index(row["attachment_type"]) if row["attachment_type"] in PRIORITY else len(PRIORITY),
            row["attachment_type"],
        )
    )
    refinement_rows.sort(key=lambda row: int(row["document_post_id"]) if row["document_post_id"].isdigit() else 0)

    new_taxonomy_types = {row["attachment_type"] for row in taxonomy_rows}
    appeared = sorted_types(new_taxonomy_types - old_taxonomy_types)
    disappeared = sorted_types(old_taxonomy_types - new_taxonomy_types)

    write_tsv(OUTPUT_TAXONOMY, taxonomy_rows, TAXONOMY_FIELDS)
    write_tsv(OUTPUT_REFINEMENT, refinement_rows, REFINEMENT_FIELDS)

    type_counts = {row["attachment_type"]: row["documents"] for row in taxonomy_rows}
    report_lines = [
        "D3.1B Attachment Taxonomy Refinement Report",
        f"input_packages\t{PACKAGES}",
        f"input_matrix\t{MATRIX}",
        f"input_taxonomy_d3_1a\t{OLD_TAXONOMY}",
        f"taxonomy_d3_1b\t{OUTPUT_TAXONOMY}",
        f"refinement_changes\t{OUTPUT_REFINEMENT}",
        f"total_special_reports\t{total_special_reports}",
        f"documents_changed\t{len(refinement_rows)}",
        f"unknown_attachment_resolved\t{unknown_resolved}",
        f"confrontation_protocol_found\t{type_counts.get('confrontation_protocol', '0')}",
        f"statement_found\t{type_counts.get('statement', '0')}",
        f"letter_found\t{type_counts.get('letter', '0')}",
        f"memo_note_found\t{type_counts.get('memo_note', '0')}",
        f"types_appeared_after_refinement\t{'|'.join(appeared) if appeared else 'none'}",
        f"types_disappeared_after_refinement\t{'|'.join(disappeared) if disappeared else 'none'}",
        "top_attachment_types",
    ]
    for row in taxonomy_rows[:12]:
        report_lines.append(f"{row['attachment_type']}\t{row['documents']}\t{row['percentage_of_special_reports']}%")
    report_lines.append("policy\tclassification refinement only; no chunking, translation, embeddings, APIs, or blueprint changes")
    ensure_parent(OUTPUT_REPORT).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_TAXONOMY)
    print(OUTPUT_REFINEMENT)
    print(OUTPUT_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
