#!/usr/bin/env python3
import argparse
import csv
import sys
import re
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")
SEARCH_CORPUS = BASE / "showtrials_search_corpus.tsv"

csv.field_size_limit(sys.maxsize)

def tokenize(s):
    return re.findall(r"[\wА-Яа-яЁё]+", (s or "").casefold())

def contains_all(text, terms):
    t = text.casefold()
    return all(term.casefold() in t for term in terms)

def score_text(text, query_terms):
    tokens = tokenize(text)
    counts = Counter(tokens)
    score = 0
    for term in query_terms:
        term_cf = term.casefold()
        score += text.casefold().count(term_cf) * 5
        score += counts.get(term_cf, 0) * 10
    return score

def load_rows(path):
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def main():
    p = argparse.ArgumentParser(description="Full-text search over local ShowTrials exported corpus.")
    p.add_argument("query", nargs="+", help="Search query terms")
    p.add_argument("--corpus", default=str(SEARCH_CORPUS))
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--all", action="store_true", help="Require all query terms as substrings")
    p.add_argument("--process")
    p.add_argument("--collection")
    p.add_argument("--tag")
    p.add_argument("--category")
    p.add_argument("--format", choices=["table", "detail"], default="table")
    p.add_argument("--export-tsv")
    args = p.parse_args()

    query_terms = args.query
    results = []

    for r in load_rows(args.corpus):
        text = r.get("search_text", "")

        if args.process and args.process.casefold() not in r.get("primary_process", "").casefold():
            continue
        if args.collection and args.collection.casefold() not in r.get("primary_collection", "").casefold():
            continue
        if args.tag and args.tag.casefold() not in r.get("tag_names", "").casefold():
            continue
        if args.category and args.category.casefold() not in r.get("category_names", "").casefold():
            continue

        if args.all and not contains_all(text, query_terms):
            continue

        score = score_text(text, query_terms)
        if score <= 0:
            continue

        r["_score"] = score
        results.append(r)

    results.sort(key=lambda r: int(r["_score"]), reverse=True)

    if args.export_tsv:
        out = Path(args.export_tsv)
        with out.open("w", encoding="utf-8", newline="") as f:
            fields = [k for k in results[0].keys() if k != "search_text"] if results else []
            w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
            w.writeheader()
            for r in results:
                w.writerow({k: v for k, v in r.items() if k != "search_text"})

    print(f"Matches: {len(results)}")
    print()

    if args.format == "table":
        print("score\tid\tdate\twords\tprocess\tcollection\ttags\ttitle\turl")
        for r in results[:args.limit]:
            print("\t".join([
                str(r["_score"]),
                r.get("document_post_id", ""),
                r.get("document_date", ""),
                r.get("content_words", ""),
                r.get("primary_process", ""),
                r.get("primary_collection", ""),
                r.get("tag_names", ""),
                r.get("document_title", ""),
                r.get("document_url", ""),
            ]))
    else:
        for i, r in enumerate(results[:args.limit], start=1):
            print(f"#{i} SCORE: {r['_score']}")
            print(f"ID: {r.get('document_post_id')}")
            print(f"DATE: {r.get('document_date')}")
            print(f"WORDS: {r.get('content_words')}")
            print(f"TITLE: {r.get('document_title')}")
            print(f"PROCESS: {r.get('primary_process')}")
            print(f"COLLECTION: {r.get('primary_collection')}")
            print(f"CATEGORIES: {r.get('category_names')}")
            print(f"TAGS: {r.get('tag_names')}")
            print(f"URL: {r.get('document_url')}")
            print()

if __name__ == "__main__":
    main()
