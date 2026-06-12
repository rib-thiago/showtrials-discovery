#!/usr/bin/env python3
import argparse
import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ENTITY_CATEGORIES,
    ENTITY_COLLECTIONS,
    ENTITY_PROCESSES,
    ENTITY_TAGS,
    MASTER_CATALOG,
    ensure_parent,
)

CATALOG = MASTER_CATALOG

ENTITY_FILES = {
    "processes": ENTITY_PROCESSES,
    "collections": ENTITY_COLLECTIONS,
    "categories": ENTITY_CATEGORIES,
    "tags": ENTITY_TAGS,
}

def norm(s):
    return (s or "").casefold().strip()

def contains(haystack, needle):
    if not needle:
        return True
    return norm(needle) in norm(haystack)

def split_pipe(value):
    return [x.strip() for x in (value or "").split(" | ") if x.strip()]

def to_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

def load_catalog(path=CATALOG):
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        r["content_words"] = to_int(r.get("content_words"))
        r["content_chars"] = to_int(r.get("content_chars"))
        r["year"] = (r.get("document_date") or "")[:4]
    return rows

def load_entities(kind):
    path = ENTITY_FILES[kind]
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def match_multi_field(row, field, query):
    if not query:
        return True
    values = split_pipe(row.get(field))
    return any(contains(v, query) for v in values)

def filter_rows(rows, args):
    out = []
    for r in rows:
        if args.process and not contains(r.get("primary_process"), args.process):
            continue
        if args.collection and not contains(r.get("primary_collection"), args.collection):
            continue
        if args.category and not match_multi_field(r, "category_names", args.category):
            continue
        if args.tag and not match_multi_field(r, "tag_names", args.tag):
            continue
        if args.title and not contains(r.get("document_title"), args.title):
            continue
        if args.slug and not contains(r.get("slug"), args.slug):
            continue
        if args.url and not contains(r.get("document_url"), args.url):
            continue
        if args.year and r.get("year") != str(args.year):
            continue
        if args.words_min is not None and r["content_words"] < args.words_min:
            continue
        if args.words_max is not None and r["content_words"] > args.words_max:
            continue
        if args.has_tag and not r.get("tag_names"):
            continue
        if args.no_tag and r.get("tag_names"):
            continue
        out.append(r)
    return out

def sort_rows(rows, sort_key):
    reverse = True
    if sort_key == "date":
        return sorted(rows, key=lambda r: r.get("document_date") or "")
    if sort_key == "date_desc":
        return sorted(rows, key=lambda r: r.get("document_date") or "", reverse=True)
    if sort_key == "words":
        return sorted(rows, key=lambda r: r["content_words"], reverse=True)
    if sort_key == "words_asc":
        return sorted(rows, key=lambda r: r["content_words"])
    if sort_key == "title":
        return sorted(rows, key=lambda r: norm(r.get("document_title")))
    return rows

def print_table(rows, limit):
    fields = ["document_post_id", "document_date", "content_words", "primary_process", "primary_collection", "document_title", "document_url"]
    print("\t".join(["id", "date", "words", "process", "collection", "title", "url"]))
    for r in rows[:limit]:
        print("\t".join(str(r.get(f, "")) for f in fields))

def print_detail(rows, limit):
    for idx, r in enumerate(rows[:limit], start=1):
        print(f"#{idx}  ID: {r.get('document_post_id')}")
        print(f"DATE: {r.get('document_date')}")
        print(f"WORDS: {r.get('content_words')}")
        print(f"TITLE: {r.get('document_title')}")
        print(f"PROCESS: {r.get('primary_process')}")
        print(f"COLLECTION: {r.get('primary_collection')}")
        print(f"CATEGORIES: {r.get('category_names')}")
        print(f"TAGS: {r.get('tag_names')}")
        print(f"URL: {r.get('document_url')}")
        print()

def export_tsv(rows, path):
    if not rows:
        ensure_parent(path).write_text("", encoding="utf-8")
        return
    with ensure_parent(path).open("w", encoding="utf-8", newline="") as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(rows)

def list_entities(kind, query=None):
    rows = load_entities(kind)
    rows = [r for r in rows if not query or contains(r.get("entity_name"), query) or contains(r.get("wp_slug"), query)]
    rows = sorted(rows, key=lambda r: to_int(r.get("total_words")), reverse=True)

    print("\t".join(["name", "docs", "words", "slug"]))
    for r in rows:
        print("\t".join([
            r.get("entity_name", ""),
            r.get("document_count", ""),
            r.get("total_words", ""),
            r.get("wp_slug", ""),
        ]))

def main():
    p = argparse.ArgumentParser(
        description="Search the local ShowTrials master catalog TSV."
    )

    p.add_argument("--catalog", default=str(CATALOG), help="Path to master catalog TSV")

    p.add_argument("--list", choices=["processes", "collections", "categories", "tags"], help="List available entities")
    p.add_argument("--list-filter", help="Filter entity list by name/slug")

    p.add_argument("--process", help="Filter by primary process")
    p.add_argument("--collection", help="Filter by primary collection")
    p.add_argument("--category", help="Filter by category name")
    p.add_argument("--tag", help="Filter by tag name")
    p.add_argument("--title", help="Filter by document title")
    p.add_argument("--slug", help="Filter by slug")
    p.add_argument("--url", help="Filter by URL")
    p.add_argument("--year", help="Filter by year YYYY")
    p.add_argument("--words-min", type=int, help="Minimum word count")
    p.add_argument("--words-max", type=int, help="Maximum word count")
    p.add_argument("--has-tag", action="store_true", help="Only documents with tags")
    p.add_argument("--no-tag", action="store_true", help="Only documents without tags")

    p.add_argument("--sort", choices=["date", "date_desc", "words", "words_asc", "title"], default="date_desc")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--format", choices=["table", "detail"], default="table")
    p.add_argument("--export-tsv", help="Export matching rows to TSV")
    p.add_argument("--count-only", action="store_true")

    args = p.parse_args()

    if args.list:
        list_entities(args.list, args.list_filter)
        return

    rows = load_catalog(Path(args.catalog))
    rows = filter_rows(rows, args)
    rows = sort_rows(rows, args.sort)

    if args.export_tsv:
        export_tsv(rows, Path(args.export_tsv))

    if args.count_only:
        print(len(rows))
        return

    print(f"Matches: {len(rows)}")
    print()

    if args.format == "detail":
        print_detail(rows, args.limit)
    else:
        print_table(rows, args.limit)

if __name__ == "__main__":
    main()
