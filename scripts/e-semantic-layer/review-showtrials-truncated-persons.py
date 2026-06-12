#!/usr/bin/env python3
import argparse
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PERSON_ALIASES_MANUAL,
    TRUNCATED_PERSON_CANDIDATES,
    ensure_parent,
)

CANDIDATES = TRUNCATED_PERSON_CANDIDATES
OUT_MANUAL = PERSON_ALIASES_MANUAL

FIELDS = ["raw_person", "canonical_person", "decision", "confidence", "reason", "notes"]

def append_decision(path, row):
    exists = path.exists()
    with ensure_parent(path).open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
        if not exists:
            w.writeheader()
        w.writerow(row)

def main():
    p = argparse.ArgumentParser(description="Review truncated ShowTrials person names.")
    p.add_argument("--candidates", default=str(CANDIDATES))
    p.add_argument("--out", default=str(OUT_MANUAL))
    p.add_argument("--limit", type=int)
    args = p.parse_args()

    with Path(args.candidates).open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    grouped = {}
    for r in rows:
        grouped.setdefault(r["truncated_person"], []).append(r)

    items = list(grouped.items())
    if args.limit:
        items = items[:args.limit]

    print(f"Truncated names to review: {len(items)}")
    print(f"Output manual TSV: {args.out}")
    print()
    print("Commands:")
    print("  number = approve candidate number")
    print("  c      = custom canonical")
    print("  n      = reject / keep unresolved")
    print("  s      = skip")
    print("  q      = quit")
    print()

    for idx, (trunc, candidates) in enumerate(items, start=1):
        print("=" * 80)
        print(f"[{idx}/{len(items)}]")
        print(f"TRUNCATED: {trunc}")
        print(f"Raw forms: {candidates[0].get('truncated_raw_forms')}")
        print(f"Docs: {candidates[0].get('document_count')}  Words: {candidates[0].get('total_words')}")
        print(f"Dates: {candidates[0].get('first_date')} → {candidates[0].get('last_date')}")
        print()
        print("Titles:")
        for title in candidates[0].get("document_titles", "").split(" | ")[:5]:
            if title:
                print(f"  - {title}")
        print()
        print("Candidates:")
        real_candidates = [c for c in candidates if c.get("candidate_person")]
        for i, c in enumerate(real_candidates, start=1):
            print(
                f"  {i}. {c['candidate_person']} "
                f"(docs={c['candidate_document_count']}, sim={c['candidate_similarity']}, reason={c['candidate_reason']})"
            )
        if not real_candidates:
            print("  NO CANDIDATES")
        print()

        cmd = input("[number/c/n/s/q] > ").strip().lower()

        if cmd == "q":
            break
        if cmd == "s" or cmd == "":
            continue
        if cmd == "n":
            append_decision(Path(args.out), {
                "raw_person": trunc,
                "canonical_person": "",
                "decision": "reject",
                "confidence": "reviewed",
                "reason": "truncated_name_review_reject",
                "notes": "left unresolved",
            })
            print("Rejected / unresolved.")
            continue
        if cmd == "c":
            canon = input("Canonical person: ").strip()
            if not canon:
                print("No canonical entered; skipped.")
                continue
        else:
            try:
                choice = int(cmd)
                canon = real_candidates[choice - 1]["candidate_person"]
            except Exception:
                print("Invalid choice; skipped.")
                continue

        append_decision(Path(args.out), {
            "raw_person": trunc,
            "canonical_person": canon,
            "decision": "approve",
            "confidence": "reviewed",
            "reason": "truncated_name_review",
            "notes": "approved truncated name alias",
        })

        print(f"Approved: {trunc} -> {canon}")

    print()
    print(f"Done. Manual TSV: {args.out}")

if __name__ == "__main__":
    main()
