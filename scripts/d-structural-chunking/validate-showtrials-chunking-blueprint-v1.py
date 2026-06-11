#!/usr/bin/env python3
"""Validate chunking blueprint v1."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
INPUT_BLUEPRINT = ROOT / "showtrials_chunking_blueprint_v1.tsv"
OUTPUT_VALIDATION = ROOT / "showtrials_chunking_blueprint_v1_validation.tsv"
OUTPUT_REPORT = ROOT / "showtrials_chunking_blueprint_v1_validation_report.txt"

FIELDS = ["level", "document_type", "check", "message"]


def read_tsv(path: Path) -> list[dict[str, str]]:
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


def relevant_text(row: dict[str, str]) -> str:
    keys = [
        "expected_structure",
        "primary_chunk_unit",
        "secondary_chunk_unit",
        "preserve_boundaries",
        "fallback_strategy",
        "notes",
    ]
    return " ".join(row.get(key, "") for key in keys).lower()


def issue(level: str, row: dict[str, str], check: str, message: str) -> dict[str, str]:
    return {
        "level": level,
        "document_type": row.get("document_type", ""),
        "check": check,
        "message": message,
    }


def main() -> int:
    if not INPUT_BLUEPRINT.exists():
        raise SystemExit(f"Missing input: {INPUT_BLUEPRINT}")
    rows = read_tsv(INPUT_BLUEPRINT)
    issues: list[dict[str, str]] = []

    for row in rows:
        document_type = row.get("document_type", "").strip()
        text = relevant_text(row)
        target = as_int(row.get("target_chunk_chars", ""))
        soft = as_int(row.get("soft_max_chars", ""))
        hard = as_int(row.get("hard_max_chars", ""))

        if not document_type:
            issues.append(issue("FAIL", row, "document_type_nonempty", "document_type is empty"))
        if hard is None:
            issues.append(issue("FAIL", row, "hard_max_chars_numeric", "hard_max_chars is not numeric"))
        elif hard > 5000:
            issues.append(issue("FAIL", row, "hard_max_chars_cap", "hard_max_chars exceeds 5000"))
        if target is None:
            issues.append(issue("FAIL", row, "target_chunk_chars_numeric", "target_chunk_chars is not numeric"))
        elif target <= 0:
            issues.append(issue("FAIL", row, "target_chunk_chars_positive", "target_chunk_chars must be > 0"))
        if soft is None:
            issues.append(issue("FAIL", row, "soft_max_chars_numeric", "soft_max_chars is not numeric"))
        elif hard is not None and soft > hard:
            issues.append(issue("FAIL", row, "soft_max_le_hard_max", "soft_max_chars exceeds hard_max_chars"))
        if not row.get("preserve_boundaries", "").strip():
            issues.append(issue("FAIL", row, "preserve_boundaries_nonempty", "preserve_boundaries is empty"))
        if not row.get("primary_chunk_unit", "").strip():
            issues.append(issue("FAIL", row, "primary_chunk_unit_nonempty", "primary_chunk_unit is empty"))

        if document_type == "session_transcript" and "speaker" not in text:
            issues.append(issue("FAIL", row, "session_transcript_speaker", "session_transcript must mention speaker"))
        if document_type == "conversation_recording" and "speaker" not in text and "conversation" not in text:
            issues.append(
                issue(
                    "FAIL",
                    row,
                    "conversation_recording_speaker_or_conversation",
                    "conversation_recording must mention speaker or conversation",
                )
            )
        if document_type in {"biographical_article", "article"} and row.get("primary_chunk_unit", "") == "question_answer_block":
            issues.append(
                issue(
                    "FAIL",
                    row,
                    "article_not_qa_primary",
                    f"{document_type} cannot use question_answer_block as primary_chunk_unit",
                )
            )
        if document_type == "special_report" and "attachment" not in text and "body" not in text:
            issues.append(issue("FAIL", row, "special_report_attachment_or_body", "special_report must mention attachment or body"))

        if row.get("manual_review_required", "").strip() not in {"yes", "no", "sample_review"}:
            issues.append(issue("WARN", row, "manual_review_required_value", "manual_review_required has a nonstandard value"))
        notes = row.get("notes", "")
        if (
            document_type in {"biographical_article", "article"}
            and "d2_dominant_unit=question_answer_blocks" in notes
            and "false-positive QA" not in notes
        ):
            issues.append(
                issue(
                    "WARN",
                    row,
                    "article_false_positive_note",
                    "article-like type should document lexical QA caution when D2 reports question_answer_blocks",
                )
            )

    if not issues:
        issues.append({"level": "OK", "document_type": "", "check": "all_checks", "message": "passed"})

    write_tsv(OUTPUT_VALIDATION, issues, FIELDS)

    fail_count = sum(1 for row in issues if row["level"] == "FAIL")
    warn_count = sum(1 for row in issues if row["level"] == "WARN")
    ok_count = sum(1 for row in issues if row["level"] == "OK")
    if fail_count == 0 and warn_count == 0:
        status_line = "OK all_checks passed"
    else:
        status_line = f"issues found FAIL={fail_count} WARN={warn_count}"
    report_lines = [
        "Chunking Blueprint v1 Validation Report",
        f"blueprint\t{INPUT_BLUEPRINT}",
        f"validation\t{OUTPUT_VALIDATION}",
        f"rows_checked\t{len(rows)}",
        f"failures\t{fail_count}",
        f"warnings\t{warn_count}",
        f"ok_rows\t{ok_count}",
        status_line,
    ]
    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_VALIDATION)
    print(OUTPUT_REPORT)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
