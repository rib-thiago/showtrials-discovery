#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PEOPLE,
    PERSON_NORMALIZATION_CANDIDATES,
    PERSON_NORMALIZATION_REPORT,
    ensure_parent,
)

OUT_MAP = PERSON_NORMALIZATION_CANDIDATES
OUT_REPORT = PERSON_NORMALIZATION_REPORT

CANONICAL = {
    "Сталин": ["Сталин", "Сталину", "Сталина", "Сталиным"],
    "Ежов": ["Ежов", "Ежову", "Ежова", "Ежовым"],
    "Ягода": ["Ягода", "Ягоде", "Ягоды", "Ягодой", "Ягоду"],
    "Бухарин": ["Бухарин", "Бухарина", "Бухарину", "Бухариным"],
    "Рыков": ["Рыков", "Рыкова", "Рыкову", "Рыковым"],
    "Радек": ["Радек", "Радека", "Радеку", "Радеком"],
    "Пятаков": ["Пятаков", "Пятакова", "Пятакову", "Пятаковым"],
    "Троцкий": ["Троцкий", "Троцкого", "Троцкому", "Троцким"],
    "Зиновьев": ["Зиновьев", "Зиновьева", "Зиновьеву", "Зиновьевым"],
    "Каменев": ["Каменев", "Каменева", "Каменеву", "Каменевым"],
    "Седов": ["Седов", "Седова", "Седову", "Седовым"],
    "Ольберг": ["Ольберг", "Ольберга", "Ольбергу", "Ольбергом"],
    "Сокольников": ["Сокольников", "Сокольникова", "Сокольникову", "Сокольниковым"],
    "Мрачковский": ["Мрачковский", "Мрачковского", "Мрачковскому", "Мрачковским"],
    "Агранов": ["Агранов", "Агранова", "Агранову", "Аграновым"],
    "Вышинский": ["Вышинский", "Вышинского", "Вышинскому", "Вышинским"],
    "Молотов": ["Молотов", "Молотова", "Молотову", "Молотовым"],
    "Киров": ["Киров", "Кирова", "Кирову", "Кировым"],
    "Синани-Скалов": ["Синани-Скалов", "Синани-Скалова", "Синани-", "Г.Б. Синани-"],
    "Каганович": ["Каганович", "Кагановича", "Кагановичу", "Кагановичем"],
}

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def strip_initials(entity):
    return re.sub(r"^(?:[А-ЯЁ]\.){1,3}\s*", "", entity).strip()

def infer(raw):
    e = norm(raw)
    no_initials = strip_initials(e)

    for canon, variants in CANONICAL.items():
        for v in variants:
            if v.casefold() in e.casefold() or v.casefold() in no_initials.casefold():
                reason = "manual_variant"
                if e != no_initials:
                    reason = "initials_plus_manual_variant"
                if e.endswith("-"):
                    reason = "truncation_candidate"
                return canon, reason, "high"

    if re.search(r"[А-ЯЁ]\.[А-ЯЁ]\.", e):
        return no_initials, "initials_stripped_unreviewed", "medium"

    return e, "identity_unreviewed", "low"

rows = []
with PEOPLE.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        raw = r["person"]
        canon, reason, confidence = infer(raw)
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

with ensure_parent(OUT_MAP).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "raw_person", "canonical_person", "reason", "confidence",
        "document_count", "total_words", "first_date", "last_date",
        "processes", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

by_canon = {}
for r in rows:
    by_canon.setdefault(r["canonical_person"], []).append(r)

report = []
report.append("ShowTrials person normalization diagnosis")
report.append("")
report.append(f"Raw people: {len(rows)}")
report.append(f"Canonical candidates: {len(by_canon)}")
report.append("")
report.append("Canonical groups with multiple raw forms:")
for canon, items in sorted(by_canon.items(), key=lambda x: len(x[1]), reverse=True):
    if len(items) > 1:
        raw_forms = " | ".join(i["raw_person"] for i in items)
        report.append(f"{len(items)}\t{canon}\t{raw_forms}")

report.append("")
report.append("Low-confidence identity mappings:")
for r in [x for x in rows if x["confidence"] == "low"][:120]:
    report.append(f"{r['document_count']}\t{r['raw_person']}\t→\t{r['canonical_person']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_MAP)
print(OUT_REPORT)
