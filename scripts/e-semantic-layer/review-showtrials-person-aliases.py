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
    PERSON_MERGE_CANDIDATES,
    ensure_parent,
)

CANDIDATES = PERSON_MERGE_CANDIDATES
OUT_MANUAL = PERSON_ALIASES_MANUAL

FIELDS = [
    "raw_person",
    "canonical_person",
    "decision",
    "confidence",
    "reason",
    "notes",
]

def load_existing(path):
    existing = {}
    if not path.exists():
        return existing
    with path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            existing[r["raw_person"]] = r
    return existing

def append_decision(path, row):
    exists = path.exists()
    with ensure_parent(path).open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
        if not exists:
            w.writeheader()
        w.writerow(row)

def main():
    p = argparse.ArgumentParser(description="Interactively review ShowTrials person alias candidates.")
    p.add_argument("--candidates", default=str(CANDIDATES))
    p.add_argument("--out", default=str(OUT_MANUAL))
    p.add_argument("--confidence", choices=["high", "medium", "all"], default="high")
    p.add_argument("--limit", type=int)
    args = p.parse_args()

    existing = load_existing(Path(args.out))

    with Path(args.candidates).open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    rows = [r for r in rows if r.get("status") == "review"]
    if args.confidence != "all":
        rows = [r for r in rows if r.get("confidence") == args.confidence]
    if args.limit:
        rows = rows[:args.limit]

    print(f"Candidates to review: {len(rows)}")
    print(f"Output manual TSV: {args.out}")
    print()
    print("Commands:")
    print("  y = approve candidate_b -> suggested_canonical")
    print("  a = approve candidate_a -> suggested_canonical")
    print("  b = approve candidate_b -> candidate_a")
    print("  c = custom canonical")
    print("  n = reject")
    print("  s = skip")
    print("  q = quit")
    print()

    for idx, r in enumerate(rows, start=1):
        a = r["candidate_a"]
        b = r["candidate_b"]

        if a in existing and b in existing:
            continue

        print("=" * 80)
        print(f"[{idx}/{len(rows)}]")
        print(f"Confidence: {r['confidence']}")
        print(f"Reason: {r['reason']}")
        print(f"Shared initials: {r['shared_initials']}")
        print()
        print(f"A: {a}")
        print(f"   docs={r['documents_a']} words={r['words_a']}")
        print(f"   raw_forms={r['raw_forms_a']}")
        print()
        print(f"B: {b}")
        print(f"   docs={r['documents_b']} words={r['words_b']}")
        print(f"   raw_forms={r['raw_forms_b']}")
        print()
        print(f"Suggested canonical: {r['suggested_canonical']}")
        print()

        cmd = input("[y/a/b/c/n/s/q] > ").strip().lower()

        if cmd == "q":
            break
        if cmd == "s" or cmd == "":
            continue

        if cmd == "n":
            append_decision(Path(args.out), {
                "raw_person": b,
                "canonical_person": "",
                "decision": "reject",
                "confidence": r["confidence"],
                "reason": r["reason"],
                "notes": f"Rejected merge with {a}",
            })
            print("Rejected.")
            continue

        if cmd == "y":
            raw = b
            canon = r["suggested_canonical"]
        elif cmd == "a":
            raw = a
            canon = r["suggested_canonical"]
        elif cmd == "b":
            raw = b
            canon = a
        elif cmd == "c":
            raw = input("Raw person to map [A/B/custom]: ").strip()
            if raw.lower() == "a":
                raw = a
            elif raw.lower() == "b" or not raw:
                raw = b
            canon = input("Canonical person: ").strip()
            if not canon:
                print("No canonical entered; skipped.")
                continue
        else:
            print("Unknown command; skipped.")
            continue

        notes = input("Notes optional: ").strip()

        append_decision(Path(args.out), {
            "raw_person": raw,
            "canonical_person": canon,
            "decision": "approve",
            "confidence": r["confidence"],
            "reason": r["reason"],
            "notes": notes,
        })

        print(f"Approved: {raw} -> {canon}")

    print()
    print(f"Done. Manual decisions: {args.out}")

if __name__ == "__main__":
    main()
