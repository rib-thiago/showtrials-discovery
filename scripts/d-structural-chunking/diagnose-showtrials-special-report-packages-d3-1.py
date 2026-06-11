#!/usr/bin/env python3
"""Diagnose special_report records as documentary packages."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "showtrials_master_catalog.tsv"
DOC_TYPES = ROOT / "showtrials_document_types_v4.tsv"
CORPUS = ROOT / "showtrials_search_corpus.tsv"
SIZING = ROOT / "showtrials_corpus_sizing_by_document_d1.tsv"
BLUEPRINT = ROOT / "showtrials_chunking_blueprint_v1.tsv"

OUTPUT_PACKAGES = ROOT / "showtrials_special_report_packages_d3_1.tsv"
OUTPUT_SUMMARY = ROOT / "showtrials_special_report_package_summary_d3_1.tsv"
OUTPUT_EXAMPLES = ROOT / "showtrials_special_report_package_examples_d3_1.tsv"
OUTPUT_REPORT = ROOT / "showtrials_special_report_packages_d3_1_report.txt"

PACKAGE_FIELDS = [
    "document_post_id",
    "document_title",
    "primary_process",
    "content_chars",
    "package_likelihood",
    "detected_attachment_count",
    "detected_attachment_types",
    "detected_markers",
    "first_marker_position",
    "cover_note_likely",
    "embedded_interrogation_protocol",
    "embedded_list",
    "embedded_memo",
    "embedded_diary",
    "embedded_theses",
    "embedded_reference_note",
    "embedded_draft_project",
    "recommended_package_strategy",
    "notes",
]

SUMMARY_FIELDS = ["summary_scope", "summary_key", "documents", "strong", "likely", "possible", "none"]
EXAMPLE_FIELDS = ["document_post_id", "marker", "attachment_type_guess", "context_snippet"]

MARKER_PATTERNS = [
    ("с приложением", "package_marker", r"\bс\s+приложени(?:ем|ями)\b"),
    ("приложение", "package_marker", r"\bприложени[еяиюемях]*\b"),
    ("прилагаю", "package_marker", r"\bприлага(?:ю|ем|ется|ются|лись|лся|емые|емый|емая)\b"),
    ("направляю", "package_marker", r"\bнаправля(?:ю|ем|ется|ются|лся|лись|емый|емые|емая)\b"),
]

ATTACHMENT_PATTERNS = [
    ("memo", "меморандум", r"\bмеморандум[а-я]*\b"),
    ("interrogation_protocol", "протокол допроса", r"\bпротокол(?:ы|а|ом|е)?\s+допрос[а-я]*\b"),
    ("list", "список", r"\bспис(?:ок|ки|ка|ков|ком|ке)\b"),
    ("memo", "записка", r"\bзаписк[а-я]*\b"),
    ("diary", "дневник", r"\bдневник[а-я]*\b"),
    ("theses", "тезисы", r"\bтезис[а-я]*\b"),
    ("reference_note", "справка", r"\bсправк[а-я]*\b"),
    ("draft_project", "проект постановления", r"\bпроект\s+постановлени[а-я]*\b"),
    ("reference_note", "выдержки из показаний", r"\bвыдержк[а-я]*\s+из\s+показани[а-я]*\b"),
]

WEAK_MARKERS = {"приложение", "прилагаю", "направляю"}


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


def index_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("document_post_id", "").strip(): row for row in rows if row.get("document_post_id", "").strip()}


def compile_patterns(patterns: list[tuple[str, str, str]]) -> list[tuple[str, str, re.Pattern[str]]]:
    return [(label, kind, re.compile(pattern, re.IGNORECASE)) for label, kind, pattern in patterns]


MARKERS = compile_patterns(MARKER_PATTERNS)
ATTACHMENTS = compile_patterns(ATTACHMENT_PATTERNS)


def find_hits(text: str) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for marker, kind, pattern in MARKERS:
        for match in pattern.finditer(text):
            hits.append({"marker": marker, "type": kind, "start": match.start(), "end": match.end()})
    for attachment_type, marker, pattern in ATTACHMENTS:
        for match in pattern.finditer(text):
            hits.append(
                {
                    "marker": marker,
                    "type": attachment_type,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
    hits.sort(key=lambda item: (int(item["start"]), str(item["marker"])))
    return hits


def context_snippet(text: str, start: int, end: int, radius: int = 120) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = text[left:right]
    snippet = re.sub(r"\s+", " ", snippet).strip()
    if left > 0:
        snippet = "..." + snippet
    if right < len(text):
        snippet = snippet + "..."
    return snippet


def likelihood(markers: set[str], attachment_types: set[str]) -> str:
    if "с приложением" in markers or len(attachment_types) >= 2:
        return "strong"
    if "направляю" in markers and attachment_types:
        return "likely"
    if markers or attachment_types:
        return "possible"
    return "none"


def strategy_for(package_likelihood: str) -> str:
    if package_likelihood == "none":
        return "simple_special_report"
    if package_likelihood in {"possible", "likely"}:
        return "cover_plus_attachment_detection"
    return "package_split_before_chunking"


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    doc_type_rows = read_tsv(DOC_TYPES)
    corpus_rows = read_tsv(CORPUS)
    sizing_rows = read_tsv(SIZING)
    master_rows = read_tsv(MASTER)
    blueprint_rows = read_tsv(BLUEPRINT)

    corpus_by_id = index_by_id(corpus_rows)
    sizing_by_id = index_by_id(sizing_rows)
    master_by_id = index_by_id(master_rows)
    blueprint_by_type = {row.get("document_type", "").strip(): row for row in blueprint_rows}

    special_ids = [
        row.get("document_post_id", "").strip()
        for row in doc_type_rows
        if row.get("document_type", "").strip() == "special_report"
    ]

    output_rows: list[dict[str, str]] = []
    example_rows: list[dict[str, str]] = []
    likelihood_counts: Counter[str] = Counter()
    process_counts: dict[str, Counter[str]] = defaultdict(Counter)
    attachment_counts: dict[str, Counter[str]] = defaultdict(Counter)
    missing_corpus = 0

    for document_post_id in special_ids:
        corpus = corpus_by_id.get(document_post_id, {})
        sizing = sizing_by_id.get(document_post_id, {})
        master = master_by_id.get(document_post_id, {})
        text = corpus.get("search_text", "")
        if not text:
            missing_corpus += 1
        hits = find_hits(text)
        markers = {str(hit["marker"]) for hit in hits if str(hit["type"]) == "package_marker"}
        attachment_types = {str(hit["type"]) for hit in hits if str(hit["type"]) != "package_marker"}
        if "с приложением" in markers:
            attachment_types.add("generic_attachment")
        detected_markers = sorted({str(hit["marker"]) for hit in hits})
        first_marker_position = str(hits[0]["start"]) if hits else ""
        package_likelihood = likelihood(markers, attachment_types)
        strategy = strategy_for(package_likelihood)
        primary_process = (
            sizing.get("primary_process")
            or corpus.get("primary_process")
            or master.get("primary_process")
            or ""
        ).strip()
        title = (
            sizing.get("document_title")
            or corpus.get("document_title")
            or master.get("document_title")
            or ""
        ).strip()
        content_chars = (
            sizing.get("content_chars")
            or master.get("content_chars")
            or str(len(text))
        ).strip()

        likelihood_counts[package_likelihood] += 1
        process_counts[primary_process][package_likelihood] += 1
        for attachment_type in sorted(attachment_types):
            attachment_counts[attachment_type][package_likelihood] += 1

        notes = []
        if "с приложением" in markers:
            notes.append("explicit с приложением marker")
        weak_only = markers and markers.issubset(WEAK_MARKERS) and not attachment_types
        if weak_only:
            notes.append("weak marker only; requires human review")
        if blueprint_by_type.get("special_report"):
            notes.append("align with blueprint header_body_attachment_block")
        if not text:
            notes.append("missing corpus text")

        output_rows.append(
            {
                "document_post_id": document_post_id,
                "document_title": title,
                "primary_process": primary_process,
                "content_chars": content_chars,
                "package_likelihood": package_likelihood,
                "detected_attachment_count": str(len(attachment_types)),
                "detected_attachment_types": "|".join(sorted(attachment_types)),
                "detected_markers": "|".join(detected_markers),
                "first_marker_position": first_marker_position,
                "cover_note_likely": yes_no(package_likelihood in {"likely", "strong"} and bool(markers)),
                "embedded_interrogation_protocol": yes_no("interrogation_protocol" in attachment_types),
                "embedded_list": yes_no("list" in attachment_types),
                "embedded_memo": yes_no("memo" in attachment_types),
                "embedded_diary": yes_no("diary" in attachment_types),
                "embedded_theses": yes_no("theses" in attachment_types),
                "embedded_reference_note": yes_no("reference_note" in attachment_types),
                "embedded_draft_project": yes_no("draft_project" in attachment_types),
                "recommended_package_strategy": strategy,
                "notes": "; ".join(notes) if notes else "no package markers detected",
            }
        )

        for hit in hits:
            if len(example_rows) >= 100:
                break
            attachment_guess = str(hit["type"])
            example_rows.append(
                {
                    "document_post_id": document_post_id,
                    "marker": str(hit["marker"]),
                    "attachment_type_guess": attachment_guess,
                    "context_snippet": context_snippet(text, int(hit["start"]), int(hit["end"])),
                }
            )

    output_rows.sort(key=lambda row: int(row["document_post_id"]) if row["document_post_id"].isdigit() else 0)

    summary_rows: list[dict[str, str]] = []
    for process, counts in sorted(process_counts.items()):
        summary_rows.append(
            {
                "summary_scope": "primary_process",
                "summary_key": process,
                "documents": str(sum(counts.values())),
                "strong": str(counts.get("strong", 0)),
                "likely": str(counts.get("likely", 0)),
                "possible": str(counts.get("possible", 0)),
                "none": str(counts.get("none", 0)),
            }
        )
    for attachment_type, counts in sorted(attachment_counts.items()):
        summary_rows.append(
            {
                "summary_scope": "attachment_type",
                "summary_key": attachment_type,
                "documents": str(sum(counts.values())),
                "strong": str(counts.get("strong", 0)),
                "likely": str(counts.get("likely", 0)),
                "possible": str(counts.get("possible", 0)),
                "none": str(counts.get("none", 0)),
            }
        )

    write_tsv(OUTPUT_PACKAGES, output_rows, PACKAGE_FIELDS)
    write_tsv(OUTPUT_SUMMARY, summary_rows, SUMMARY_FIELDS)
    write_tsv(OUTPUT_EXAMPLES, example_rows, EXAMPLE_FIELDS)

    report_lines = [
        "D3.1 Special Report Documentary Package Analysis",
        f"packages\t{OUTPUT_PACKAGES}",
        f"summary\t{OUTPUT_SUMMARY}",
        f"examples\t{OUTPUT_EXAMPLES}",
        f"special_report_rows\t{len(output_rows)}",
        f"missing_corpus_text\t{missing_corpus}",
        f"strong\t{likelihood_counts.get('strong', 0)}",
        f"likely\t{likelihood_counts.get('likely', 0)}",
        f"possible\t{likelihood_counts.get('possible', 0)}",
        f"none\t{likelihood_counts.get('none', 0)}",
        "heuristic\tstrong=s prilozheniem or multiple attachment types; likely=napravlyayu plus embedded type; possible=single weak marker/type; none=no marker",
        "policy\tanalysis aid only; no translation, API calls, embeddings, or input mutation",
    ]
    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(OUTPUT_PACKAGES)
    print(OUTPUT_SUMMARY)
    print(OUTPUT_EXAMPLES)
    print(OUTPUT_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
