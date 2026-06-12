#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path
from difflib import SequenceMatcher

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    LITERAL_PEOPLE,
    PERSON_ALIASES,
    PERSON_MERGE_CANDIDATES,
    PERSON_MERGE_CANDIDATES_REPORT,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
ALIASES = PERSON_ALIASES

OUT_TSV = PERSON_MERGE_CANDIDATES
OUT_REPORT = PERSON_MERGE_CANDIDATES_REPORT

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def initials_and_surname(person):
    person = norm(person)
    m = re.match(r"^((?:[А-ЯЁ]\.){1,3})\s*([А-ЯЁ][а-яё-]+-?)$", person)
    if not m:
        return "", person
    return m.group(1), m.group(2)

def rough_stem(s):
    s = s.casefold().strip()
    endings = [
        "ского", "скому", "ским", "ском",
        "ого", "ему", "ым", "ом", "ой",
        "ова", "ову", "овым", "овой",
        "ева", "еву", "евым", "евой",
        "ина", "ину", "иным", "иной",
        "а", "у", "е", "ы", "ой",
    ]
    for e in endings:
        if s.endswith(e) and len(s) > len(e) + 3:
            return s[:-len(e)]
    return s

def similarity(a, b):
    return round(SequenceMatcher(None, a.casefold(), b.casefold()).ratio(), 4)

def to_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

manual_alias_pairs = set()
with ALIASES.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        raw = r["raw_person"]
        canon = r["canonical_person"]
        if raw != canon:
            manual_alias_pairs.add(tuple(sorted([raw, canon])))

people = []
with PEOPLE.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        person = r["person"]
        initials, surname = initials_and_surname(person)
        people.append({
            "person": person,
            "initials": initials,
            "surname": surname,
            "stem": rough_stem(surname),
            "document_count": to_int(r.get("document_count")),
            "total_words": to_int(r.get("total_words")),
            "first_date": r.get("first_date", ""),
            "last_date": r.get("last_date", ""),
            "raw_forms": r.get("raw_forms", ""),
            "processes": r.get("processes", ""),
            "collections": r.get("collections", ""),
        })

rows = []

for i, a in enumerate(people):
    if not a["initials"]:
        continue

    for b in people[i + 1:]:
        if not b["initials"]:
            continue
        if a["initials"] != b["initials"]:
            continue

        sim = similarity(a["surname"], b["surname"])
        same_stem = a["stem"] and b["stem"] and (a["stem"] == b["stem"])
        stem_prefix = a["stem"] and b["stem"] and (
            a["stem"].startswith(b["stem"]) or b["stem"].startswith(a["stem"])
        )

        if same_stem:
            confidence = "high"
            reason = "same_initials_same_stem"
        elif stem_prefix and sim >= 0.75:
            confidence = "medium"
            reason = "same_initials_stem_prefix"
        elif sim >= 0.84:
            confidence = "medium"
            reason = "same_initials_high_similarity"
        else:
            continue

        pair = tuple(sorted([a["person"], b["person"]]))
        if pair in manual_alias_pairs:
            status = "already_manual_alias"
        else:
            status = "review"

        suggested = a["person"]
        if b["document_count"] > a["document_count"]:
            suggested = b["person"]
        elif b["document_count"] == a["document_count"] and len(b["surname"]) < len(a["surname"]):
            suggested = b["person"]

        rows.append({
            "candidate_a": a["person"],
            "candidate_b": b["person"],
            "shared_initials": a["initials"],
            "surname_a": a["surname"],
            "surname_b": b["surname"],
            "stem_a": a["stem"],
            "stem_b": b["stem"],
            "similarity": sim,
            "documents_a": a["document_count"],
            "documents_b": b["document_count"],
            "words_a": a["total_words"],
            "words_b": b["total_words"],
            "suggested_canonical": suggested,
            "confidence": confidence,
            "reason": reason,
            "status": status,
            "raw_forms_a": a["raw_forms"],
            "raw_forms_b": b["raw_forms"],
        })

rows.sort(key=lambda r: (
    0 if r["status"] == "review" else 1,
    0 if r["confidence"] == "high" else 1,
    -max(r["documents_a"], r["documents_b"]),
    r["candidate_a"],
))

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "candidate_a", "candidate_b", "shared_initials",
        "surname_a", "surname_b", "stem_a", "stem_b", "similarity",
        "documents_a", "documents_b", "words_a", "words_b",
        "suggested_canonical", "confidence", "reason", "status",
        "raw_forms_a", "raw_forms_b"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

review = [r for r in rows if r["status"] == "review"]
already = [r for r in rows if r["status"] == "already_manual_alias"]

report = []
report.append("ShowTrials unmerged person diagnosis")
report.append("")
report.append(f"People loaded: {len(people)}")
report.append(f"Merge candidates: {len(rows)}")
report.append(f"Review candidates: {len(review)}")
report.append(f"Already manual aliases: {len(already)}")
report.append("")
report.append("Top review candidates:")
for r in review[:80]:
    report.append(
        f"{r['confidence']}\t{r['reason']}\t{r['documents_a']}+{r['documents_b']}\t"
        f"{r['candidate_a']}\t<->\t{r['candidate_b']}\tSUGGEST={r['suggested_canonical']}"
    )
report.append("")
report.append("Already manual aliases detected:")
for r in already[:80]:
    report.append(
        f"{r['candidate_a']}\t<->\t{r['candidate_b']}\t{r['reason']}"
    )

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
