#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS = PROJECT_ROOT / "data" / "t-translation-assets" / "ezhov_parallel_search_corpus.tsv"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--lang", choices=["en", "ru"], default=None)
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    patterns = [re.compile(re.escape(t), re.I) for t in args.query.split() if t]
    results = []

    with CORPUS.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if args.lang and row["language"] != args.lang:
                continue
            text = row["text"]
            score = sum(len(p.findall(text)) for p in patterns)
            score += 5 * sum(len(p.findall(row["title"])) for p in patterns)
            if score:
                pos = min((m.start() for p in patterns for m in p.finditer(text)), default=0)
                snippet = text[max(0, pos - 160):pos + 420]
                results.append((score, row, snippet))

    results.sort(key=lambda x: x[0], reverse=True)
    print(f"Results: {len(results)}")
    for score, row, snippet in results[:args.limit]:
        print("=" * 80)
        print(f"[{score}] {row['asset_doc_id']} {row['language']}")
        print(f"Title: {row['title']}")
        print(snippet)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
