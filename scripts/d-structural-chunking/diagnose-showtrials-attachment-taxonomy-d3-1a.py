#!/usr/bin/env python3
"""Normalize special_report attachment taxonomy from D3.1 package diagnostics."""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
INPUT_PACKAGES = ROOT / "showtrials_special_report_packages_d3_1.tsv"

OUTPUT_MATRIX = ROOT / "showtrials_special_report_attachment_matrix.tsv"
OUTPUT_TAXONOMY = ROOT / "showtrials_attachment_taxonomy_d3_1a.tsv"
OUTPUT_CROSSWALK = ROOT / "showtrials_attachment_taxonomy_crosswalk_d3_1a.tsv"
OUTPUT_REPORT = ROOT / "showtrials_attachment_taxonomy_d3_1a_report.txt"

VALID_TYPES = {
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

MATRIX_FIELDS = [
    "document_post_id",
    "document_title",
    "primary_process",
    "package_likelihood",
    "attachment_type",
    "dominant_attachment_type",
]

TAXONOMY_FIELDS = [
    "attachment_type",
    "documents",
    "percentage_of_special_reports",
    "strong_packages",
    "possible_packages",
    "none_packages",
]

CROSSWALK_FIELDS = ["raw_detected_attachment_types", "normalized_attachment_type"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing input: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_raw_types(raw: str) -> list[str]:
    values = []
    for part in (raw or "").split("|"):
        value = part.strip()
        if value and value != "-":
            values.append(value)
    return values


def normalize_types(raw: str) -> list[str]:
    normalized = []
    saw_nonempty = False
    for value in split_raw_types(raw):
        saw_nonempty = True
        if value == "generic_attachment":
            continue
        if value in VALID_TYPES:
            normalized.append(value)
        else:
            normalized.append("unknown_attachment")
    normalized = sorted(set(normalized), key=lambda item: PRIORITY.index(item) if item in PRIORITY else len(PRIORITY))
    if saw_nonempty and not normalized:
        return ["unknown_attachment"]
    return normalized


def dominant_type(normalized: list[str]) -> str:
    if not normalized:
        return ""
    normalized_set = set(normalized)
    for candidate in PRIORITY:
        if candidate in normalized_set:
            return candidate
    return "unknown_attachment"


def percentage(count: int, total: int) -> str:
    if total <= 0:
        return "0.00"
    return f"{(count / total) * 100:.2f}"


def main() -> int:
    package_rows = read_tsv(INPUT_PACKAGES)
    total_special_reports = len(package_rows)

    matrix_rows: list[dict[str, str]] = []
    crosswalk: dict[str, str] = {}
    taxonomy_doc_ids: dict[str, set[str]] = defaultdict(set)
    taxonomy_likelihoods: dict[str, Counter[str]] = defaultdict(Counter)
    combination_counts: Counter[str] = Counter()
    dominant_counts: Counter[str] = Counter()

    for row in package_rows:
        document_post_id = row.get("document_post_id", "").strip()
        raw = row.get("detected_attachment_types", "").strip()
        package_likelihood = row.get("package_likelihood", "").strip()
        normalized = normalize_types(raw)
        dominant = dominant_type(normalized)
        combination_counts[raw or "-"] += 1
        if raw or normalized:
            crosswalk[raw or "-"] = dominant or "none"
        if not normalized:
            continue
        dominant_counts[dominant] += 1
        for attachment_type in normalized:
            taxonomy_doc_ids[attachment_type].add(document_post_id)
            taxonomy_likelihoods[attachment_type][package_likelihood] += 1
            matrix_rows.append(
                {
                    "document_post_id": document_post_id,
                    "document_title": row.get("document_title", "").strip(),
                    "primary_process": row.get("primary_process", "").strip(),
                    "package_likelihood": package_likelihood,
                    "attachment_type": attachment_type,
                    "dominant_attachment_type": dominant,
                }
            )

    matrix_rows.sort(
        key=lambda row: (
            int(row["document_post_id"]) if row["document_post_id"].isdigit() else 0,
            PRIORITY.index(row["attachment_type"]) if row["attachment_type"] in PRIORITY else len(PRIORITY),
        )
    )

    taxonomy_rows: list[dict[str, str]] = []
    for attachment_type, doc_ids in taxonomy_doc_ids.items():
        counts = taxonomy_likelihoods[attachment_type]
        taxonomy_rows.append(
            {
                "attachment_type": attachment_type,
                "documents": str(len(doc_ids)),
                "percentage_of_special_reports": percentage(len(doc_ids), total_special_reports),
                "strong_packages": str(counts.get("strong", 0)),
                "possible_packages": str(counts.get("possible", 0)),
                "none_packages": str(counts.get("none", 0)),
            }
        )
    taxonomy_rows.sort(
        key=lambda row: (
            -int(row["documents"]),
            PRIORITY.index(row["attachment_type"]) if row["attachment_type"] in PRIORITY else len(PRIORITY),
            row["attachment_type"],
        )
    )

    crosswalk_rows = [
        {"raw_detected_attachment_types": raw, "normalized_attachment_type": normalized}
        for raw, normalized in sorted(crosswalk.items())
    ]

    write_tsv(OUTPUT_MATRIX, matrix_rows, MATRIX_FIELDS)
    write_tsv(OUTPUT_TAXONOMY, taxonomy_rows, TAXONOMY_FIELDS)
    write_tsv(OUTPUT_CROSSWALK, crosswalk_rows, CROSSWALK_FIELDS)

    report_lines = [
        "D3.1A Attachment Taxonomy Normalization Report",
        f"input_packages\t{INPUT_PACKAGES}",
        f"attachment_matrix\t{OUTPUT_MATRIX}",
        f"taxonomy\t{OUTPUT_TAXONOMY}",
        f"crosswalk\t{OUTPUT_CROSSWALK}",
        f"total_special_reports\t{total_special_reports}",
        f"total_attachment_relations\t{len(matrix_rows)}",
        f"unique_attachment_types\t{len(taxonomy_rows)}",
        "top_attachment_types",
    ]
    for row in taxonomy_rows[:10]:
        report_lines.append(
            f"{row['attachment_type']}\t{row['documents']}\t{row['percentage_of_special_reports']}%"
        )
    report_lines.append("top_combinations")
    for raw, count in combination_counts.most_common(10):
        report_lines.append(f"{raw or '-'}\t{count}")
    report_lines.append("dominant_attachment_types")
    for attachment_type, count in dominant_counts.most_common():
        report_lines.append(f"{attachment_type}\t{count}\t{percentage(count, total_special_reports)}%")
    report_lines.append("policy\tgeneric_attachment ignored as a document type; generic-only packages become unknown_attachment")
    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_MATRIX)
    print(OUTPUT_TAXONOMY)
    print(OUTPUT_CROSSWALK)
    print(OUTPUT_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
