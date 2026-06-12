#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path
from collections import Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    EXPORT_TXT_DIR,
    TEXT_CLEANLINESS,
    TEXT_CLEANLINESS_REPORT,
    ensure_parent,
)

TXT_DIR = EXPORT_TXT_DIR

OUT_TSV = TEXT_CLEANLINESS
OUT_REPORT = TEXT_CLEANLINESS_REPORT

PATTERNS = {
    "html_tag_like": re.compile(r"<[^>\n]+>"),
    "html_entity_like": re.compile(r"&[A-Za-z0-9#]+;"),
    "nbsp_char": re.compile("\u00a0"),
    "many_spaces": re.compile(r" {3,}"),
    "many_blank_lines": re.compile(r"\n{4,}"),
    "footnote_marker": re.compile(r"\[\d+\]"),
    "archive_ref": re.compile(r"(РГАСПИ|ГА РФ|ЦА ФСБ|АП РФ|Ф\.\s*\d+|Оп\.\s*\d+|Д\.\s*\d+|Л\.\s*\d+)", re.I),
    "editorial_braces": re.compile(r"\{[^}\n]{1,120}\}"),
    "angle_editorial": re.compile(r"<[^>\n]{1,120}>"),
    "stamp_marker": re.compile(r"\[Штамп:|\[Помета:", re.I),
}

rows = []
totals = Counter()

for path in sorted(TXT_DIR.glob("*.txt")):
    text = path.read_text(encoding="utf-8", errors="replace")
    line_count = text.count("\n") + 1
    word_count = len(text.split())

    row = {
        "file": str(path),
        "filename": path.name,
        "chars": len(text),
        "words": word_count,
        "lines": line_count,
    }

    for name, pattern in PATTERNS.items():
        count = len(pattern.findall(text))
        row[name] = count
        totals[name] += count

    rows.append(row)

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
    fields = ["file", "filename", "chars", "words", "lines"] + list(PATTERNS.keys())
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials text cleanliness diagnosis")
report.append("")
report.append(f"Files scanned: {len(rows)}")
report.append(f"Total chars: {sum(r['chars'] for r in rows)}")
report.append(f"Total words: {sum(r['words'] for r in rows)}")
report.append("")
report.append("Pattern totals:")
for name in PATTERNS:
    report.append(f"{name}\t{totals[name]}")
report.append("")
report.append("Top files by possible HTML residue:")
for r in sorted(rows, key=lambda x: x["html_tag_like"], reverse=True)[:20]:
    if r["html_tag_like"]:
        report.append(f"{r['html_tag_like']}\t{r['filename']}")
report.append("")
report.append("Top files by NBSP chars:")
for r in sorted(rows, key=lambda x: x["nbsp_char"], reverse=True)[:20]:
    if r["nbsp_char"]:
        report.append(f"{r['nbsp_char']}\t{r['filename']}")
report.append("")
report.append("Top files by many blank lines:")
for r in sorted(rows, key=lambda x: x["many_blank_lines"], reverse=True)[:20]:
    if r["many_blank_lines"]:
        report.append(f"{r['many_blank_lines']}\t{r['filename']}")
report.append("")
report.append("Top files by archive references:")
for r in sorted(rows, key=lambda x: x["archive_ref"], reverse=True)[:20]:
    if r["archive_ref"]:
        report.append(f"{r['archive_ref']}\t{r['filename']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
