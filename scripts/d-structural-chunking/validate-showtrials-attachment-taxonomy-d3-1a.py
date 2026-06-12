#!/usr/bin/env python3
"""Validate D3.1A normalized special_report attachment taxonomy."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


csv.field_size_limit(sys.maxsize)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    ATTACHMENT_TAXONOMY_D3_1A,
    ATTACHMENT_TAXONOMY_D3_1A_VALIDATION,
    ATTACHMENT_TAXONOMY_D3_1A_VALIDATION_REPORT,
    SPECIAL_REPORT_ATTACHMENT_MATRIX,
    SPECIAL_REPORT_PACKAGES_D3_1,
    ensure_parent,
)

INPUT_PACKAGES = SPECIAL_REPORT_PACKAGES_D3_1
MATRIX = SPECIAL_REPORT_ATTACHMENT_MATRIX
TAXONOMY = ATTACHMENT_TAXONOMY_D3_1A
VALIDATION = ATTACHMENT_TAXONOMY_D3_1A_VALIDATION
REPORT = ATTACHMENT_TAXONOMY_D3_1A_VALIDATION_REPORT

FIELDS = ["level", "document_post_id", "check", "message"]
KNOWN_TYPES = {
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


def issue(level: str, document_post_id: str, check: str, message: str) -> dict[str, str]:
    return {
        "level": level,
        "document_post_id": document_post_id,
        "check": check,
        "message": message,
    }


def as_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    package_rows = read_tsv(INPUT_PACKAGES)
    matrix_rows = read_tsv(MATRIX)
    taxonomy_rows = read_tsv(TAXONOMY)
    issues: list[dict[str, str]] = []

    total_special_reports = len(package_rows)
    if total_special_reports == 526:
        pass
    elif total_special_reports:
        issues.append(
            issue(
                "WARN",
                "",
                "total_special_reports_available",
                f"input package count is {total_special_reports}, not the known 526",
            )
        )
    else:
        issues.append(issue("FAIL", "", "total_special_reports_available", "no package rows available"))

    for row in matrix_rows:
        document_post_id = row.get("document_post_id", "").strip()
        attachment_type = row.get("attachment_type", "").strip()
        dominant = row.get("dominant_attachment_type", "").strip()
        if not document_post_id:
            issues.append(issue("FAIL", document_post_id, "document_post_id_nonempty", "document_post_id is empty"))
        if not attachment_type:
            issues.append(issue("FAIL", document_post_id, "attachment_type_nonempty", "attachment_type is empty"))
        if not dominant:
            issues.append(
                issue("FAIL", document_post_id, "dominant_attachment_type_nonempty", "dominant_attachment_type is empty")
            )
        if attachment_type == "unknown_attachment" or dominant == "unknown_attachment":
            issues.append(issue("WARN", document_post_id, "unknown_attachment_type", "unknown_attachment present"))

    taxonomy_document_sum = 0
    for row in taxonomy_rows:
        attachment_type = row.get("attachment_type", "").strip()
        documents = as_int(row.get("documents", ""))
        pct = as_float(row.get("percentage_of_special_reports", ""))
        if not attachment_type:
            issues.append(issue("FAIL", "", "taxonomy_attachment_type_nonempty", "taxonomy attachment_type is empty"))
        elif attachment_type not in KNOWN_TYPES:
            issues.append(issue("WARN", "", "taxonomy_unknown_type", f"unknown taxonomy type: {attachment_type}"))
        if documents is None:
            issues.append(issue("FAIL", "", "taxonomy_documents_numeric", f"documents is not numeric for {attachment_type}"))
        else:
            taxonomy_document_sum += documents
        if pct is None:
            issues.append(
                issue(
                    "FAIL",
                    "",
                    "percentage_of_special_reports_numeric",
                    f"percentage is not numeric for {attachment_type}",
                )
            )
        elif pct < 0 or pct > 100:
            issues.append(
                issue(
                    "FAIL",
                    "",
                    "percentage_of_special_reports_range",
                    f"percentage out of range for {attachment_type}: {pct}",
                )
            )

    if taxonomy_document_sum <= 0:
        issues.append(issue("FAIL", "", "taxonomy_documents_sum_positive", "sum of taxonomy documents must be > 0"))

    if not issues:
        issues.append({"level": "OK", "document_post_id": "", "check": "all_checks", "message": "passed"})

    write_tsv(VALIDATION, issues, FIELDS)

    failures = sum(1 for row in issues if row["level"] == "FAIL")
    warnings = sum(1 for row in issues if row["level"] == "WARN")
    status = "OK all_checks passed" if failures == 0 and warnings == 0 else f"issues found FAIL={failures} WARN={warnings}"
    report_lines = [
        "D3.1A Attachment Taxonomy Validation Report",
        f"attachment_matrix\t{MATRIX}",
        f"taxonomy\t{TAXONOMY}",
        f"validation\t{VALIDATION}",
        f"total_special_reports\t{total_special_reports}",
        f"matrix_relations\t{len(matrix_rows)}",
        f"taxonomy_rows\t{len(taxonomy_rows)}",
        f"taxonomy_documents_sum\t{taxonomy_document_sum}",
        f"failures\t{failures}",
        f"warnings\t{warnings}",
        status,
    ]
    ensure_parent(REPORT).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(VALIDATION)
    print(REPORT)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
