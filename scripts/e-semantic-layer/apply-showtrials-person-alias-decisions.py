#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

ALIASES = BASE / "showtrials_person_aliases.tsv"
MANUAL = BASE / "showtrials_person_aliases_manual.tsv"
OUT = BASE / "showtrials_person_aliases_reviewed.tsv"
REPORT = BASE / "showtrials_person_aliases_reviewed_report.txt"

def load_aliases(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

rows = load_aliases(ALIASES)
by_raw = {r["raw_person"]: dict(r) for r in rows}

approved = 0
rejected = 0

if MANUAL.exists():
    with MANUAL.open("r", encoding="utf-8", newline="") as f:
        for m in csv.DictReader(f, delimiter="\t"):
            raw = m["raw_person"]
            decision = m["decision"]

            if decision == "reject":
                rejected += 1
                continue

            if decision != "approve":
                continue

            canon = m["canonical_person"]
            if not raw or not canon:
                continue

            if raw not in by_raw:
                by_raw[raw] = {
                    "raw_person": raw,
                    "canonical_person": canon,
                    "reason": "manual_review",
                    "confidence": m.get("confidence", "reviewed"),
                    "document_count": "",
                    "total_words": "",
                    "first_date": "",
                    "last_date": "",
                    "processes": "",
                    "collections": "",
                }
            else:
                by_raw[raw]["canonical_person"] = canon
                by_raw[raw]["reason"] = "manual_review"
                by_raw[raw]["confidence"] = "reviewed"

            approved += 1

fields = list(rows[0].keys())

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for raw in sorted(by_raw):
        w.writerow(by_raw[raw])

REPORT.write_text(
    "\n".join([
        "ShowTrials reviewed alias application",
        "",
        f"Base aliases: {len(rows)}",
        f"Manual approved: {approved}",
        f"Manual rejected: {rejected}",
        f"Reviewed aliases: {len(by_raw)}",
        f"Output: {OUT}",
    ]) + "\n",
    encoding="utf-8"
)

print(OUT)
print(REPORT)
