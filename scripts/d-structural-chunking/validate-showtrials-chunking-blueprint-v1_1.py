#!/usr/bin/env python3
"""Validate ShowTrials chunking blueprint v1.1."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
BLUEPRINT = ROOT / "showtrials_chunking_blueprint_v1_1.tsv"
VALIDATION = ROOT / "showtrials_chunking_blueprint_v1_1_validation.tsv"
REPORT = ROOT / "showtrials_chunking_blueprint_v1_1_validation_report.txt"

FIELDS = ["level", "document_type", "check", "message"]
VALID_TRANSLATION_READY = {"yes", "conditional", "review_required", "no"}
VALID_CONFIDENCE = {"high", "medium", "low"}


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


def as_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def issue(level: str, row: dict[str, str], check: str, message: str) -> dict[str, str]:
    return {
        "level": level,
        "document_type": row.get("document_type", ""),
        "check": check,
        "message": message,
    }


def main() -> int:
    rows = read_tsv(BLUEPRINT)
    issues: list[dict[str, str]] = []

    for row in rows:
        document_type = row.get("document_type", "").strip()
        primary = row.get("primary_chunk_unit", "").strip()
        hard = as_int(row.get("hard_max_chars", ""))
        translation_ready = row.get("translation_ready", "").strip()
        confidence = row.get("chunking_confidence", "").strip()

        if not document_type:
            issues.append(issue("FAIL", row, "document_type_nonempty", "document_type is empty"))
        if not primary:
            issues.append(issue("FAIL", row, "primary_chunk_unit_nonempty", "primary_chunk_unit is empty"))
        if hard is None:
            issues.append(issue("FAIL", row, "hard_max_chars_numeric", "hard_max_chars is not numeric"))
        elif hard > 5000:
            issues.append(issue("FAIL", row, "hard_max_chars_cap", "hard_max_chars exceeds 5000"))
        if translation_ready not in VALID_TRANSLATION_READY:
            issues.append(issue("FAIL", row, "translation_ready_valid", "translation_ready has invalid value"))
        if confidence not in VALID_CONFIDENCE:
            issues.append(issue("FAIL", row, "chunking_confidence_valid", "chunking_confidence has invalid value"))

        if document_type == "special_report":
            if row.get("package_detection_required", "").strip() != "yes":
                issues.append(issue("FAIL", row, "special_report_package_detection", "special_report must require package detection"))
            if row.get("attachment_first_strategy", "").strip() != "yes":
                issues.append(issue("FAIL", row, "special_report_attachment_first", "special_report must use attachment_first_strategy"))
        if document_type == "interrogation_protocol" and primary != "question_answer_block":
            issues.append(issue("FAIL", row, "interrogation_protocol_unit", "interrogation_protocol must use question_answer_block"))
        if document_type == "confrontation_protocol" and primary != "confrontation_exchange":
            issues.append(issue("FAIL", row, "confrontation_protocol_unit", "confrontation_protocol must use confrontation_exchange"))
        if document_type == "session_transcript" and primary != "speaker_turn":
            issues.append(issue("FAIL", row, "session_transcript_unit", "session_transcript must use speaker_turn"))
        if document_type == "conversation_recording" and primary != "conversation_segment":
            issues.append(issue("FAIL", row, "conversation_recording_unit", "conversation_recording must use conversation_segment"))

        if translation_ready == "review_required":
            issues.append(issue("WARN", row, "translation_readiness_incomplete", "document type still needs future review"))

    if not issues:
        issues.append({"level": "OK", "document_type": "", "check": "all_checks", "message": "passed"})

    write_tsv(VALIDATION, issues, FIELDS)
    failures = sum(1 for row in issues if row["level"] == "FAIL")
    warnings = sum(1 for row in issues if row["level"] == "WARN")
    status = "OK all_checks passed" if failures == 0 and warnings == 0 else f"issues found FAIL={failures} WARN={warnings}"
    report_lines = [
        "Chunking Blueprint v1.1 Validation Report",
        f"blueprint\t{BLUEPRINT}",
        f"validation\t{VALIDATION}",
        f"rows_checked\t{len(rows)}",
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
