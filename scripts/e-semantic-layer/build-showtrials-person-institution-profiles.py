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
    PERSON_FAMILY_PAIRS,
    PERSON_INSTITUTION_PROFILES,
    PERSON_INSTITUTION_PROFILES_REPORT,
    PERSON_ORGANIZATION_PROFILE_PAIRS,
    PERSON_POSITION_PROFILE_PAIRS,
    POSITION_DOCUMENTS,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
PERSON_DOCS = LITERAL_PERSON_DOCUMENTS
ORG_DOCS = ORGANIZATION_DOCUMENTS
FAMILY_MATRIX = ORGANIZATION_FAMILY_DOCUMENT_MATRIX
POSITION_DOCS = POSITION_DOCUMENTS
DOC_TYPES = DOCUMENT_TYPES_V4
CATALOG = MASTER_CATALOG

OUT_PROFILES = PERSON_INSTITUTION_PROFILES
OUT_PERSON_FAMILY = PERSON_FAMILY_PAIRS
OUT_PERSON_ORG = PERSON_ORGANIZATION_PROFILE_PAIRS
OUT_PERSON_POSITION = PERSON_POSITION_PROFILE_PAIRS
OUT_REPORT = PERSON_INSTITUTION_PROFILES_REPORT

KEY_PEOPLE = {
    "Сталин", "Ежов", "Ягода", "Вышинский", "Бухарин", "Радек",
    "Троцкий", "Зиновьев", "Каменев", "Пятаков", "Рыков"
}

NOISY_POSITIONS = {
    "троцкист",
    "правый",
    "вредитель",
    "член",
    "кандидат",
    "представитель",
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

doc_positions = defaultdict(set)
doc_positions_signal = defaultdict(set)
for r in load_tsv(POSITION_DOCS):
    pos = r["position"]
    doc_positions[r["document_post_id"]].add(pos)
    if pos not in NOISY_POSITIONS:
        doc_positions_signal[r["document_post_id"]].add(pos)

profiles = []
person_family_rows = []
person_org_rows = []
person_position_rows = []

for person, docs in sorted(person_docs.items()):
    family_counter = Counter()
    org_counter = Counter()
    position_counter = Counter()
    signal_position_counter = Counter()
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
        for pos in doc_positions.get(doc_id, set()):
            position_counter[pos] += 1
        for pos in doc_positions_signal.get(doc_id, set()):
            signal_position_counter[pos] += 1

    total_docs = len(docs)

    top_families = " | ".join(f"{k}:{v}" for k, v in family_counter.most_common(8))
    top_orgs = " | ".join(f"{k}:{v}" for k, v in org_counter.most_common(10))
    top_positions = " | ".join(f"{k}:{v}" for k, v in signal_position_counter.most_common(10))
    top_doc_types = " | ".join(f"{k}:{v}" for k, v in dtype_counter.most_common(8))
    top_processes = " | ".join(f"{k}:{v}" for k, v in process_counter.most_common(8))
    top_collections = " | ".join(f"{k}:{v}" for k, v in collection_counter.most_common(8))

    likely_profile = []
    if family_counter.get("security_apparatus", 0) >= max(5, total_docs * 0.25):
        likely_profile.append("security_context")
    if family_counter.get("party_apparatus", 0) >= max(5, total_docs * 0.25):
        likely_profile.append("party_context")
    if family_counter.get("judicial_apparatus", 0) >= max(3, total_docs * 0.15):
        likely_profile.append("judicial_context")
    if family_counter.get("press_media", 0) >= max(3, total_docs * 0.20):
        likely_profile.append("press_context")
    if family_counter.get("international", 0) >= max(3, total_docs * 0.20):
        likely_profile.append("international_context")
    if dtype_counter.get("interrogation_protocol", 0) >= max(3, total_docs * 0.25):
        likely_profile.append("investigation_document_context")
    if dtype_counter.get("letter", 0) >= max(3, total_docs * 0.25):
        likely_profile.append("correspondence_context")

    profiles.append({
        "person": person,
        "document_count": total_docs,
        "total_words": people.get(person, {}).get("total_words", ""),
        "first_date": people.get(person, {}).get("first_date", ""),
        "last_date": people.get(person, {}).get("last_date", ""),
        "profile_tags": " | ".join(likely_profile),
        "top_families": top_families,
        "top_organizations": top_orgs,
        "top_signal_positions": top_positions,
        "top_document_types": top_doc_types,
        "top_processes": top_processes,
        "top_collections": top_collections,
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

    for pos, count in position_counter.most_common():
        person_position_rows.append({
            "person": person,
            "position": pos,
            "position_is_noisy": "yes" if pos in NOISY_POSITIONS else "no",
            "document_count": count,
            "person_total_documents": total_docs,
            "share_of_person_documents": round(count / total_docs, 4) if total_docs else 0,
        })

profiles = sorted(profiles, key=lambda r: (-int(r["document_count"]), r["person"]))

with ensure_parent(OUT_PROFILES).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "document_count", "total_words", "first_date", "last_date",
        "profile_tags", "top_families", "top_organizations", "top_signal_positions",
        "top_document_types", "top_processes", "top_collections", "interpretation_note"
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

with ensure_parent(OUT_PERSON_POSITION).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "person", "position", "position_is_noisy", "document_count",
        "person_total_documents", "share_of_person_documents"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(person_position_rows, key=lambda r: (-int(r["document_count"]), r["person"], r["position"])))

report = []
report.append("ShowTrials person institution profiles")
report.append("")
report.append(f"People: {len(profiles)}")
report.append(f"Person-family rows: {len(person_family_rows)}")
report.append(f"Person-organization rows: {len(person_org_rows)}")
report.append(f"Person-position rows: {len(person_position_rows)}")
report.append("")
report.append("Top people profiles:")
for r in profiles[:30]:
    report.append(
        f"{r['document_count']}\t{r['person']}\t{r['profile_tags']}"
        f"\tFAMILIES={r['top_families']}"
        f"\tPOSITIONS={r['top_signal_positions']}"
    )

report.append("")
report.append("Key people:")
for r in profiles:
    if r["person"] in KEY_PEOPLE:
        report.append(
            f"{r['document_count']}\t{r['person']}\t{r['profile_tags']}"
            f"\tFAMILIES={r['top_families']}"
            f"\tORGS={r['top_organizations']}"
            f"\tPOSITIONS={r['top_signal_positions']}"
        )

report.append("")
report.append("Outputs:")
report.append(str(OUT_PROFILES))
report.append(str(OUT_PERSON_FAMILY))
report.append(str(OUT_PERSON_ORG))
report.append(str(OUT_PERSON_POSITION))

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PROFILES)
print(OUT_PERSON_FAMILY)
print(OUT_PERSON_ORG)
print(OUT_PERSON_POSITION)
print(OUT_REPORT)
