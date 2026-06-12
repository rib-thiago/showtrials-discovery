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
    LITERAL_PERSON_DOCUMENTS,
    PERSON_ORGANIZATION_SUMMARY,
    PERSON_PROCESS_MATRIX,
    TRANSLATION_GLOSSARY_G3,
    TRANSLATION_GLOSSARY_G3_REPORT,
    TRANSLATION_GLOSSARY_G3_REVIEW,
    TRANSLATION_GLOSSARY_V1,
    ensure_parent,
)

GLOSSARY = TRANSLATION_GLOSSARY_V1
PERSON_DOCS = LITERAL_PERSON_DOCUMENTS
PERSON_PROCESS = PERSON_PROCESS_MATRIX
PERSON_ORG = PERSON_ORGANIZATION_SUMMARY

OUT = TRANSLATION_GLOSSARY_G3
REVIEW = TRANSLATION_GLOSSARY_G3_REVIEW
REPORT = TRANSLATION_GLOSSARY_G3_REPORT

# Mais abrangente que G2: inclui nomes conhecidos + correções morfológicas comuns
PERSON_CANONICAL_EXTRA = {
    "Л.В. Николаева": "L.V. Nikolaeva",
    "Г.Е. Прокофьева": "G.E. Prokofiev",
    "Г.И. Сафарова": "G.I. Safarov",
    "Е.В. Цетлина": "E.V. Tsetlin",
    "Дмитриев": "Dmitriev",
    "Н.А. Розенфельд": "N.A. Rosenfeld",
    "Г.Е. Евдокимова": "G.E. Evdokimov",
    "Членов": "Chlenov",
    "И.И. Котолынова": "I.I. Kotolynov",
    "А.И. Анишева": "A.I. Anishev",
    "В.В. Румянцева": "V.V. Rumyantsev",
    "Г.Ф. Попова": "G.F. Popov",
    "И.С. Горшенина": "I.S. Gorshenin",
    "А.М. Гертика": "A.M. Gertik",
    "М.М. Харитонова": "M.M. Kharitonov",
    "Н.В. Голубенко": "N.V. Golubenko",
    "Н.С. Антонова": "N.S. Antonov",
    "П.А. Николаева": "P.A. Nikolaev",
    "Б.Н. Сахова": "B.N. Sakhov",
    "В.С. Левина": "V.S. Levin",
    "К.К. Муханова": "K.K. Mukhanov",
    "М.А. Нырчука": "M.A. Nyrchuk",
    "М.Н. Яковлева": "M.N. Yakovlev",
    "Т.И. Глебовой": "T.I. Glebova",
    "Г.А. Молчанова": "G.A. Molchanov",
    "Г.Ф. Федорова": "G.F. Fedorov",
    "И.Г. Юскина": "I.G. Yuskin",
    "И.И. Тарасова": "I.I. Tarasov",
    "Н.И. Мухина": "N.I. Mukhin",
    "В.В. Кузьмина": "V.V. Kuzmin",
    "В.М. Попова": "V.M. Popov",
    "В.Ф. Логинова": "V.F. Loginov",
    "Е.А. Дрейцера": "E.A. Dreitser",
    "Н.П. Мясникова": "N.P. Myasnikov",
    "Ф.Ф. Фадеева": "F.F. Fadeev",
    "Молотов": "Vyacheslav Molotov",
    "Л.З. Мехлиса": "Lev Mekhlis",
    "Н.А. Угланова": "N.A. Uglanov",
    "Я.Р. Ельковича": "Ya.R. Elkovich",
    "В.Я. Головский-Голощапов": "V.Ya. Golovsky-Goloshchapov",
    "Л.С. Сосновского": "L.S. Sosnovsky",
}

ROLE_NOTES = {
    "троцкист": "Political label. Prefer 'Trotskyist'; keep as analytical/accusatory category, not neutral affiliation.",
    "правый": "Political label. Prefer 'Rightist' in context of Soviet opposition terminology.",
    "агент": "Ambiguous: can mean agent, operative, or accused foreign/intelligence agent depending on context.",
    "вредитель": "Accusatory Stalinist term. 'Wrecker' is historically conventional but should remain marked as accusatory.",
}

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def maybe_masculinize_ru_genitive(en):
    # Heurística conservadora sobre transliterações já existentes.
    fixes = [
        ("ova", "ov"),
        ("eva", "ev"),
        ("ina", "in"),
        ("ogo", "y"),
        ("skogo", "sky"),
        ("tskogo", "tsky"),
        ("vicha", "vich"),
        ("ovoi", "ova"),
        ("evoi", "eva"),
        ("inoi", "ina"),
    ]
    for old, new in fixes:
        if en.endswith(old):
            return en[:-len(old)] + new
    return en

person_docs = defaultdict(int)
for r in load(PERSON_DOCS):
    person_docs[r["person"]] += 1

person_processes = defaultdict(Counter)
for r in load(PERSON_PROCESS):
    person_processes[r["person"]][r["process"]] += int(r["document_count"] or 0)

person_orgs = defaultdict(int)
for r in load(PERSON_ORG):
    person_orgs[r["person"]] = int(r.get("organization_count") or 0)

rows = load(GLOSSARY)
out_rows = []
review_rows = []

for r in rows:
    row = dict(r)

    row["g3_action"] = ""
    row["g3_review_priority"] = ""
    row["g3_review_reason"] = ""
    row["process_distribution"] = ""
    row["person_document_count"] = ""
    row["person_organization_count"] = ""

    src = row["source_ru"]

    if row["layer"] == "people":
        doc_count = person_docs.get(src, int(row.get("source_count") or 0))
        org_count = person_orgs.get(src, 0)
        row["person_document_count"] = str(doc_count)
        row["person_organization_count"] = str(org_count)
        row["process_distribution"] = " | ".join(
            f"{k}:{v}" for k, v in person_processes.get(src, Counter()).most_common()
        )

        if src in PERSON_CANONICAL_EXTRA:
            row["canonical_en"] = PERSON_CANONICAL_EXTRA[src]
            row["status"] = "approved"
            row["confidence"] = "medium"
            row["g3_action"] = "approved_by_g3_curated_or_morphological_rule"
            row["notes"] = "G3 curated/corrected canonical person form"
        elif row["status"] != "approved":
            suggested = maybe_masculinize_ru_genitive(row["canonical_en"])
            if suggested != row["canonical_en"]:
                row["canonical_en"] = suggested
                row["status"] = "auto_normalized_needs_review"
                row["confidence"] = "medium"
                row["g3_action"] = "auto_morphological_normalization"

        if row["status"] != "approved":
            if doc_count >= 20:
                row["g3_review_priority"] = "high"
                row["g3_review_reason"] = "person_20plus_docs_not_approved"
            elif doc_count >= 10:
                row["g3_review_priority"] = "medium"
                row["g3_review_reason"] = "person_10plus_docs_not_approved"
            elif doc_count >= 5:
                row["g3_review_priority"] = "low"
                row["g3_review_reason"] = "person_5plus_docs_not_approved"
            elif org_count >= 3:
                row["g3_review_priority"] = "low"
                row["g3_review_reason"] = "person_multiple_org_contexts_not_approved"

    elif row["layer"] == "roles":
        if src in ROLE_NOTES:
            row["notes"] = ROLE_NOTES[src]
            row["g3_action"] = "role_note_enriched"
            row["g3_review_priority"] = "medium"
            row["g3_review_reason"] = "political_or_accusatory_label_semantic_review"

    elif row["layer"] in {"organizations", "processes"}:
        if row["status"] != "approved":
            row["g3_review_priority"] = "high"
            row["g3_review_reason"] = f"{row['layer']}_not_approved"

    out_rows.append(row)
    if row["g3_review_reason"]:
        review_rows.append(row)

fields = [
    "source_ru", "canonical_en", "layer", "glossary_kind",
    "priority", "source_count", "status", "confidence",
    "review_reason", "g3_action", "g3_review_priority", "g3_review_reason",
    "person_document_count", "person_organization_count", "process_distribution",
    "notes",
]

priority_order = {"high": 0, "medium": 1, "low": 2, "": 9}
status_order = {
    "approved": 0,
    "auto_normalized_needs_review": 1,
    "auto_transliterated_needs_review": 2,
    "pending": 3,
}

out_rows = sorted(
    out_rows,
    key=lambda r: (
        priority_order.get(r["priority"], 9),
        status_order.get(r["status"], 9),
        -int(r.get("source_count") or 0),
        r["layer"],
        r["source_ru"],
    )
)

review_rows = sorted(
    review_rows,
    key=lambda r: (
        priority_order.get(r["g3_review_priority"], 9),
        -int(r.get("person_document_count") or r.get("source_count") or 0),
        r["layer"],
        r["source_ru"],
    )
)

with ensure_parent(OUT).open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(out_rows)

with ensure_parent(REVIEW).open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(review_rows)

by_status = Counter(r["status"] for r in out_rows)
by_layer = Counter(r["layer"] for r in out_rows)
by_review = Counter(r["g3_review_reason"] for r in review_rows)
by_action = Counter(r["g3_action"] for r in out_rows if r["g3_action"])

report = []
report.append("ShowTrials translation glossary G3 enrichment")
report.append("")
report.append(f"Input rows: {len(rows)}")
report.append(f"Output rows: {len(out_rows)}")
report.append(f"G3 review rows: {len(review_rows)}")
report.append("")
report.append("Rows by layer:")
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by G3 action:")
for k, v in sorted(by_action.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Review queue by reason:")
for k, v in sorted(by_review.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Top G3 review queue:")
for r in review_rows[:100]:
    report.append(
        f"{r['g3_review_priority']}\t{r.get('person_document_count') or r.get('source_count')}\t"
        f"{r['layer']}\t{r['source_ru']}\t→\t{r['canonical_en']}\t{r['g3_review_reason']}"
    )
report.append("")
report.append("Outputs:")
report.append(str(OUT))
report.append(str(REVIEW))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REVIEW)
print(REPORT)
