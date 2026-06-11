#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path("/tmp/showtrials-discovery")

G3 = BASE / "showtrials_translation_glossary_g3.tsv"
PERSON_DOCS = BASE / "showtrials_literal_person_documents.tsv"
ALIASES = BASE / "showtrials_person_aliases.tsv"
PERSON_PROCESS = BASE / "showtrials_person_process_matrix.tsv"
PERSON_ORG = BASE / "showtrials_person_organization_summary.tsv"

OUT = BASE / "showtrials_translation_glossary_g4.tsv"
REVIEW = BASE / "showtrials_translation_glossary_g4_review.tsv"
REPORT = BASE / "showtrials_translation_glossary_g4_report.txt"

# G4: nomes históricos/políticos/processuais ainda não cobertos ou cobertos de forma fraca.
# Critério: resolver o máximo útil sem inventar biografia completa.
PERSON_CANONICAL_G4 = {
    "В.А. Балицкого": "Vsevolod Balitsky",
    "И.П. Бакаева": "Ivan Bakaev",
    "И.И. Рейнгольда": "Isaak Reingold",
    "М.К. Чернявского": "M.K. Chernyavsky",
    "Г.Б. Синани-Скалов": "G.B. Sinani-Skalov",
    "Б.Л. Браво": "B.L. Bravo",
    "В.А. Барута": "V.A. Baruta",
    "Астров": "Astrov",
    "И.А. Мусульбаса": "I.A. Musulbas",
    "М.М. Киллерога": "M.M. Killerog",
    "Н.И. Бураго": "N.I. Burago",
    "С.А. Чихладзе": "S.A. Chikhladze",
    "П.А. Коваленко": "P.A. Kovalenko",
    "Шемелев": "Shemelev",
    "А.Ю. Айхенвальда": "A.Yu. Aikhenvald",
    "В.Я. Головский-Голощапов": "V.Ya. Golovsky-Goloshchapov",
    "Л.С. Сосновского": "L.S. Sosnovsky",
    "М.П. Томского": "Mikhail Tomsky",
    "В.В. Осинского": "Valerian Osinsky",
    "И.Т. Смилги": "Ivar Smilga",
    "Э.С. Гольцмана": "Eduard Holtzman",
    "Я.А. Лившица": "Ya.A. Livshits",
    "З.М. Беленького": "Z.M. Belenky",
    "Л.И. Сосицкого": "L.I. Sositsky",
    "М.С. Богуславского": "M.S. Boguslavsky",
    "П.А. Залуцкого": "P.A. Zalutsky",
    "Н.П. Глебов-Авилов": "N.P. Glebov-Avilov",
    "К.Б. Бермана-Юрина": "K.B. Berman-Yurin",
    "В.А. Тер-Ваганяна": "V.A. Ter-Vaganyan",
    "Е.А. Дрейцера": "E.A. Dreitser",
    "И.М. Бык-Бека": "I.M. Byk-Bek",
    "А.М. Аркус": "A.M. Arkus",
    "Г.М. Аркуса": "G.M. Arkus",
}

# Correções amplas, mas sem tentar "curar" tudo como approved.
ROMANIZATION_FIXES = [
    ("Gertsberga", "Gertsberg"),
    ("Birkengofa", "Birkengof"),
    ("Kushnera", "Kushner"),
    ("Mironova", "Mironov"),
    ("Korshunova", "Korshunov"),
    ("Knyazeva", "Knyazev"),
    ("Trusova", "Trusov"),
    ("Voroshilova", "Voroshilov"),
    ("Pikelya", "Pikel"),
    ("Kulishera", "Kulisher"),
    ("Goltsmana", "Holtzman"),
    ("Livshitsa", "Livshits"),
    ("Andreevu", "Andreev"),
    ("Dokuchaeva", "Dokuchaev"),
    ("Karmalitova", "Karmalitov"),
    ("Konovoi", "Konov"),
    ("Sinelobova", "Sinelobov"),
    ("Kantora", "Kantor"),
    ("Sverdlova", "Sverdlov"),
    ("Kozeleva", "Kozelev"),
    ("Kuzmicheva", "Kuzmichev"),
    ("Glebovoi", "Glebova"),
    ("Davydovoi", "Davydova"),
    ("Beskinoi", "Beskina"),
    ("Safonovoi", "Safonova"),
    ("Kostinoi", "Kostina"),
    ("Rozenfelda", "Rosenfeld"),
    ("Dityatevoi", "Dityateva"),
    ("Pozdeevoi", "Pozdeeva"),
    ("Tsarkova", "Tsarkov"),
    ("Golovskii", "Golovsky"),
    ("Goloshchapov", "Goloshchapov"),
    ("Faivilovich", "Faivilovich"),
    ("Zvezdov", "Zvezdov"),
]

def load(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def apply_fixes(s):
    out = s or ""
    for old, new in ROMANIZATION_FIXES:
        out = out.replace(old, new)
    return out

def is_case_form_ru(src):
    # Heurística para detectar formas oblíquas russas que ainda devem ser revisadas.
    return bool(re.search(r"(ого|его|овой|евой|иной|ым|им|у|а)$", src))

def has_initials(src):
    return bool(re.match(r"^[А-ЯЁ]\.[А-ЯЁ]\.\s+", src))

person_docs = defaultdict(int)
for r in load(PERSON_DOCS):
    person_docs[r["person"]] += 1

alias_count = defaultdict(int)
for r in load(ALIASES):
    p = r.get("canonical_person") or r.get("person") or r.get("source_ru") or ""
    if p:
        alias_count[p] += 1

person_processes = defaultdict(Counter)
for r in load(PERSON_PROCESS):
    person_processes[r["person"]][r["process"]] += int(r.get("document_count") or 0)

person_orgs = defaultdict(int)
for r in load(PERSON_ORG):
    person_orgs[r["person"]] = int(r.get("organization_count") or 0)

rows = load(G3)
out_rows = []
review_rows = []

for r in rows:
    row = dict(r)

    for col in [
        "g4_action", "g4_confidence", "g4_review_priority",
        "g4_review_reason", "alias_count", "historical_person_tier",
    ]:
        row[col] = ""

    src = row["source_ru"]
    layer = row["layer"]

    if layer == "people":
        doc_count = person_docs.get(src, int(row.get("person_document_count") or row.get("source_count") or 0))
        org_count = person_orgs.get(src, int(row.get("person_organization_count") or 0))
        aliases = alias_count.get(src, 0)

        row["person_document_count"] = str(doc_count)
        row["person_organization_count"] = str(org_count)
        row["alias_count"] = str(aliases)

        if not row.get("process_distribution"):
            row["process_distribution"] = " | ".join(
                f"{k}:{v}" for k, v in person_processes.get(src, Counter()).most_common()
            )

        if src in PERSON_CANONICAL_G4:
            row["canonical_en"] = PERSON_CANONICAL_G4[src]
            row["status"] = "approved"
            row["confidence"] = "medium"
            row["g4_action"] = "approved_by_g4_historical_person_map"
            row["g4_confidence"] = "medium"
            row["g4_review_priority"] = ""
            row["g4_review_reason"] = ""
            row["notes"] = "G4 historical/person canonicalization"
        elif row["status"] != "approved":
            fixed = apply_fixes(row["canonical_en"])
            if fixed != row["canonical_en"]:
                row["canonical_en"] = fixed
                if row["status"] == "auto_transliterated_needs_review":
                    row["status"] = "auto_normalized_needs_review"
                row["confidence"] = "medium"
                row["g4_action"] = "romanization_cleanup"

        # Tier interpretativo para guiar curadoria futura.
        if row["status"] == "approved" and doc_count >= 20:
            row["historical_person_tier"] = "tier1_core_or_high_frequency"
        elif row["status"] == "approved" and doc_count >= 10:
            row["historical_person_tier"] = "tier2_significant"
        elif doc_count >= 10 and row["status"] != "approved":
            row["historical_person_tier"] = "tier2_unresolved"
        elif doc_count >= 5 and row["status"] != "approved":
            row["historical_person_tier"] = "tier3_review_if_needed"
        elif org_count >= 8 and row["status"] != "approved":
            row["historical_person_tier"] = "tier3_high_org_context"
        else:
            row["historical_person_tier"] = "tier4_auto_ok"

        # G4 reduz a fila: não usa org_count sozinho como revisão ampla.
        if row["status"] != "approved":
            if doc_count >= 10:
                row["g4_review_priority"] = "medium"
                row["g4_review_reason"] = "person_10plus_docs_unresolved"
            elif doc_count >= 5:
                row["g4_review_priority"] = "low"
                row["g4_review_reason"] = "person_5plus_docs_unresolved"
            elif org_count >= 8 and is_case_form_ru(src):
                row["g4_review_priority"] = "low"
                row["g4_review_reason"] = "case_form_with_high_org_context"
            elif has_initials(src) and aliases >= 2 and row["status"] != "approved":
                row["g4_review_priority"] = "low"
                row["g4_review_reason"] = "multiple_aliases_unresolved"

    elif layer == "roles":
        if row.get("g3_review_reason") == "political_or_accusatory_label_semantic_review":
            row["g4_review_priority"] = "medium"
            row["g4_review_reason"] = "semantic_label_policy_review"
            row["historical_person_tier"] = "not_person"

    elif layer in {"organizations", "processes"}:
        if row["status"] != "approved":
            row["g4_review_priority"] = "high"
            row["g4_review_reason"] = f"{layer}_unapproved"
        row["historical_person_tier"] = "not_person"
    else:
        row["historical_person_tier"] = "not_person"

    out_rows.append(row)
    if row["g4_review_reason"]:
        review_rows.append(row)

fields = [
    "source_ru", "canonical_en", "layer", "glossary_kind",
    "priority", "source_count", "status", "confidence",
    "historical_person_tier",
    "review_reason", "g3_action", "g3_review_priority", "g3_review_reason",
    "g4_action", "g4_confidence", "g4_review_priority", "g4_review_reason",
    "person_document_count", "person_organization_count", "alias_count",
    "process_distribution", "notes",
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
        -int(r.get("person_document_count") or r.get("source_count") or 0),
        r["layer"],
        r["source_ru"],
    )
)

review_rows = sorted(
    review_rows,
    key=lambda r: (
        priority_order.get(r["g4_review_priority"], 9),
        -int(r.get("person_document_count") or r.get("source_count") or 0),
        -int(r.get("person_organization_count") or 0),
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

by_status = Counter(r["status"] for r in out_rows)
by_layer = Counter(r["layer"] for r in out_rows)
by_g4_action = Counter(r["g4_action"] for r in out_rows if r["g4_action"])
by_review = Counter(r["g4_review_reason"] for r in review_rows)
by_tier = Counter(r["historical_person_tier"] for r in out_rows)

report = []
report.append("ShowTrials translation glossary G4 historical person canonicalization")
report.append("")
report.append(f"Input rows: {len(rows)}")
report.append(f"Output rows: {len(out_rows)}")
report.append(f"G4 review rows: {len(review_rows)}")
report.append("")
report.append("Rows by layer:")
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by historical person tier:")
for k, v in sorted(by_tier.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by G4 action:")
for k, v in sorted(by_g4_action.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Review queue by reason:")
for k, v in sorted(by_review.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Top G4 review queue:")
for r in review_rows[:100]:
    report.append(
        f"{r['g4_review_priority']}\t{r.get('person_document_count') or r.get('source_count')}\t"
        f"orgs={r.get('person_organization_count')}\taliases={r.get('alias_count')}\t"
        f"{r['layer']}\t{r['source_ru']}\t→\t{r['canonical_en']}\t{r['g4_review_reason']}"
    )
report.append("")
report.append("Outputs:")
report.append(str(OUT))
report.append(str(REVIEW))

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REVIEW)
print(REPORT)
