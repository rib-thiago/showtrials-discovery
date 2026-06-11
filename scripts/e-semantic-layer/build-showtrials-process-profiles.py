#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/tmp/showtrials-discovery")

PERSON_PROCESS = BASE / "showtrials_person_process_matrix.tsv"
ORG_PROCESS = BASE / "showtrials_organization_process_matrix.tsv"
FAMILY_PROCESS = BASE / "showtrials_family_process_matrix.tsv"

OUT_PERSON = BASE / "showtrials_person_process_profiles.tsv"
OUT_ORG = BASE / "showtrials_organization_process_profiles.tsv"
OUT_FAMILY = BASE / "showtrials_family_process_profiles.tsv"
OUT_REPORT = BASE / "showtrials_process_profiles_report.txt"

def load_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def build_profiles(rows, entity_field):
    buckets = defaultdict(list)

    for r in rows:
        buckets[r[entity_field]].append(r)

    out = []

    for entity, items in buckets.items():
        counter = Counter()
        kind_counter = Counter()

        for r in items:
            process = r["process"]
            kind = r["process_kind"]
            count = int(r["document_count"] or 0)
            counter[process] += count
            kind_counter[kind] += count

        total = sum(counter.values())
        top_process, top_count = counter.most_common(1)[0]

        out.append({
            entity_field: entity,
            "total_process_documents": total,
            "process_count": len(counter),
            "process_kind_count": len(kind_counter),
            "top_process": top_process,
            "top_process_document_count": top_count,
            "top_process_share": round(top_count / total, 4) if total else 0,
            "process_distribution": " | ".join(f"{k}:{v}" for k, v in counter.most_common()),
            "process_kind_distribution": " | ".join(f"{k}:{v}" for k, v in kind_counter.most_common()),
            "interpretation_note": "process_profile_from_document_cooccurrence",
        })

    return sorted(out, key=lambda r: (-int(r["total_process_documents"]), -int(r["process_count"]), r[entity_field]))

person_rows = load_tsv(PERSON_PROCESS)
org_rows = load_tsv(ORG_PROCESS)
family_rows = load_tsv(FAMILY_PROCESS)

person_profiles = build_profiles(person_rows, "person")
org_profiles = build_profiles(org_rows, "organization")
family_profiles = build_profiles(family_rows, "organization_family")

def write(path, rows, entity_field):
    with path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            entity_field,
            "total_process_documents",
            "process_count",
            "process_kind_count",
            "top_process",
            "top_process_document_count",
            "top_process_share",
            "process_distribution",
            "process_kind_distribution",
            "interpretation_note",
        ]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(rows)

write(OUT_PERSON, person_profiles, "person")
write(OUT_ORG, org_profiles, "organization")
write(OUT_FAMILY, family_profiles, "organization_family")

report = []
report.append("ShowTrials process profiles")
report.append("")
report.append(f"Person profiles: {len(person_profiles)}")
report.append(f"Organization profiles: {len(org_profiles)}")
report.append(f"Family profiles: {len(family_profiles)}")

report.append("")
report.append("Top person process profiles:")
for r in person_profiles[:40]:
    report.append(
        f"{r['total_process_documents']}\tprocesses={r['process_count']}"
        f"\ttop_share={r['top_process_share']}\t{r['person']}"
        f"\tTOP={r['top_process']}:{r['top_process_document_count']}"
    )

report.append("")
report.append("Top organization process profiles:")
for r in org_profiles[:30]:
    report.append(
        f"{r['total_process_documents']}\tprocesses={r['process_count']}"
        f"\ttop_share={r['top_process_share']}\t{r['organization']}"
        f"\tTOP={r['top_process']}:{r['top_process_document_count']}"
    )

report.append("")
report.append("Family process profiles:")
for r in family_profiles:
    report.append(
        f"{r['total_process_documents']}\tprocesses={r['process_count']}"
        f"\ttop_share={r['top_process_share']}\t{r['organization_family']}"
        f"\tTOP={r['top_process']}:{r['top_process_document_count']}"
    )

report.append("")
report.append("Outputs:")
report.append(str(OUT_PERSON))
report.append(str(OUT_ORG))
report.append(str(OUT_FAMILY))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PERSON)
print(OUT_ORG)
print(OUT_FAMILY)
print(OUT_REPORT)
