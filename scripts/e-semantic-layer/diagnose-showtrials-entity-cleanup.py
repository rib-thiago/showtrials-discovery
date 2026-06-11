#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")
ENTITIES = BASE / "showtrials_title_entities.tsv"

OUT_TSV = BASE / "showtrials_entity_candidates.tsv"
OUT_REPORT = BASE / "showtrials_entity_cleanup_report.txt"

DOCUMENT_TERMS = {
    "делу", "аресте", "показаниях", "качестве", "семей", "ходе", "делам",
    "пленума", "центра", "очной", "правительственной", "результатах",
    "заключения", "согласии", "санкции", "слова", "время", "помиловании",
    "арестованного", "обвинения", "допроса", "заявления", "письма",
}

ORG_TERMS = {
    "Политбюро", "КПК", "НКВД", "ОГПУ", "ГУГБ", "ЦК", "ВКП",
    "Президиум", "Совета",
}

KNOWN_PERSON = {
    "Сталин", "Ежов", "Ягода", "Ягоде", "Ягодой", "Бухарин", "Рыков",
    "Радек", "Пятаков", "Зиновьев", "Каменев", "Троцкий", "Седов",
    "Агранов", "Сокольников", "Смирнов", "Мрачковский", "Ольберг",
    "Вышинский", "Молотов", "Киров", "Раковский", "Крестинский",
    "Томский", "Фриновский", "Прокофьев", "Прокофьева", "Балицкий",
    "Сафаров", "Сафарова", "Николаев", "Николаева", "Цетлин", "Цетлина",
    "Членов", "Дмитриев", "Гавен", "Шемелев", "Рейнгольд", "Голубенко",
    "Тивель", "Пригожин", "Астров", "Радин", "Розенфельд",
}

STOP_LOWER = {x.casefold() for x in DOCUMENT_TERMS}

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def has_initials(e):
    return bool(re.search(r"\b[А-ЯЁ]\.[А-ЯЁ]\.", e))

def looks_like_person(e):
    if has_initials(e):
        return True
    for p in KNOWN_PERSON:
        if p.casefold() in e.casefold():
            return True
    return False

def classify(e):
    e = norm(e)
    low = e.casefold()

    if not e:
        return ("UNKNOWN", "low")

    if low in STOP_LOWER:
        return ("DOCUMENT_TERM", "high")

    if e in ORG_TERMS:
        return ("ORGANIZATION", "high")

    if looks_like_person(e):
        return ("PERSON", "high" if has_initials(e) or e in KNOWN_PERSON else "medium")

    if re.search(r"[А-ЯЁ]\.[А-ЯЁ]\.", e):
        return ("PERSON", "medium")

    if re.match(r"^[А-ЯЁ][а-яё-]+(?:а|у|ым|ом|ой|ого|ему|е)?$", e):
        if len(e) >= 5 and low not in STOP_LOWER:
            return ("UNKNOWN", "medium")

    return ("UNKNOWN", "low")

rows = []
counts = Counter()

with ENTITIES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        entity = norm(r["entity"])
        etype, confidence = classify(entity)
        counts[(etype, confidence)] += 1

        rows.append({
            "entity": entity,
            "entity_type": etype,
            "confidence": confidence,
            "document_count": r.get("document_count", ""),
            "total_words": r.get("total_words", ""),
            "process_count": r.get("process_count", ""),
            "processes": r.get("processes", ""),
            "collection_count": r.get("collection_count", ""),
            "collections": r.get("collections", ""),
        })

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "entity", "entity_type", "confidence", "document_count", "total_words",
        "process_count", "processes", "collection_count", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials entity cleanup diagnosis")
report.append("")
report.append(f"Input entities: {len(rows)}")
report.append("")
report.append("Classification counts:")
for (etype, conf), count in sorted(counts.items()):
    report.append(f"{etype}\t{conf}\t{count}")

report.append("")
report.append("Top PERSON candidates:")
for r in [x for x in rows if x["entity_type"] == "PERSON"][:80]:
    report.append(f"{r['document_count']}\t{r['total_words']}\t{r['confidence']}\t{r['entity']}")

report.append("")
report.append("Top DOCUMENT_TERM candidates:")
for r in [x for x in rows if x["entity_type"] == "DOCUMENT_TERM"][:80]:
    report.append(f"{r['document_count']}\t{r['total_words']}\t{r['entity']}")

report.append("")
report.append("Top UNKNOWN candidates:")
for r in [x for x in rows if x["entity_type"] == "UNKNOWN"][:80]:
    report.append(f"{r['document_count']}\t{r['total_words']}\t{r['confidence']}\t{r['entity']}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
