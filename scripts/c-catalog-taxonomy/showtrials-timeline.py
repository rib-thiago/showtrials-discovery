#!/usr/bin/env python3
import argparse, csv
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"

def norm(s): return (s or "").casefold().strip()
def contains(h, n): return not n or norm(n) in norm(h)
def split_pipe(v): return [x.strip() for x in (v or "").split(" | ") if x.strip()]
def to_int(v):
    try: return int(v or 0)
    except ValueError: return 0

def load_rows(path):
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        r["content_words"] = to_int(r.get("content_words"))
        r["content_chars"] = to_int(r.get("content_chars"))
    return rows

def match_multi(row, field, q):
    if not q: return True
    return any(contains(v, q) for v in split_pipe(row.get(field)))

def filter_rows(rows, args):
    out = []
    for r in rows:
        if args.process and not contains(r.get("primary_process"), args.process): continue
        if args.collection and not contains(r.get("primary_collection"), args.collection): continue
        if args.category and not match_multi(r, "category_names", args.category): continue
        if args.tag and not match_multi(r, "tag_names", args.tag): continue
        if args.title and not contains(r.get("document_title"), args.title): continue
        if args.words_min is not None and r["content_words"] < args.words_min: continue
        if args.words_max is not None and r["content_words"] > args.words_max: continue
        out.append(r)
    return out

def main():
    p = argparse.ArgumentParser(description="Timeline for ShowTrials catalog.")
    p.add_argument("--catalog", default=str(CATALOG))
    p.add_argument("--process")
    p.add_argument("--collection")
    p.add_argument("--category")
    p.add_argument("--tag")
    p.add_argument("--title")
    p.add_argument("--words-min", type=int)
    p.add_argument("--words-max", type=int)
    p.add_argument("--grain", choices=["year", "month", "day"], default="month")
    p.add_argument("--sort", choices=["date", "docs", "words"], default="date")
    args = p.parse_args()

    rows = filter_rows(load_rows(args.catalog), args)

    agg = defaultdict(lambda: {"docs": 0, "words": 0, "chars": 0})
    for r in rows:
        date = r.get("document_date", "")
        if args.grain == "year":
            key = date[:4] if len(date) >= 4 else "unknown"
        elif args.grain == "month":
            key = date[:7] if len(date) >= 7 else "unknown"
        else:
            key = date[:10] if len(date) >= 10 else "unknown"
        agg[key]["docs"] += 1
        agg[key]["words"] += r["content_words"]
        agg[key]["chars"] += r["content_chars"]

    items = list(agg.items())
    if args.sort == "docs":
        items.sort(key=lambda x: x[1]["docs"], reverse=True)
    elif args.sort == "words":
        items.sort(key=lambda x: x[1]["words"], reverse=True)
    else:
        items.sort(key=lambda x: x[0])

    print(f"Matches: {len(rows)}")
    print()
    print("period\tdocs\twords\tchars\tavg_words")
    for k, v in items:
        avg = round(v["words"] / v["docs"], 2) if v["docs"] else 0
        print(f"{k}\t{v['docs']}\t{v['words']}\t{v['chars']}\t{avg}")

if __name__ == "__main__":
    main()
