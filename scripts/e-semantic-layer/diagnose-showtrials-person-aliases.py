#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
PEOPLE = BASE / "showtrials_people.tsv"

OUT_ALIASES = BASE / "showtrials_person_aliases.tsv"
OUT_REPORT = BASE / "showtrials_person_aliases_report.txt"

CASE_ENDINGS = [
    ("ого", ""), ("ему", ""), ("ым", ""), ("ом", ""), ("ой", ""),
    ("а", ""), ("у", ""), ("е", ""), ("ы", ""),
]

MANUAL = {
    "Г.Г. Ягоды": "Г.Г. Ягода",
    "Г.Г. Ягоде": "Г.Г. Ягода",
    "Г.Г. Ягодой": "Г.Г. Ягода",

    "Л.Д. Троцкому": "Л.Д. Троцкий",

    "А.Я. Вышинского": "А.Я. Вышинский",
    "А.Я. Вышинскому": "А.Я. Вышинский",
    "А.Я. Вышинским": "А.Я. Вышинский",

    "Л.М. Кагановичу": "Л.М. Каганович",

    "С.В. Мрачковского": "С.В. Мрачковский",
    "С.В. Мрачковским": "С.В. Мрачковский",

    "Г.Б. Синани-": "Г.Б. Синани-Скалов",
}

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def initials_and_surname(e):
    e = norm(e)
    m = re.match(r"^((?:[А-ЯЁ]\.){1,3})\s*([А-ЯЁ][а-яё-]+-?)$", e)
    if not m:
        return "", e
    return m.group(1), m.group(2)

def rough_lemma(surname):
    s = surname.strip()
    for ending, repl in CASE_ENDINGS:
        if s.endswith(ending) and len(s) > len(ending) + 3:
            return s[:-len(ending)] + repl
    return s

rows = []
with PEOPLE.open("r", encoding="utf-8", newline="") as f:
    people = list(csv.DictReader(f, delimiter="\t"))

for r in people:
    raw = r["person"]
    initials, surname = initials_and_surname(raw)

    if raw in MANUAL:
        canon = MANUAL[raw]
        reason = "manual_alias"
        confidence = "high"
    else:
        canon = raw
        reason = "identity_unless_manual_alias"
        confidence = "identity"

    rows.append({
        "raw_person": raw,
        "canonical_person": canon,
        "reason": reason,
        "confidence": confidence,
        "document_count": r.get("document_count", ""),
        "total_words": r.get("total_words", ""),
        "first_date": r.get("first_date", ""),
        "last_date": r.get("last_date", ""),
        "processes": r.get("processes", ""),
        "collections": r.get("collections", ""),
    })

with OUT_ALIASES.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "raw_person", "canonical_person", "reason", "confidence",
        "document_count", "total_words", "first_date", "last_date",
        "processes", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

groups = defaultdict(list)
for r in rows:
    groups[r["canonical_person"]].append(r["raw_person"])

report = []
report.append("ShowTrials person aliases diagnosis")
report.append("")
report.append(f"Raw people: {len(rows)}")
report.append(f"Canonical literal/alias people: {len(groups)}")
report.append("")
report.append("Alias groups:")
for canon, raws in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
    if len(raws) > 1:
        report.append(f"{len(raws)}\t{canon}\t{' | '.join(sorted(raws))}")
report.append("")
report.append("Manual aliases:")
for r in rows:
    if r["reason"] == "manual_alias":
        report.append(f"{r['raw_person']}\t→\t{r['canonical_person']}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_ALIASES)
print(OUT_REPORT)
