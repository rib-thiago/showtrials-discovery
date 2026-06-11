#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/tmp/showtrials-discovery")

CATALOG = BASE / "showtrials_master_catalog.tsv"
ORG_DOCS = BASE / "showtrials_organization_documents.tsv"
FAMILIES = BASE / "showtrials_organization_families.tsv"

OUT_MATRIX = BASE / "showtrials_organization_family_document_matrix.tsv"
OUT_SUMMARY = BASE / "showtrials_organization_family_document_summary.tsv"
OUT_CROSS = BASE / "showtrials_organization_family_crosspairs.tsv"
OUT_REPORT = BASE / "showtrials_organization_family_document_matrix_report.txt"

def load_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

catalog = {r["document_post_id"]: r for r in load_tsv(CATALOG)}
org_docs = load_tsv(ORG_DOCS)
families = {r["organization"]: r["organization_family"] for r in load_tsv(FAMILIES)}

doc_families = defaultdict(set)
doc_orgs = defaultdict(set)

for r in org_docs:
    doc_id = r["document_post_id"]
    org = r["organization"]
    fam = families.get(org, "unclassified")

    doc_families[doc_id].add(fam)
    doc_orgs[doc_id].add(org)

matrix_rows = []

for doc_id, meta in sorted(catalog.items(), key=lambda x: (x[1].get("document_date", ""), x[0])):
    fams = sorted(doc_families.get(doc_id, set()))
    orgs = sorted(doc_orgs.get(doc_id, set()))

    row = {
        "document_post_id": doc_id,
        "document_date": meta.get("document_date", ""),
        "document_title": meta.get("document_title", ""),
        "primary_process": meta.get("primary_process", ""),
        "primary_collection": meta.get("primary_collection", ""),
        "category_names": meta.get("category_names", ""),
        "tag_names": meta.get("tag_names", ""),
        "organization_families": " | ".join(fams),
        "organizations": " | ".join(orgs),
        "family_count": len(fams),
        "organization_count": len(orgs),
        "has_party_apparatus": "yes" if "party_apparatus" in fams else "no",
        "has_security_apparatus": "yes" if "security_apparatus" in fams else "no",
        "has_state_apparatus": "yes" if "state_apparatus" in fams else "no",
        "has_judicial_apparatus": "yes" if "judicial_apparatus" in fams else "no",
        "has_press_media": "yes" if "press_media" in fams else "no",
        "has_international": "yes" if "international" in fams else "no",
        "has_political_organizations": "yes" if "political_organizations" in fams else "no",
        "content_words": meta.get("content_words", ""),
        "document_url": meta.get("document_url", ""),
    }
    matrix_rows.append(row)

with OUT_MATRIX.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "primary_process", "primary_collection", "category_names", "tag_names",
        "organization_families", "organizations",
        "family_count", "organization_count",
        "has_party_apparatus", "has_security_apparatus", "has_state_apparatus",
        "has_judicial_apparatus", "has_press_media", "has_international",
        "has_political_organizations",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(matrix_rows)

family_doc_counts = Counter()
family_words = Counter()
process_family = Counter()
collection_family = Counter()
crosspairs = Counter()

for r in matrix_rows:
    fams = [x for x in r["organization_families"].split(" | ") if x]
    words = int(r["content_words"] or 0)

    for fam in fams:
        family_doc_counts[fam] += 1
        family_words[fam] += words
        process_family[(r["primary_process"] or "UNSET", fam)] += 1
        collection_family[(r["primary_collection"] or "UNSET", fam)] += 1

    for i, a in enumerate(fams):
        for b in fams[i+1:]:
            crosspairs[(a, b)] += 1

with OUT_SUMMARY.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["scope", "name", "organization_family", "document_count", "total_words"])

    for fam, count in sorted(family_doc_counts.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["global", "ALL", fam, count, family_words[fam]])

    for (proc, fam), count in sorted(process_family.items(), key=lambda x: (x[0][0], -x[1], x[0][1])):
        w.writerow(["process", proc, fam, count, ""])

    for (coll, fam), count in sorted(collection_family.items(), key=lambda x: (x[0][0], -x[1], x[0][1])):
        w.writerow(["collection", coll, fam, count, ""])

with OUT_CROSS.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["family_a", "family_b", "document_count"])

    for (a, b), count in sorted(crosspairs.items(), key=lambda x: (-x[1], x[0])):
        w.writerow([a, b, count])

docs_with_any = sum(1 for r in matrix_rows if int(r["family_count"]) > 0)
docs_with_multi = sum(1 for r in matrix_rows if int(r["family_count"]) > 1)

report = []
report.append("ShowTrials organization family document matrix")
report.append("")
report.append(f"Documents: {len(matrix_rows)}")
report.append(f"Documents with any organization family: {docs_with_any}")
report.append(f"Documents with multiple organization families: {docs_with_multi}")
report.append("")
report.append("Family document counts:")
for fam, count in sorted(family_doc_counts.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{fam}\twords={family_words[fam]}")
report.append("")
report.append("Top family co-occurrences:")
for (a, b), count in sorted(crosspairs.items(), key=lambda x: (-x[1], x[0]))[:30]:
    report.append(f"{count}\t{a}\t+\t{b}")
report.append("")
report.append("Outputs:")
report.append(str(OUT_MATRIX))
report.append(str(OUT_SUMMARY))
report.append(str(OUT_CROSS))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_MATRIX)
print(OUT_SUMMARY)
print(OUT_CROSS)
print(OUT_REPORT)
