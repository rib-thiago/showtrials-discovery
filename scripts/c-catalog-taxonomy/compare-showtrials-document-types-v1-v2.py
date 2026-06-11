#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")

V1 = BASE / "showtrials_document_types.tsv"
V2 = BASE / "showtrials_document_types_v2.tsv"

OUT = BASE / "showtrials_document_type_v1_v2_changes.tsv"
REPORT = BASE / "showtrials_document_type_v1_v2_compare_report.txt"

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return {r["document_post_id"]: r for r in csv.DictReader(f, delimiter="\t")}

v1 = load(V1)
v2 = load(V2)

rows = []
transition = Counter()

for doc_id, r1 in v1.items():
    r2 = v2.get(doc_id)
    if not r2:
        continue

    old = r1["document_type"]
    new = r2["document_type"]
    transition[(old, new)] += 1

    if old != new:
        rows.append({
            "document_post_id": doc_id,
            "old_type": old,
            "new_type": new,
            "document_title": r2["document_title"],
            "primary_process": r2["primary_process"],
            "primary_collection": r2["primary_collection"],
            "document_url": r2["document_url"],
        })

with OUT.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "old_type", "new_type", "document_title",
        "primary_process", "primary_collection", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials document type v1/v2 comparison")
report.append("")
report.append(f"Compared documents: {len(v1)}")
report.append(f"Changed documents: {len(rows)}")
report.append("")
report.append("Transitions:")
for (old, new), count in sorted(transition.items(), key=lambda x: (-x[1], x[0])):
    if old != new:
        report.append(f"{count}\t{old}\t→\t{new}")

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REPORT)
