#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter, defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ENTITY_ANOMALIES_REPORT,
    LITERAL_PEOPLE,
    MASTER_CATALOG,
    PERSON_ANOMALIES,
    TAXONOMY_ANOMALIES,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
CATALOG = MASTER_CATALOG

OUT_PEOPLE = PERSON_ANOMALIES
OUT_TERMS = TAXONOMY_ANOMALIES
OUT_REPORT = ENTITY_ANOMALIES_REPORT

def split_pipe(v):
    return [x.strip() for x in (v or "").split(" | ") if x.strip()]

def to_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

def sim(a, b):
    return round(SequenceMatcher(None, a.casefold(), b.casefold()).ratio(), 4)

def initials_person(s):
    return bool(re.match(r"^(?:[А-ЯЁ]\.){1,3}\s+", s or ""))

people = []
with PEOPLE.open("r", encoding="utf-8", newline="") as f:
    people = list(csv.DictReader(f, delimiter="\t"))

docs = []
with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

person_rows = []

for p in people:
    person = p["person"]
    raw_forms = split_pipe(p.get("raw_forms"))
    doc_count = to_int(p.get("document_count"))

    flags = []

    if person.endswith("-"):
        flags.append("truncated_name_candidate")

    KNOWN_SHORT_OR_NO_INITIALS = {"Ежов", "Гавен", "Пригожин", "Радин"}
    if person not in KNOWN_SHORT_OR_NO_INITIALS:
        if not initials_person(person) and doc_count <= 3:
            flags.append("low_count_no_initials")

    if re.search(r"\b(?:делу|аресте|показаниях|ходе|центре|пленума)\b", person, re.I):
        flags.append("document_term_leaked_as_person")

    if person not in KNOWN_SHORT_OR_NO_INITIALS:
        if len(person) <= 4:
            flags.append("very_short_person_string")

    if flags:
        person_rows.append({
            "person": person,
            "document_count": p.get("document_count", ""),
            "total_words": p.get("total_words", ""),
            "first_date": p.get("first_date", ""),
            "last_date": p.get("last_date", ""),
            "flags": " | ".join(flags),
            "raw_forms": p.get("raw_forms", ""),
            "processes": p.get("processes", ""),
            "collections": p.get("collections", ""),
        })

with ensure_parent(OUT_PEOPLE).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "document_count", "total_words", "first_date", "last_date",
        "flags", "raw_forms", "processes", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(person_rows)

taxonomy = defaultdict(Counter)

for d in docs:
    for x in split_pipe(d.get("all_processes")):
        taxonomy["process"][x] += 1
    for x in split_pipe(d.get("all_collections")):
        taxonomy["collection"][x] += 1
    for x in split_pipe(d.get("category_names")):
        taxonomy["category"][x] += 1
    for x in split_pipe(d.get("tag_names")):
        taxonomy["tag"][x] += 1

tax_rows = []

for scope, counter in taxonomy.items():
    items = list(counter.items())

    for term, count in items:
        flags = []

        if count == 1:
            flags.append("single_document_term")
        if term.endswith("-"):
            flags.append("truncated_term_candidate")
        if len(term) <= 3:
            flags.append("very_short_term")
        if re.search(r"\s{2,}", term):
            flags.append("multiple_spaces")

        for other, other_count in items:
            if term >= other:
                continue
            similarity = sim(term, other)
            if similarity >= 0.9 and term != other:
                tax_rows.append({
                    "scope": scope,
                    "term": term,
                    "count": count,
                    "flags": "near_duplicate_candidate",
                    "near_term": other,
                    "near_term_count": other_count,
                    "similarity": similarity,
                })

        if flags:
            tax_rows.append({
                "scope": scope,
                "term": term,
                "count": count,
                "flags": " | ".join(flags),
                "near_term": "",
                "near_term_count": "",
                "similarity": "",
            })

with ensure_parent(OUT_TERMS).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "scope", "term", "count", "flags",
        "near_term", "near_term_count", "similarity"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(tax_rows)

flag_counts = Counter()
for r in person_rows:
    for f in split_pipe(r["flags"]):
        flag_counts[f] += 1

tax_flag_counts = Counter()
for r in tax_rows:
    for f in split_pipe(r["flags"]):
        tax_flag_counts[f] += 1

report = []
report.append("ShowTrials entity anomalies diagnosis")
report.append("")
report.append(f"People loaded: {len(people)}")
report.append(f"People anomaly rows: {len(person_rows)}")
report.append(f"Taxonomy anomaly rows: {len(tax_rows)}")
report.append("")
report.append("Person anomaly flags:")
for k, v in sorted(flag_counts.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{v}\t{k}")
report.append("")
report.append("Taxonomy anomaly flags:")
for k, v in sorted(tax_flag_counts.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{v}\t{k}")
report.append("")
report.append("Top person anomalies:")
for r in sorted(person_rows, key=lambda x: (to_int(x["document_count"]), x["person"]))[:80]:
    report.append(f"{r['document_count']}\t{r['flags']}\t{r['person']}\tRAW={r['raw_forms']}")
report.append("")
report.append("Top taxonomy anomalies:")
for r in tax_rows[:120]:
    report.append(
        f"{r['scope']}\t{r['count']}\t{r['flags']}\t{r['term']}"
        + (f"\t~ {r['near_term']} ({r['similarity']})" if r.get("near_term") else "")
    )

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PEOPLE)
print(OUT_TERMS)
print(OUT_REPORT)
