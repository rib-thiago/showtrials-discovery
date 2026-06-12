#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    POSITION_DOCUMENTS,
    POSITIONS,
    ROLE_DOCUMENTS_V2,
    ROLES_V2,
    ROLES_V2_REPORT,
    ensure_parent,
)

POSITION_DOCS = POSITION_DOCUMENTS

OUT_ROLES = ROLES_V2
OUT_DOCS = ROLE_DOCUMENTS_V2
OUT_REPORT = ROLES_V2_REPORT

ROLE_CLASS = {
    "нарком": "office_position",
    "наркомвнудел": "office_position",
    "следователь": "office_position",
    "прокурор": "office_position",
    "председатель": "office_position",
    "секретарь": "office_position",
    "начальник": "office_position",
    "заместитель": "office_position",
    "комиссар": "office_position",
    "судья": "office_position",
    "секретарь_суда": "office_position",
    "адвокат": "office_position",
    "редактор": "office_position",
    "корреспондент": "office_position",
    "посол": "office_position",
    "полпред": "office_position",
    "директор": "office_position",
    "руководитель": "office_position",

    "обвиняемый": "trial_role",
    "подсудимый": "trial_role",
    "свидетель": "trial_role",

    "троцкист": "political_label",
    "правый": "political_label",

    "вредитель": "accusatory_label",
    "агент": "accusatory_or_intelligence_label",

    "член": "generic_membership",
    "кандидат": "generic_membership",
    "представитель": "generic_representative",
    "сотрудник": "generic_staff",
}

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

positions = load(POSITIONS)
docs = load(POSITION_DOCS)

role_counts = Counter()
class_counts = Counter()

role_rows = []
for r in positions:
    role = r["position"]
    role_class = ROLE_CLASS.get(role, "unclassified")
    role_counts[role] = int(r["document_count"] or 0)
    class_counts[role_class] += int(r["document_count"] or 0)

    role_rows.append({
        "role": role,
        "role_class": role_class,
        "position_family_v1": r.get("position_family", ""),
        "document_count": r.get("document_count", ""),
        "total_words": r.get("total_words", ""),
        "first_date": r.get("first_date", ""),
        "last_date": r.get("last_date", ""),
        "raw_forms": r.get("raw_forms", ""),
        "promote_to_profile_signal": "yes" if role_class in {"office_position", "trial_role"} else "no",
        "notes": "derived_from_positions_v1",
    })

doc_rows = []
for r in docs:
    role = r["position"]
    role_class = ROLE_CLASS.get(role, "unclassified")
    doc_rows.append({
        **r,
        "role": role,
        "role_class": role_class,
        "promote_to_profile_signal": "yes" if role_class in {"office_position", "trial_role"} else "no",
    })

with ensure_parent(OUT_ROLES).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "role", "role_class", "position_family_v1", "document_count",
        "total_words", "first_date", "last_date", "raw_forms",
        "promote_to_profile_signal", "notes"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(role_rows, key=lambda x: (x["role_class"], -int(x["document_count"]), x["role"])))

with ensure_parent(OUT_DOCS).open("w", encoding="utf-8", newline="") as f:
    fields = list(doc_rows[0].keys())
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(doc_rows)

report = []
report.append("ShowTrials roles v2")
report.append("")
report.append(f"Roles: {len(role_rows)}")
report.append("")
report.append("Role classes:")
for cls, count in sorted(class_counts.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{cls}")
report.append("")
report.append("Roles:")
for r in sorted(role_rows, key=lambda x: (x["role_class"], -int(x["document_count"]), x["role"])):
    report.append(f"{r['document_count']}\t{r['role_class']}\t{r['role']}\tsignal={r['promote_to_profile_signal']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_ROLES)
print(OUT_DOCS)
print(OUT_REPORT)
