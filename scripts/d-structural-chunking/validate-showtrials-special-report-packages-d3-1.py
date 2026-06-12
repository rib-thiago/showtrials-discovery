#!/usr/bin/env python3
"""Validate D3.1 special_report package analysis outputs."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


csv.field_size_limit(sys.maxsize)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.showtrials_paths import (
    CHUNKING_BLUEPRINT_V1,
    DOCUMENT_TYPES_V4,
    SPECIAL_REPORT_PACKAGES_D3_1,
    SPECIAL_REPORT_PACKAGES_D3_1_VALIDATION,
    SPECIAL_REPORT_PACKAGES_D3_1_VALIDATION_REPORT,
    ensure_parent,
)

PACKAGES = SPECIAL_REPORT_PACKAGES_D3_1
DOC_TYPES = DOCUMENT_TYPES_V4
BLUEPRINT = CHUNKING_BLUEPRINT_V1
VALIDATION = SPECIAL_REPORT_PACKAGES_D3_1_VALIDATION
REPORT = SPECIAL_REPORT_PACKAGES_D3_1_VALIDATION_REPORT

FIELDS = ["level", "document_post_id", "check", "message"]
ALLOWED_LIKELIHOODS = {"none", "possible", "likely", "strong"}


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


def as_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def issue(level: str, document_post_id: str, check: str, message: str) -> dict[str, str]:
    return {
        "level": level,
        "document_post_id": document_post_id,
        "check": check,
        "message": message,
    }


def expected_special_report_count() -> int | None:
    blueprint_rows = read_tsv(BLUEPRINT)
    for row in blueprint_rows:
        if row.get("document_type", "").strip() == "special_report":
            value = as_int(row.get("documents", ""))
            if value is not None:
                return value
    return None


def main() -> int:
    rows = read_tsv(PACKAGES)
    doc_type_rows = read_tsv(DOC_TYPES)
    special_report_count = sum(
        1 for row in doc_type_rows if row.get("document_type", "").strip() == "special_report"
    )
    expected_count = expected_special_report_count()
    issues: list[dict[str, str]] = []

    if expected_count is not None and expected_count == 526 and len(rows) != 526:
        issues.append(
            issue(
                "FAIL",
                "",
                "expected_526_special_reports",
                f"expected 526 special_report rows from blueprint, found {len(rows)}",
            )
        )
    if special_report_count and len(rows) != special_report_count:
        issues.append(
            issue(
                "FAIL",
                "",
                "special_report_count_matches_document_types",
                f"document_types has {special_report_count} special_report rows, package output has {len(rows)}",
            )
        )

    seen_ids: set[str] = set()
    for row in rows:
        document_post_id = row.get("document_post_id", "").strip()
        likelihood = row.get("package_likelihood", "").strip()
        attachment_count = as_int(row.get("detected_attachment_count", ""))
        strategy = row.get("recommended_package_strategy", "").strip()

        if not document_post_id:
            issues.append(issue("FAIL", document_post_id, "document_post_id_nonempty", "document_post_id is empty"))
        elif document_post_id in seen_ids:
            issues.append(issue("FAIL", document_post_id, "document_post_id_unique", "duplicate document_post_id"))
        seen_ids.add(document_post_id)

        if likelihood not in ALLOWED_LIKELIHOODS:
            issues.append(
                issue(
                    "FAIL",
                    document_post_id,
                    "package_likelihood_allowed",
                    f"package_likelihood must be one of {sorted(ALLOWED_LIKELIHOODS)}",
                )
            )
        if attachment_count is None:
            issues.append(
                issue(
                    "FAIL",
                    document_post_id,
                    "detected_attachment_count_numeric",
                    "detected_attachment_count is not numeric",
                )
            )
        elif likelihood == "strong" and attachment_count <= 0:
            issues.append(
                issue(
                    "FAIL",
                    document_post_id,
                    "strong_has_attachment_count",
                    "strong package_likelihood must have detected_attachment_count > 0",
                )
            )
        if not strategy:
            issues.append(
                issue(
                    "FAIL",
                    document_post_id,
                    "recommended_package_strategy_nonempty",
                    "recommended_package_strategy is empty",
                )
            )

    if not issues:
        issues.append({"level": "OK", "document_post_id": "", "check": "all_checks", "message": "passed"})

    write_tsv(VALIDATION, issues, FIELDS)

    failures = sum(1 for row in issues if row["level"] == "FAIL")
    warnings = sum(1 for row in issues if row["level"] == "WARN")
    report_lines = [
        "D3.1 Special Report Package Validation Report",
        f"packages\t{PACKAGES}",
        f"validation\t{VALIDATION}",
        f"rows_checked\t{len(rows)}",
        f"document_types_special_report_rows\t{special_report_count}",
        f"blueprint_expected_special_report_rows\t{expected_count if expected_count is not None else ''}",
        f"failures\t{failures}",
        f"warnings\t{warnings}",
        "OK all_checks passed" if failures == 0 and warnings == 0 else f"issues found FAIL={failures} WARN={warnings}",
    ]
    ensure_parent(REPORT).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(VALIDATION)
    print(REPORT)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
