#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    KNOWN_TRUNCATED_ALIASES_REPORT,
    PERSON_ALIASES_MANUAL,
    ensure_parent,
)

MANUAL = PERSON_ALIASES_MANUAL
REPORT = KNOWN_TRUNCATED_ALIASES_REPORT

ALIASES = {
    "Л.С. Мамишвили-": "Л.С. Мамишвили-Мишкевич",
    "Л.С. Тер-": "Л.С. Тер-Минасов",
    "С.М. Закса-": "С.М. Закс-Гладнев",
    "Я.Я. Упмал-": "Я.Я. Упмал-Ангарский",
    "А.А. Гардина-": "А.А. Гардин-Гейер",
    "А.И. Рамм-": "А.И. Рамм-Пфемферт",
    "В.А. Антонова-": "В.А. Антонов-Овсеенко",
    "В.П. Шевелева-": "В.П. Шевелев-Лубков",
    "В.Я. Головским-": "В.Я. Головский-Голощапов",
    "Е.Ф. Тойво-": "Е.Ф. Тойво-Пешина",
    "И.В. Вардина-": "И.В. Вардин-Мгеладзе",
    "И.М. Орловской-": "И.М. Орловская-Мрачковская",
    "М.М. Оскольского-": "М.М. Оскольский-Финкельштейн",
    "М.С. Жалыбиной-": "М.С. Жалыбина-Быкова",
}

FIELDS = ["raw_person", "canonical_person", "decision", "confidence", "reason", "notes"]

existing = set()
if MANUAL.exists():
    with MANUAL.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            existing.add(r["raw_person"])

exists = MANUAL.exists()
added = []

with ensure_parent(MANUAL).open("a", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
    if not exists:
        w.writeheader()

    for raw, canon in ALIASES.items():
        if raw in existing:
            continue
        w.writerow({
            "raw_person": raw,
            "canonical_person": canon,
            "decision": "approve",
            "confidence": "reviewed",
            "reason": "known_truncated_compound_name",
            "notes": "derived from document title",
        })
        added.append((raw, canon))

ensure_parent(REPORT).write_text(
    "ShowTrials known truncated person aliases\n\n"
    f"Added: {len(added)}\n"
    f"Manual TSV: {MANUAL}\n\n"
    + "\n".join(f"{a}\t→\t{b}" for a, b in added)
    + "\n",
    encoding="utf-8",
)

print(REPORT)
print(MANUAL)
