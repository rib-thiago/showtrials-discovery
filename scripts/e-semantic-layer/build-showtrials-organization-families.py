#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ORGANIZATION_FAMILIES,
    ORGANIZATION_FAMILIES_REPORT,
    ORGANIZATIONS,
    ensure_parent,
)

ORGS = ORGANIZATIONS

OUT = ORGANIZATION_FAMILIES
REPORT = ORGANIZATION_FAMILIES_REPORT

FAMILY_MAP = {
    "ВКП(б)": "party_apparatus",
    "ЦК ВКП(б)": "party_apparatus",
    "Политбюро": "party_apparatus",
    "КПК": "party_apparatus",
    "КПК при ЦК ВКП(б)": "party_apparatus",
    "Горьковский крайком ВКП(б)": "party_apparatus",

    "НКВД": "security_apparatus",
    "ГУГБ": "security_apparatus",
    "ИНО ГУГБ": "security_apparatus",
    "ОО ГУГБ НКВД": "security_apparatus",
    "УНКВД СССР по Горькраю": "security_apparatus",

    "ЦИК СССР": "state_apparatus",
    "Секретариат ЦИК СССР": "state_apparatus",
    "Совнарком": "state_apparatus",
    "Верховный Совет СССР": "state_apparatus",
    "НКИД": "state_apparatus",

    "Прокуратура СССР": "judicial_apparatus",
    "Верховный Суд СССР": "judicial_apparatus",

    "Правда": "press_media",
    "Известия": "press_media",
    "The New York Times": "press_media",
    "United Press International": "press_media",

    "Коминтерн": "international",
    "ИККИ": "international",
    "Лига Наций": "international",

    "Народная Трудовая Демократическая партия России": "political_organizations",
}

rows = []
family_counter = Counter()
family_docs = Counter()

with ORGS.open("r", encoding="utf-8", newline="") as f:
    orgs = list(csv.DictReader(f, delimiter="\t"))

for r in orgs:
    org = r["organization"]

    family = FAMILY_MAP.get(org, "unclassified")

    doc_count = int(r.get("document_count") or 0)

    rows.append({
        "organization": org,
        "organization_kind": r.get("organization_kind", ""),
        "organization_family": family,
        "document_count": doc_count,
        "first_date": r.get("first_date", ""),
        "last_date": r.get("last_date", ""),
    })

    family_counter[family] += 1
    family_docs[family] += doc_count

with ensure_parent(OUT).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "organization",
        "organization_kind",
        "organization_family",
        "document_count",
        "first_date",
        "last_date",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials organization families")
report.append("")
report.append(f"Organizations: {len(rows)}")
report.append("")

for fam, count in sorted(family_counter.items(), key=lambda x: (-x[1], x[0])):
    report.append(
        f"{fam}\torganizations={count}\tdocuments={family_docs[fam]}"
    )

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REPORT)
