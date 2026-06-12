#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    DOCUMENT_TYPES_V2,
    DOCUMENT_TYPES_V2_REPORT,
    DOCUMENT_TYPE_SUMMARY_V2,
    DOCUMENT_TYPE_UNKNOWN_PREFIXES_V2,
    MASTER_CATALOG,
    ensure_parent,
)

CATALOG = MASTER_CATALOG

OUT_DOCS = DOCUMENT_TYPES_V2
OUT_SUMMARY = DOCUMENT_TYPE_SUMMARY_V2
OUT_UNKNOWN_PREFIXES = DOCUMENT_TYPE_UNKNOWN_PREFIXES_V2
OUT_REPORT = DOCUMENT_TYPES_V2_REPORT

RULES = [
    ("interrogation_protocol", r"\bпротокол допроса\b"),
    ("confrontation_protocol", r"\bочная ставка\b|\bпротокол очной ставки\b"),
    ("conversation_recording", r"\bзапись разговоров\b"),
    ("special_report", r"\bспецсообщение\b"),
    ("letter", r"\bписьм[оа]\b|\bписьма\b"),
    ("statement", r"\bзаявлени[ея]\b|\bзаявления\b"),
    ("session_transcript", r"\bстенограмма\b|\bфрагмент стенограммы\b|\bзаседани[ея]\b"),
    ("memo_note", r"\bзаписка\b"),
    ("indictment", r"\bобвинительное заключение\b|\bпроект обвинительного заключения\b"),
    ("verdict_or_sentence", r"\bприговор\b"),
    ("plea_pardon", r"\bпомиловани[ея]\b|\bпрошени[ея]\b"),
    ("autobiography", r"\bавтобиография\b"),
    ("reference_note", r"\bсправка\b"),
    ("article", r"\bстатья\b|\bочерк\b"),

    # v2 additions
    ("testimony", r"\bпоказани[ея]\b|\bпоказание\b|\bсобственноручные показания\b|\bдополнительные показания\b"),
    ("list", r"\bсписок\b|\bсписки\b"),
    ("decree_resolution", r"\bпостановление\b"),
    ("summary", r"\bсводка\b|\bсведения\b|\bстатистические данные\b"),
    ("plan_instruction", r"\bплан\b|\bинструкция\b"),
    ("draft_project", r"\bпроект\b|\bчерновые варианты\b|\bварианты\b"),
    ("explanation", r"\bобъяснени[ея]\b"),
    ("questionnaire_response", r"\bответы\b.*\bанкеты\b|\bвопросы анкеты\b"),
    ("speech", r"\bвыступлени[ея]\b|\bпоследнего слова\b|\bпоследнее слово\b"),
    ("program", r"\bпрограмма\b"),
    ("prosecutor_announcement", r"\bсообщение прокуратуры\b"),
    ("search_protocol", r"\bобыск[а]?\b|\bпротокол обыска\b|\bпроткол обыска\b"),
    ("data_extract", r"\bизменения к списку\b|\bматериалы\b|\bданные\b"),
]

def classify(title):
    t = (title or "").casefold()
    matches = []
    for dtype, pattern in RULES:
        if re.search(pattern, t, re.I):
            matches.append(dtype)
    if matches:
        return matches[0], " | ".join(matches), "rule_title_v2"
    return "unknown", "", "unmatched"

def first_words(title, n=4):
    words = re.findall(r"[A-Za-zА-Яа-яЁё0-9№]+", title or "")
    return " ".join(words[:n]) if words else "UNSET"

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

rows = []
summary = Counter()
unknown_prefixes = Counter()
unknown_examples = defaultdict(list)

for d in docs:
    dtype, matches, reason = classify(d.get("document_title", ""))

    rows.append({
        "document_post_id": d.get("document_post_id", ""),
        "document_date": d.get("document_date", ""),
        "document_title": d.get("document_title", ""),
        "document_type": dtype,
        "matched_types": matches,
        "reason": reason,
        "primary_process": d.get("primary_process", ""),
        "primary_collection": d.get("primary_collection", ""),
        "category_names": d.get("category_names", ""),
        "tag_names": d.get("tag_names", ""),
        "content_words": d.get("content_words", ""),
        "document_url": d.get("document_url", ""),
    })

    summary[dtype] += 1

    if dtype == "unknown":
        prefix = first_words(d.get("document_title", ""))
        unknown_prefixes[prefix] += 1
        if len(unknown_examples[prefix]) < 5:
            unknown_examples[prefix].append(d.get("document_title", ""))

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "document_type", "matched_types", "reason",
        "primary_process", "primary_collection",
        "category_names", "tag_names",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

with ensure_parent(OUT_SUMMARY).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["document_type", "count"])
    for dtype, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
        w.writerow([dtype, count])

with ensure_parent(OUT_UNKNOWN_PREFIXES).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["prefix", "count", "examples"])
    for prefix, count in sorted(unknown_prefixes.items(), key=lambda x: (-x[1], x[0])):
        w.writerow([prefix, count, " | ".join(unknown_examples[prefix])])

report = []
report.append("ShowTrials document type v2 diagnosis")
report.append("")
report.append(f"Documents: {len(docs)}")
report.append("")
report.append("Document types:")
for dtype, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{dtype}")

report.append("")
report.append("Unknown prefixes:")
for prefix, count in sorted(unknown_prefixes.items(), key=lambda x: (-x[1], x[0]))[:80]:
    report.append(f"{count}\t{prefix}\tEX={unknown_examples[prefix][0] if unknown_examples[prefix] else ''}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOCS)
print(OUT_SUMMARY)
print(OUT_UNKNOWN_PREFIXES)
print(OUT_REPORT)
