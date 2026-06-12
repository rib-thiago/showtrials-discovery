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
    LITERAL_PERSON_DOCUMENTS,
    MASTER_CATALOG,
    TRUNCATED_PERSON_CANDIDATES,
    TRUNCATED_PERSON_CANDIDATES_REPORT,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
PERSON_DOCS = LITERAL_PERSON_DOCUMENTS
CATALOG = MASTER_CATALOG

OUT_TSV = TRUNCATED_PERSON_CANDIDATES
OUT_REPORT = TRUNCATED_PERSON_CANDIDATES_REPORT

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def split_pipe(v):
    return [x.strip() for x in (v or "").split(" | ") if x.strip()]

def initials_and_tail(person):
    person = norm(person)
    m = re.match(r"^((?:[А-ЯЁ]\.){1,3})\s*(.+)$", person)
    if not m:
        return "", person
    return m.group(1), m.group(2)

def sim(a, b):
    return round(SequenceMatcher(None, a.casefold(), b.casefold()).ratio(), 4)

people = []
with PEOPLE.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        r["initials"], r["tail"] = initials_and_tail(r["person"])
        people.append(r)

docs_by_person = {}
with PERSON_DOCS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        docs_by_person.setdefault(r["person"], []).append(r)

truncated = []
for p in people:
    raw_forms = split_pipe(p.get("raw_forms"))
    if p["person"].endswith("-") or any(x.endswith("-") for x in raw_forms):
        truncated.append(p)

rows = []

for t in truncated:
    t_person = t["person"]
    t_initials = t["initials"]
    t_tail = t["tail"].rstrip("-")
    t_docs = docs_by_person.get(t_person, [])

    candidates = []

    for p in people:
        if p["person"] == t_person:
            continue

        if t_initials and p["initials"] and t_initials != p["initials"]:
            continue

        p_tail = p["tail"].rstrip("-")

        if not t_tail:
            continue

        prefix = p_tail.casefold().startswith(t_tail.casefold()) or t_tail.casefold().startswith(p_tail.casefold())
        similarity = sim(t_tail, p_tail)

        if prefix or similarity >= 0.72:
            candidates.append({
                "candidate_person": p["person"],
                "candidate_document_count": p.get("document_count", ""),
                "candidate_total_words": p.get("total_words", ""),
                "candidate_raw_forms": p.get("raw_forms", ""),
                "candidate_similarity": similarity,
                "candidate_reason": "prefix" if prefix else "similarity",
            })

    candidates = sorted(
        candidates,
        key=lambda x: (
            0 if x["candidate_reason"] == "prefix" else 1,
            -float(x["candidate_similarity"]),
            -int(x["candidate_document_count"] or 0),
        )
    )

    if not candidates:
        rows.append({
            "truncated_person": t_person,
            "truncated_raw_forms": t.get("raw_forms", ""),
            "document_count": t.get("document_count", ""),
            "total_words": t.get("total_words", ""),
            "first_date": t.get("first_date", ""),
            "last_date": t.get("last_date", ""),
            "document_titles": " | ".join(d.get("document_title", "") for d in t_docs[:5]),
            "candidate_person": "",
            "candidate_document_count": "",
            "candidate_total_words": "",
            "candidate_raw_forms": "",
            "candidate_similarity": "",
            "candidate_reason": "no_candidate",
            "suggested_decision": "review_source_document",
        })
    else:
        for c in candidates[:5]:
            rows.append({
                "truncated_person": t_person,
                "truncated_raw_forms": t.get("raw_forms", ""),
                "document_count": t.get("document_count", ""),
                "total_words": t.get("total_words", ""),
                "first_date": t.get("first_date", ""),
                "last_date": t.get("last_date", ""),
                "document_titles": " | ".join(d.get("document_title", "") for d in t_docs[:5]),
                "candidate_person": c["candidate_person"],
                "candidate_document_count": c["candidate_document_count"],
                "candidate_total_words": c["candidate_total_words"],
                "candidate_raw_forms": c["candidate_raw_forms"],
                "candidate_similarity": c["candidate_similarity"],
                "candidate_reason": c["candidate_reason"],
                "suggested_decision": "review_candidate",
            })

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "truncated_person", "truncated_raw_forms", "document_count", "total_words",
        "first_date", "last_date", "document_titles",
        "candidate_person", "candidate_document_count", "candidate_total_words",
        "candidate_raw_forms", "candidate_similarity", "candidate_reason",
        "suggested_decision",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials truncated persons diagnosis")
report.append("")
report.append(f"Truncated people: {len(truncated)}")
report.append(f"Candidate rows: {len(rows)}")
report.append("")
report.append("Truncated names:")
for t in truncated:
    report.append(f"{t.get('document_count')}\t{t['person']}\tRAW={t.get('raw_forms', '')}")
report.append("")
report.append("Candidate preview:")
for r in rows[:120]:
    report.append(
        f"{r['truncated_person']}\t→\t{r['candidate_person'] or 'NO_CANDIDATE'}"
        f"\t{r['candidate_reason']}\t{r['candidate_similarity']}"
        f"\tTITLE={r['document_titles'][:160]}"
    )

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
