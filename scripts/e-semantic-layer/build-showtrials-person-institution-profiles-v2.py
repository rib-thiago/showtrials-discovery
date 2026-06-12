#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict, Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    DOCUMENT_TYPES_V4,
    LITERAL_PEOPLE,
    LITERAL_PERSON_DOCUMENTS,
    MASTER_CATALOG,
    ORGANIZATION_DOCUMENTS,
    ORGANIZATION_FAMILY_DOCUMENT_MATRIX,
    PERSON_FAMILY_PAIRS_V2,
    PERSON_INSTITUTION_PROFILES_V2,
    PERSON_INSTITUTION_PROFILES_V2_REPORT,
    PERSON_ORGANIZATION_PAIRS_V2,
    PERSON_ROLE_PAIRS_V2,
    ROLE_DOCUMENTS_V2,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
PERSON_DOCS = LITERAL_PERSON_DOCUMENTS
ORG_DOCS = ORGANIZATION_DOCUMENTS
FAMILY_MATRIX = ORGANIZATION_FAMILY_DOCUMENT_MATRIX
ROLE_DOCS = ROLE_DOCUMENTS_V2
DOC_TYPES = DOCUMENT_TYPES_V4
CATALOG = MASTER_CATALOG

OUT_PROFILES = PERSON_INSTITUTION_PROFILES_V2
OUT_PERSON_FAMILY = PERSON_FAMILY_PAIRS_V2
OUT_PERSON_ORG = PERSON_ORGANIZATION_PAIRS_V2
OUT_PERSON_ROLE = PERSON_ROLE_PAIRS_V2
OUT_REPORT = PERSON_INSTITUTION_PROFILES_V2_REPORT

KEY_PEOPLE = {
    "Сталин", "Ежов", "Г.Г. Ягода", "А.Я. Вышинский", "Бухарин",
    "Радек", "Л.Д. Троцкий", "Зиновьев", "Каменев", "Пятаков", "Рыков"
}

def load_tsv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

people = {r["person"]: r for r in load_tsv(PEOPLE)}
catalog = {r["document_post_id"]: r for r in load_tsv(CATALOG)}
doc_types = {r["document_post_id"]: r.get("document_type", "") for r in load_tsv(DOC_TYPES)}

person_docs = defaultdict(set)
for r in load_tsv(PERSON_DOCS):
    person_docs[r["person"]].add(r["document_post_id"])

doc_orgs = defaultdict(set)
for r in load_tsv(ORG_DOCS):
    doc_orgs[r["document_post_id"]].add(r["organization"])

doc_families = defaultdict(set)
for r in load_tsv(FAMILY_MATRIX):
    for fam in (r.get("organization_families") or "").split(" | "):
        fam = fam.strip()
        if fam:
            doc_families[r["document_post_id"]].add(fam)

doc_roles = defaultdict(list)
for r in load_tsv(ROLE_DOCS):
    doc_roles[r["document_post_id"]].append({
        "role": r["role"],
        "role_class": r["role_class"],
        "signal": r["promote_to_profile_signal"],
    })

profiles = []
person_family_rows = []
person_org_rows = []
person_role_rows = []

for person, docs in sorted(person_docs.items()):
    family_counter = Counter()
    org_counter = Counter()
    role_counter = Counter()
    office_counter = Counter()
    trial_counter = Counter()
    political_label_counter = Counter()
    accusatory_label_counter = Counter()
    generic_counter = Counter()
    dtype_counter = Counter()
    process_counter = Counter()
    collection_counter = Counter()

    for doc_id in docs:
        meta = catalog.get(doc_id, {})
        dtype_counter[doc_types.get(doc_id, "unknown")] += 1
        process_counter[meta.get("primary_process") or "UNSET"] += 1
        collection_counter[meta.get("primary_collection") or "UNSET"] += 1

        for fam in doc_families.get(doc_id, set()):
            family_counter[fam] += 1

        for org in doc_orgs.get(doc_id, set()):
            org_counter[org] += 1

        seen_roles_in_doc = set()
        for rr in doc_roles.get(doc_id, []):
            role = rr["role"]
            role_class = rr["role_class"]
            key = (role, role_class)
            if key in seen_roles_in_doc:
                continue
            seen_roles_in_doc.add(key)

            role_counter[key] += 1

            if role_class == "office_position":
                office_counter[role] += 1
            elif role_class == "trial_role":
                trial_counter[role] += 1
            elif role_class == "political_label":
                political_label_counter[role] += 1
            elif role_class.startswith("accusatory"):
                accusatory_label_counter[role] += 1
            elif role_class.startswith("generic"):
                generic_counter[role] += 1

    total_docs = len(docs)

    profile_tags = []
    if family_counter.get("security_apparatus", 0) >= max(5, total_docs * 0.25):
        profile_tags.append("security_context")
    if family_counter.get("party_apparatus", 0) >= max(5, total_docs * 0.25):
        profile_tags.append("party_context")
    if family_counter.get("judicial_apparatus", 0) >= max(3, total_docs * 0.15):
        profile_tags.append("judicial_context")
    if family_counter.get("press_media", 0) >= max(3, total_docs * 0.20):
        profile_tags.append("press_context")
    if family_counter.get("international", 0) >= max(3, total_docs * 0.20):
        profile_tags.append("international_context")
    if dtype_counter.get("interrogation_protocol", 0) >= max(3, total_docs * 0.25):
        profile_tags.append("investigation_document_context")
    if dtype_counter.get("letter", 0) >= max(3, total_docs * 0.25):
        profile_tags.append("correspondence_context")
    if trial_counter:
        profile_tags.append("trial_role_context")
    if political_label_counter:
        profile_tags.append("political_label_context")
    if accusatory_label_counter:
        profile_tags.append("accusatory_label_context")

    profiles.append({
        "person": person,
        "document_count": total_docs,
        "total_words": people.get(person, {}).get("total_words", ""),
        "first_date": people.get(person, {}).get("first_date", ""),
        "last_date": people.get(person, {}).get("last_date", ""),
        "profile_tags": " | ".join(profile_tags),
        "top_families": " | ".join(f"{k}:{v}" for k, v in family_counter.most_common(8)),
        "top_organizations": " | ".join(f"{k}:{v}" for k, v in org_counter.most_common(10)),
        "top_office_positions": " | ".join(f"{k}:{v}" for k, v in office_counter.most_common(10)),
        "top_trial_roles": " | ".join(f"{k}:{v}" for k, v in trial_counter.most_common(10)),
        "top_political_labels": " | ".join(f"{k}:{v}" for k, v in political_label_counter.most_common(10)),
        "top_accusatory_labels": " | ".join(f"{k}:{v}" for k, v in accusatory_label_counter.most_common(10)),
        "top_generic_roles": " | ".join(f"{k}:{v}" for k, v in generic_counter.most_common(10)),
        "top_document_types": " | ".join(f"{k}:{v}" for k, v in dtype_counter.most_common(8)),
        "top_processes": " | ".join(f"{k}:{v}" for k, v in process_counter.most_common(8)),
        "top_collections": " | ".join(f"{k}:{v}" for k, v in collection_counter.most_common(8)),
        "interpretation_note": "cooccurrence_profile_not_biographical_claim",
    })

    for fam, count in family_counter.most_common():
        person_family_rows.append({
            "person": person,
            "organization_family": fam,
            "document_count": count,
            "person_total_documents": total_docs,
            "share_of_person_documents": round(count / total_docs, 4) if total_docs else 0,
        })

    for org, count in org_counter.most_common():
        person_org_rows.append({
            "person": person,
            "organization": org,
            "document_count": count,
            "person_total_documents": total_docs,
            "share_of_person_documents": round(count / total_docs, 4) if total_docs else 0,
        })

    for (role, role_class), count in role_counter.most_common():
        person_role_rows.append({
            "person": person,
            "role": role,
            "role_class": role_class,
            "document_count": count,
            "person_total_documents": total_docs,
            "share_of_person_documents": round(count / total_docs, 4) if total_docs else 0,
        })

profiles = sorted(profiles, key=lambda r: (-int(r["document_count"]), r["person"]))

with ensure_parent(OUT_PROFILES).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "document_count", "total_words", "first_date", "last_date",
        "profile_tags", "top_families", "top_organizations",
        "top_office_positions", "top_trial_roles", "top_political_labels",
        "top_accusatory_labels", "top_generic_roles",
        "top_document_types", "top_processes", "top_collections",
        "interpretation_note"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(profiles)

with ensure_parent(OUT_PERSON_FAMILY).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "organization_family", "document_count",
        "person_total_documents", "share_of_person_documents"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(person_family_rows, key=lambda r: (-int(r["document_count"]), r["person"], r["organization_family"])))

with ensure_parent(OUT_PERSON_ORG).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "organization", "document_count",
        "person_total_documents", "share_of_person_documents"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(person_org_rows, key=lambda r: (-int(r["document_count"]), r["person"], r["organization"])))

with ensure_parent(OUT_PERSON_ROLE).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "role", "role_class", "document_count",
        "person_total_documents", "share_of_person_documents"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(person_role_rows, key=lambda r: (-int(r["document_count"]), r["person"], r["role_class"], r["role"])))

report = []
report.append("ShowTrials person institution profiles v2")
report.append("")
report.append(f"People: {len(profiles)}")
report.append(f"Person-family rows: {len(person_family_rows)}")
report.append(f"Person-organization rows: {len(person_org_rows)}")
report.append(f"Person-role rows: {len(person_role_rows)}")
report.append("")
report.append("Top people profiles:")
for r in profiles[:30]:
    report.append(
        f"{r['document_count']}\t{r['person']}\t{r['profile_tags']}"
        f"\tFAMILIES={r['top_families']}"
        f"\tOFFICE={r['top_office_positions']}"
        f"\tTRIAL={r['top_trial_roles']}"
        f"\tPOL_LABELS={r['top_political_labels']}"
        f"\tACCUS={r['top_accusatory_labels']}"
    )

report.append("")
report.append("Key people:")
for r in profiles:
    if r["person"] in KEY_PEOPLE:
        report.append(
            f"{r['document_count']}\t{r['person']}\t{r['profile_tags']}"
            f"\tFAMILIES={r['top_families']}"
            f"\tORGS={r['top_organizations']}"
            f"\tOFFICE={r['top_office_positions']}"
            f"\tTRIAL={r['top_trial_roles']}"
            f"\tPOL_LABELS={r['top_political_labels']}"
            f"\tACCUS={r['top_accusatory_labels']}"
        )

report.append("")
report.append("Outputs:")
report.append(str(OUT_PROFILES))
report.append(str(OUT_PERSON_FAMILY))
report.append(str(OUT_PERSON_ORG))
report.append(str(OUT_PERSON_ROLE))

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PROFILES)
print(OUT_PERSON_FAMILY)
print(OUT_PERSON_ORG)
print(OUT_PERSON_ROLE)
print(OUT_REPORT)
