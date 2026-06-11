#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

SEEDS = BASE / "showtrials_translation_glossary_seeds_v1.tsv"

OUT = BASE / "showtrials_translation_glossary_v1.tsv"
REVIEW = BASE / "showtrials_translation_glossary_v1_review.tsv"
REPORT = BASE / "showtrials_translation_glossary_v1_report.txt"

PERSON_CANONICAL = {
    "Сталин": "Joseph Stalin",
    "И.В. Сталин": "Joseph Stalin",
    "Ежов": "Nikolai Yezhov",
    "Н.И. Ежов": "Nikolai Yezhov",
    "Г.Г. Ягода": "Genrikh Yagoda",
    "Ягода": "Genrikh Yagoda",
    "Бухарин": "Nikolai Bukharin",
    "Н.И. Бухарин": "Nikolai Bukharin",
    "Л.Д. Троцкий": "Leon Trotsky",
    "Троцкий": "Leon Trotsky",
    "Зиновьев": "Grigory Zinoviev",
    "Г.Е. Зиновьев": "Grigory Zinoviev",
    "Каменев": "Lev Kamenev",
    "Л.Б. Каменев": "Lev Kamenev",
    "Радек": "Karl Radek",
    "К.Б. Радек": "Karl Radek",
    "Пятаков": "Georgy Pyatakov",
    "Г.Л. Пятаков": "Georgy Pyatakov",
    "Рыков": "Alexei Rykov",
    "А.И. Рыков": "Alexei Rykov",
    "А.Я. Вышинский": "Andrey Vyshinsky",
    "Вышинский": "Andrey Vyshinsky",
    "Агранов": "Yakov Agranov",
    "Я.С. Агранов": "Yakov Agranov",
    "Седов": "Lev Sedov",
    "Л.Л. Седов": "Lev Sedov",
    "Ольберг": "Valentin Olberg",
    "Киров": "Sergei Kirov",
    "С.М. Киров": "Sergei Kirov",
    "Каганович": "Lazar Kaganovich",
    "Л.М. Каганович": "Lazar Kaganovich",
    "Сокольников": "Grigory Sokolnikov",
    "Г.Я. Сокольников": "Grigory Sokolnikov",
    "Смирнов": "Ivan Smirnov",
    "И.Н. Смирнов": "Ivan Smirnov",
    "Енукидзе": "Avel Yenukidze",
    "А.С. Енукидзе": "Avel Yenukidze",
    "Мрачковский": "Sergei Mrachkovsky",
    "С.В. Мрачковский": "Sergei Mrachkovsky",
}

ORG_FIXES = {
    "The New York Times": "The New York Times",
    "United Press International": "United Press International",
    "Народная Трудовая Демократическая партия России": "People's Labor Democratic Party of Russia",
}

PREFERRED_PERSON_OVERRIDES = {
    "Trotskii": "Trotsky",
    "Zinovev": "Zinoviev",
    "Vyshinskii": "Vyshinsky",
    "Ezhov": "Yezhov",
    "Reingolda": "Reingold",
    "Balitskogo": "Balitsky",
    "Mukhanovoi": "Mukhanova",
    "Bakaeva": "Bakaev",
    "Kotelnikova": "Kotelnikov",
    "Chernyavskogo": "Chernyavsky",
    "Shkiryatovu": "Shkiryatov",
    "Gessena": "Hessen",
    "Sharapovoi": "Sharapova",
    "Arkusa": "Arkus",
    "Shmidta": "Schmidt",
}

def normalize_auto_name(name):
    out = name
    for old, new in PREFERRED_PERSON_OVERRIDES.items():
        out = out.replace(old, new)
    return out

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

rows = load(SEEDS)
out_rows = []
review_rows = []

for r in rows:
    src = r["source_ru"]
    canonical = r["canonical_en"]
    status = r["status"]
    confidence = r["confidence"]
    notes = r["notes"]

    review_reason = ""

    if r["layer"] == "people":
        if src in PERSON_CANONICAL:
            canonical = PERSON_CANONICAL[src]
            status = "approved"
            confidence = "high"
            notes = "curated historical English name"
        else:
            canonical2 = normalize_auto_name(canonical)
            if canonical2 != canonical:
                canonical = canonical2
                status = "auto_normalized_needs_review"
                confidence = "medium"
                notes = "auto transliteration adjusted by common historical romanization rules"
            if r["priority"] == "high" and status != "approved":
                review_reason = "high_priority_person_needs_human_review"
            elif r["priority"] == "medium" and status != "approved":
                review_reason = "medium_priority_person_optional_review"

    elif r["layer"] == "organizations":
        if src in ORG_FIXES:
            canonical = ORG_FIXES[src]
            status = "approved"
            confidence = "high"
            notes = "curated organization label"
        if not canonical:
            review_reason = "organization_missing_canonical"

    elif r["layer"] == "roles":
        if r["glossary_kind"] in {"political_label", "accusatory_label", "accusatory_or_intelligence_label"}:
            review_reason = "political_or_accusatory_label_review_recommended"

    out = dict(r)
    out["canonical_en"] = canonical
    out["status"] = status
    out["confidence"] = confidence
    out["notes"] = notes
    out["review_reason"] = review_reason
    out_rows.append(out)

    if review_reason:
        review_rows.append(out)

fields = [
    "source_ru", "canonical_en", "layer", "glossary_kind",
    "priority", "source_count", "status", "confidence",
    "review_reason", "notes",
]

out_rows = sorted(
    out_rows,
    key=lambda r: (
        {"high": 0, "medium": 1, "low": 2}.get(r["priority"], 9),
        {"approved": 0, "auto_normalized_needs_review": 1, "auto_transliterated_needs_review": 2, "pending": 3}.get(r["status"], 9),
        -int(r["source_count"] or 0),
        r["layer"],
        r["source_ru"],
    )
)

review_rows = sorted(
    review_rows,
    key=lambda r: (
        {"high": 0, "medium": 1, "low": 2}.get(r["priority"], 9),
        -int(r["source_count"] or 0),
        r["layer"],
        r["source_ru"],
    )
)

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(out_rows)

with REVIEW.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(review_rows)

by_status = {}
by_layer = {}
for r in out_rows:
    by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    by_layer[r["layer"]] = by_layer.get(r["layer"], 0) + 1

report = []
report.append("ShowTrials translation glossary v1 canonicalization")
report.append("")
report.append(f"Input rows: {len(rows)}")
report.append(f"Output rows: {len(out_rows)}")
report.append(f"Review rows: {len(review_rows)}")
report.append("")
report.append("Rows by layer:")
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Review queue by reason:")
reasons = {}
for r in review_rows:
    reasons[r["review_reason"]] = reasons.get(r["review_reason"], 0) + 1
for k, v in sorted(reasons.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Top review queue:")
for r in review_rows[:80]:
    report.append(
        f"{r['priority']}\t{r['source_count']}\t{r['layer']}\t{r['source_ru']}\t→\t{r['canonical_en']}\t{r['review_reason']}"
    )

report.append("")
report.append("Outputs:")
report.append(str(OUT))
report.append(str(REVIEW))

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REVIEW)
print(REPORT)
