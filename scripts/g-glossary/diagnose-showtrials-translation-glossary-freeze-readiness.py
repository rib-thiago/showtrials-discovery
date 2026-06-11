#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")

G4 = BASE / "showtrials_translation_glossary_g4.tsv"
REVIEW = BASE / "showtrials_translation_glossary_g4_review.tsv"

REPORT = BASE / "showtrials_translation_glossary_freeze_readiness_report.txt"
TSV = BASE / "showtrials_translation_glossary_freeze_readiness.tsv"

rows = list(csv.DictReader(G4.open("r", encoding="utf-8", newline=""), delimiter="\t"))
review_rows = list(csv.DictReader(REVIEW.open("r", encoding="utf-8", newline=""), delimiter="\t"))

checks = []

def add(level, check, detail, recommendation):
    checks.append({
        "level": level,
        "check": check,
        "detail": detail,
        "recommendation": recommendation,
    })

people = [r for r in rows if r["layer"] == "people"]
orgs = [r for r in rows if r["layer"] == "organizations"]
processes = [r for r in rows if r["layer"] == "processes"]
roles = [r for r in rows if r["layer"] == "roles"]

people_total = len(people)
people_approved = sum(1 for r in people if r["status"] == "approved")
people_20plus_unapproved = [
    r for r in people
    if int(r.get("person_document_count") or r.get("source_count") or 0) >= 20
    and r["status"] != "approved"
]
people_10plus_unapproved = [
    r for r in people
    if int(r.get("person_document_count") or r.get("source_count") or 0) >= 10
    and r["status"] != "approved"
]
role_semantic_review = [
    r for r in roles
    if r.get("g4_review_reason") == "semantic_label_policy_review"
]

if all(r["status"] == "approved" for r in orgs):
    add("OK", "organizations", "all organizations approved", "freeze organization layer")
else:
    add("BLOCK", "organizations", "some organizations not approved", "review before freeze")

if all(r["status"] == "approved" for r in processes):
    add("OK", "processes", "all processes approved", "freeze process layer")
else:
    add("BLOCK", "processes", "some processes not approved", "review before freeze")

if people_20plus_unapproved:
    add(
        "BLOCK",
        "high_frequency_people",
        f"{len(people_20plus_unapproved)} people with >=20 docs unapproved",
        "resolve before production glossary",
    )
else:
    add(
        "OK",
        "high_frequency_people",
        "all people with >=20 docs approved",
        "acceptable for pilot",
    )

if people_10plus_unapproved:
    add(
        "WARN",
        "medium_frequency_people",
        f"{len(people_10plus_unapproved)} people with >=10 docs unapproved",
        "review if time allows before broad translation",
    )
else:
    add(
        "OK",
        "medium_frequency_people",
        "all people with >=10 docs approved",
        "acceptable for production v1",
    )

if role_semantic_review:
    add(
        "WARN",
        "semantic_roles",
        f"{len(role_semantic_review)} political/accusatory labels need policy review",
        "decide whether current English labels are acceptable",
    )
else:
    add("OK", "semantic_roles", "no semantic role reviews", "freeze role layer")

with TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["level", "check", "detail", "recommendation"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(checks)

by_status = Counter(r["status"] for r in rows)
by_tier = Counter(r["historical_person_tier"] for r in rows)

report = [
    "ShowTrials translation glossary freeze readiness",
    "",
    f"Glossary rows: {len(rows)}",
    f"Review rows: {len(review_rows)}",
    f"People approved: {people_approved}/{people_total}",
    f"People approved share: {people_approved / people_total:.3f}" if people_total else "People approved share: 0",
    "",
    "Rows by status:",
]
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Rows by historical tier:")
for k, v in sorted(by_tier.items()):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Freeze checks:")
for c in checks:
    report.append(f"{c['level']}\t{c['check']}\t{c['detail']}\t{c['recommendation']}")

report.append("")
report.append("Remaining people >=10 docs:")
for r in people_10plus_unapproved[:80]:
    report.append(
        f"{r.get('person_document_count')}\t{r['source_ru']}\t→\t{r['canonical_en']}\t{r['g4_review_reason']}"
    )

report.append("")
report.append("Outputs:")
report.append(str(TSV))

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)
