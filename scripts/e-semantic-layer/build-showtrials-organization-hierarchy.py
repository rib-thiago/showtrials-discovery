#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

ORGS = BASE / "showtrials_organizations.tsv"

OUT = BASE / "showtrials_organization_hierarchy.tsv"
REVIEW = BASE / "showtrials_organization_hierarchy_review.tsv"
REPORT = BASE / "showtrials_organization_hierarchy_report.txt"

RULES = [
    {
        "child": "ЦК ВКП(б)",
        "parent": "ВКП(б)",
        "relation_type": "central_committee_of",
        "confidence": "high",
        "reason": "known_party_structure",
    },
    {
        "child": "Политбюро",
        "parent": "ЦК ВКП(б)",
        "relation_type": "political_bureau_of",
        "confidence": "high",
        "reason": "known_party_structure",
    },
    {
        "child": "КПК",
        "parent": "ЦК ВКП(б)",
        "relation_type": "party_control_body_of",
        "confidence": "medium",
        "reason": "party_control_body",
    },
    {
        "child": "КПК при ЦК ВКП(б)",
        "parent": "ЦК ВКП(б)",
        "relation_type": "party_control_body_of",
        "confidence": "high",
        "reason": "name_contains_parent",
    },
    {
        "child": "Горьковский крайком ВКП(б)",
        "parent": "ВКП(б)",
        "relation_type": "regional_committee_of",
        "confidence": "high",
        "reason": "name_contains_party",
    },
    {
        "child": "ГУГБ",
        "parent": "НКВД",
        "relation_type": "main_directorate_of",
        "confidence": "high",
        "reason": "known_security_structure",
    },
    {
        "child": "ИНО ГУГБ",
        "parent": "ГУГБ",
        "relation_type": "department_of",
        "confidence": "high",
        "reason": "name_contains_parent",
    },
    {
        "child": "ОО ГУГБ НКВД",
        "parent": "ГУГБ",
        "relation_type": "department_of",
        "confidence": "high",
        "reason": "name_contains_parent",
    },
    {
        "child": "УНКВД СССР по Горькраю",
        "parent": "НКВД",
        "relation_type": "regional_security_body_of",
        "confidence": "high",
        "reason": "name_contains_nkvd",
    },
    {
        "child": "Секретариат ЦИК СССР",
        "parent": "ЦИК СССР",
        "relation_type": "secretariat_of",
        "confidence": "high",
        "reason": "name_contains_parent",
    },
]

def load_orgs():
    with ORGS.open("r", encoding="utf-8", newline="") as f:
        return {r["organization"]: r for r in csv.DictReader(f, delimiter="\t")}

orgs = load_orgs()
rows = []
review_rows = []
missing = []

for rule in RULES:
    child = rule["child"]
    parent = rule["parent"]

    if child not in orgs or parent not in orgs:
        missing.append(rule)
        continue

    child_docs = int(orgs[child].get("document_count") or 0)
    parent_docs = int(orgs[parent].get("document_count") or 0)

    row = {
        "child_organization": child,
        "parent_organization": parent,
        "relation_type": rule["relation_type"],
        "confidence": rule["confidence"],
        "reason": rule["reason"],
        "child_kind": orgs[child].get("organization_kind", ""),
        "parent_kind": orgs[parent].get("organization_kind", ""),
        "child_document_count": child_docs,
        "parent_document_count": parent_docs,
        "status": "auto_proposed",
        "review_decision": "",
        "notes": "",
    }
    rows.append(row)

    if rule["confidence"] != "high":
        review_rows.append(row)

with OUT.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "child_organization", "parent_organization", "relation_type",
        "confidence", "reason", "child_kind", "parent_kind",
        "child_document_count", "parent_document_count",
        "status", "review_decision", "notes"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

with REVIEW.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "child_organization", "parent_organization", "relation_type",
        "confidence", "reason", "child_kind", "parent_kind",
        "child_document_count", "parent_document_count",
        "status", "review_decision", "notes"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(review_rows)

report = []
report.append("ShowTrials organization hierarchy")
report.append("")
report.append(f"Organizations loaded: {len(orgs)}")
report.append(f"Hierarchy rows: {len(rows)}")
report.append(f"Review rows: {len(review_rows)}")
report.append(f"Missing rows: {len(missing)}")
report.append("")
report.append("Hierarchy:")
for r in rows:
    report.append(
        f"{r['confidence']}\t{r['child_organization']}"
        f"\t→\t{r['parent_organization']}"
        f"\t{r['relation_type']}\t{r['reason']}"
    )
report.append("")
report.append("Manual review suggested:")
for r in review_rows:
    report.append(
        f"{r['child_organization']}\t→\t{r['parent_organization']}"
        f"\t{r['relation_type']}\t{r['confidence']}"
    )
if missing:
    report.append("")
    report.append("Missing organizations:")
    for r in missing:
        report.append(f"{r['child']}\t→\t{r['parent']}")

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REVIEW)
print(REPORT)
