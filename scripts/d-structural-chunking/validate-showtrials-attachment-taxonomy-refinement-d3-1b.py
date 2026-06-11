#!/usr/bin/env python3
"""Validate D3.1B refined attachment taxonomy outputs."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
TAXONOMY = ROOT / "showtrials_attachment_taxonomy_d3_1b.tsv"
REFINEMENT = ROOT / "showtrials_attachment_taxonomy_refinement_d3_1b.tsv"
VALIDATION = ROOT / "showtrials_attachment_taxonomy_refinement_d3_1b_validation.tsv"
REPORT = ROOT / "showtrials_attachment_taxonomy_refinement_d3_1b_validation_report.txt"

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

VALIDATION_FIELDS = ["level", "document_post_id", "check", "message"]


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


def issue(level: str, document_post_id: str, check: str, message: str) -> dict[str, str]:
    return {
        "level": level,
        "document_post_id": document_post_id,
        "check": check,
        "message": message,
    }


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def split_types(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]


def main() -> int:
    taxonomy_rows = read_tsv(TAXONOMY)
    refinement_rows = read_tsv(REFINEMENT)
    issues: list[dict[str, str]] = []

    for row in taxonomy_rows:
        attachment_type = row.get("attachment_type", "").strip()
        pct = as_float(row.get("percentage_of_special_reports", ""))
        if not attachment_type:
            issues.append(issue("FAIL", "", "attachment_type_nonempty", "taxonomy attachment_type is empty"))
        elif attachment_type not in ALLOWED_TYPES:
            issues.append(issue("WARN", "", "unexpected_attachment_type", f"unexpected taxonomy type: {attachment_type}"))
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

    for row in refinement_rows:
        document_post_id = row.get("document_post_id", "").strip()
        if not document_post_id:
            issues.append(issue("FAIL", document_post_id, "document_post_id_nonempty", "document_post_id is empty"))
        new_types = split_types(row.get("new_attachment_type", ""))
        if not new_types:
            issues.append(issue("FAIL", document_post_id, "new_attachment_type_nonempty", "new_attachment_type is empty"))
        for attachment_type in new_types:
            if attachment_type not in ALLOWED_TYPES:
                issues.append(
                    issue(
                        "WARN",
                        document_post_id,
                        "unexpected_refined_attachment_type",
                        f"unexpected refined type: {attachment_type}",
                    )
                )

    if not issues:
        issues.append({"level": "OK", "document_post_id": "", "check": "all_checks", "message": "passed"})

    write_tsv(VALIDATION, issues, VALIDATION_FIELDS)

    failures = sum(1 for row in issues if row["level"] == "FAIL")
    warnings = sum(1 for row in issues if row["level"] == "WARN")
    status = "OK all_checks passed" if failures == 0 and warnings == 0 else f"issues found FAIL={failures} WARN={warnings}"
    report_lines = [
        "D3.1B Attachment Taxonomy Refinement Validation Report",
        f"taxonomy\t{TAXONOMY}",
        f"refinement_changes\t{REFINEMENT}",
        f"validation\t{VALIDATION}",
        f"taxonomy_rows\t{len(taxonomy_rows)}",
        f"refinement_rows\t{len(refinement_rows)}",
        f"failures\t{failures}",
        f"warnings\t{warnings}",
        status,
    ]
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(VALIDATION)
    print(REPORT)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
