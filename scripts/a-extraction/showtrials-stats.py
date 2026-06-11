#!/usr/bin/env python3
import argparse, csv, statistics
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
        if args.year and (r.get("document_date", "")[:4] != str(args.year)): continue
        if args.words_min is not None and r["content_words"] < args.words_min: continue
        if args.words_max is not None and r["content_words"] > args.words_max: continue
        out.append(r)
    return out

def summarize(rows):
    words = [r["content_words"] for r in rows]
    chars = [r["content_chars"] for r in rows]
    if not rows:
        return {"docs":0,"words":0,"chars":0,"avg":0,"median":0,"min":0,"max":0}
    return {
        "docs": len(rows),
        "words": sum(words),
        "chars": sum(chars),
        "avg": round(sum(words)/len(words), 2),
        "median": statistics.median(words),
        "min": min(words),
        "max": max(words),
    }

def group(rows, field, multi=False):
    agg = defaultdict(list)
    for r in rows:
        keys = split_pipe(r.get(field)) if multi else [r.get(field) or "UNSET"]
        if not keys: keys = ["UNSET"]
        for k in keys:
            agg[k].append(r)
    return agg

def print_group(rows, field, label, multi=False, limit=30):
    print()
    print(f"By {label}:")
    print(f"{label}\tdocs\twords\tchars\tavg_words")
    items = []
    for k, rs in group(rows, field, multi).items():
        s = summarize(rs)
        items.append((k, s))
    items.sort(key=lambda x: x[1]["words"], reverse=True)
    for k, s in items[:limit]:
        print(f"{k}\t{s['docs']}\t{s['words']}\t{s['chars']}\t{s['avg']}")

def main():
    p = argparse.ArgumentParser(description="Stats for ShowTrials catalog.")
    p.add_argument("--catalog", default=str(CATALOG))
    p.add_argument("--process")
    p.add_argument("--collection")
    p.add_argument("--category")
    p.add_argument("--tag")
    p.add_argument("--title")
    p.add_argument("--year")
    p.add_argument("--words-min", type=int)
    p.add_argument("--words-max", type=int)
    p.add_argument("--group-by", choices=["process", "collection", "category", "tag", "year", "none"], default="none")
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args()

    rows = filter_rows(load_rows(args.catalog), args)
    s = summarize(rows)

    print("ShowTrials stats")
    print()
    print(f"Documents: {s['docs']}")
    print(f"Words: {s['words']}")
    print(f"Chars: {s['chars']}")
    print(f"Average words/document: {s['avg']}")
    print(f"Median words/document: {s['median']}")
    print(f"Min words/document: {s['min']}")
    print(f"Max words/document: {s['max']}")

    if args.group_by == "process":
        print_group(rows, "primary_process", "process", False, args.limit)
    elif args.group_by == "collection":
        print_group(rows, "primary_collection", "collection", False, args.limit)
    elif args.group_by == "category":
        print_group(rows, "category_names", "category", True, args.limit)
    elif args.group_by == "tag":
        print_group(rows, "tag_names", "tag", True, args.limit)
    elif args.group_by == "year":
        for r in rows:
            r["year"] = r.get("document_date", "")[:4] or "unknown"
        print_group(rows, "year", "year", False, args.limit)

if __name__ == "__main__":
    main()
