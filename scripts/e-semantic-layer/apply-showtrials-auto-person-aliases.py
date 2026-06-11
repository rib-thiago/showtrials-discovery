#!/usr/bin/env python3
import csv
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

CANDIDATES = BASE / "showtrials_person_merge_candidates.tsv"
MANUAL = BASE / "showtrials_person_aliases_manual.tsv"
OUT_REPORT = BASE / "showtrials_person_auto_alias_report.txt"

AUTO_REJECT = {
    ("Л.С. Сосновского", "Л.С. Ассиновского"),
}

def pair(a, b):
    return tuple(sorted([a, b]))

def is_auto_safe(r):
    a = r["candidate_a"]
    b = r["candidate_b"]

    if pair(a, b) in {pair(*x) for x in AUTO_REJECT}:
        return False

    if r["confidence"] != "high":
        return False

    if r["reason"] != "same_initials_same_stem":
        return False

    if r["shared_initials"] == "":
        return False

    # Evita merges em que ambos os lados têm volume parecido mas poucos docs;
    # esses podem ser variantes reais ou nomes ambíguos.
    da = int(r["documents_a"] or 0)
    db = int(r["documents_b"] or 0)

    if da <= 1 and db <= 1:
        return False

    return True

existing = set()
if MANUAL.exists():
    with MANUAL.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            existing.add(r["raw_person"])

approved = []
review = []
rejected = []

with CANDIDATES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r.get("status") != "review":
            continue

        a = r["candidate_a"]
        b = r["candidate_b"]

        if pair(a, b) in {pair(*x) for x in AUTO_REJECT}:
            rejected.append(r)
            continue

        if is_auto_safe(r):
            raw = b
            canon = r["suggested_canonical"]

            if raw not in existing:
                approved.append({
                    "raw_person": raw,
                    "canonical_person": canon,
                    "decision": "approve",
                    "confidence": r["confidence"],
                    "reason": "auto_" + r["reason"],
                    "notes": f"auto-approved: {a} <-> {b}",
                })
                existing.add(raw)
        else:
            review.append(r)

exists = MANUAL.exists()
with MANUAL.open("a", encoding="utf-8", newline="") as f:
    fields = ["raw_person", "canonical_person", "decision", "confidence", "reason", "notes"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    if not exists:
        w.writeheader()
    for r in approved:
        w.writerow(r)

report = []
report.append("ShowTrials auto person alias application")
report.append("")
report.append(f"Auto-approved: {len(approved)}")
report.append(f"Rejected suggested: {len(rejected)}")
report.append(f"Still review: {len(review)}")
report.append(f"Manual TSV: {MANUAL}")
report.append("")
report.append("Auto-approved aliases:")
for r in approved:
    report.append(f"{r['raw_person']}\t→\t{r['canonical_person']}")
report.append("")
report.append("Still review candidates:")
for r in review[:120]:
    report.append(
        f"{r['confidence']}\t{r['reason']}\t"
        f"{r['candidate_a']}\t<->\t{r['candidate_b']}\t"
        f"SUGGEST={r['suggested_canonical']}"
    )
report.append("")
report.append("Rejected suggested candidates:")
for r in rejected:
    report.append(f"{r['candidate_a']}\t<->\t{r['candidate_b']}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_REPORT)
print(MANUAL)
