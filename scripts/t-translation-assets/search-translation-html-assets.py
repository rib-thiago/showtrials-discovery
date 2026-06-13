#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS = PROJECT_ROOT / "data" / "t-translation-assets" / "translation_html_search_corpus.tsv"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    terms = [t for t in re.split(r"\s+", args.query.strip()) if t]
    patterns = [re.compile(re.escape(t), re.I) for t in terms]

    results = []
    with CORPUS.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            text = row["text"]
            score = sum(len(p.findall(text)) for p in patterns)
            title_score = sum(len(p.findall(row["title"] + " " + row["label"])) for p in patterns)
            total = score + 5 * title_score
            if total:
                snippet_pos = min((m.start() for p in patterns for m in p.finditer(text)), default=0)
                snippet = text[max(0, snippet_pos - 160):snippet_pos + 360]
                results.append((total, row, snippet))

    results.sort(key=lambda x: x[0], reverse=True)

    print(f"Results: {len(results)}")
    for score, row, snippet in results[:args.limit]:
        print("=" * 80)
        print(f"[{score}] {row['asset_doc_id']}")
        print(f"Title: {row['title']}")
        print(f"Label: {row['label']}")
        print(f"Source: {row['source_id']}")
        print(f"URL: {row['url']}")
        print()
        print(snippet)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
