#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")

FAMILIES = BASE / "showtrials_organization_families.tsv"

orgs = Counter()
docs = Counter()

with FAMILIES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fam = r["organization_family"]

        orgs[fam] += 1
        docs[fam] += int(r["document_count"] or 0)

print()
print("Organization family statistics")
print()

print("family\torganizations\tdocuments")

for fam, count in sorted(orgs.items(),
                         key=lambda x: (-docs[x[0]], x[0])):
    print(
        f"{fam}\t{count}\t{docs[fam]}"
    )
