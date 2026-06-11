#!/usr/bin/env python3
import csv
import json
import re
import html
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
POSTS_DIR = BASE / "posts-json"
TERMS = BASE / "showtrials_taxonomy_terms.tsv"
COLLECTIONS = BASE / "showtrials_document_collections.tsv"

OUT_TSV = BASE / "showtrials_master_catalog.tsv"
OUT_REPORT = BASE / "showtrials_master_catalog_report.txt"

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def norm_url(url):
    url = url.strip()
    if url.startswith("https://showtrials.ru/"):
        url = "http://" + url[len("https://"):]
    if url.startswith("http://showtrials.ru") and not url.endswith("/"):
        parsed = urlparse(url)
        if "." not in Path(parsed.path).name:
            url += "/"
    return url

# Load taxonomy terms
term_by_type_id = {}
with TERMS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        term_by_type_id[(r["term_type"], str(r["id"]))] = r

# Load collection mappings
collections_by_doc = defaultdict(list)
with COLLECTIONS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["process_title"] == "ГЛАВНАЯ" and r["collection_title"] == "ГЛАВНАЯ":
            continue
        collections_by_doc[str(r["document_post_id"])].append(r)

# Load posts
posts = []
for path in sorted(POSTS_DIR.glob("posts-page-*.json")):
    posts.extend(json.loads(path.read_text(encoding="utf-8")))

rows = []
for p in posts:
    post_id = str(p.get("id"))
    title = clean(p.get("title", {}).get("rendered", ""))
    content = clean(p.get("content", {}).get("rendered", ""))

    cats = []
    cat_slugs = []
    for cid in p.get("categories", []) or []:
        term = term_by_type_id.get(("category", str(cid)))
        if term:
            cats.append(term["name"])
            cat_slugs.append(term["slug"])
        else:
            cats.append(str(cid))
            cat_slugs.append("")

    tags = []
    tag_slugs = []
    for tid in p.get("tags", []) or []:
        term = term_by_type_id.get(("tag", str(tid)))
        if term:
            tags.append(term["name"])
            tag_slugs.append(term["slug"])
        else:
            tags.append(str(tid))
            tag_slugs.append("")

    coll_rows = collections_by_doc.get(post_id, [])
    process_titles = sorted(set(r["process_title"] for r in coll_rows))
    collection_titles = sorted(set(r["collection_title"] for r in coll_rows))

    primary = coll_rows[0] if coll_rows else {}

    rows.append({
        "document_post_id": post_id,
        "document_title": title,
        "document_url": p.get("link", ""),
        "document_date": p.get("date", ""),
        "document_modified": p.get("modified", ""),
        "primary_process": primary.get("process_title", ""),
        "primary_collection": primary.get("collection_title", ""),
        "all_processes": " | ".join(process_titles),
        "all_collections": " | ".join(collection_titles),
        "category_ids": " | ".join(map(str, p.get("categories", []) or [])),
        "category_names": " | ".join(cats),
        "category_slugs": " | ".join(cat_slugs),
        "tag_ids": " | ".join(map(str, p.get("tags", []) or [])),
        "tag_names": " | ".join(tags),
        "tag_slugs": " | ".join(tag_slugs),
        "content_chars": len(content),
        "content_words": len(content.split()),
        "slug": p.get("slug", ""),
        "wp_author": p.get("author", ""),
        "wp_status": p.get("status", ""),
        "wp_type": p.get("type", ""),
    })

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    fields = list(rows[0].keys())
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

missing_collection = [r for r in rows if not r["primary_process"]]
with_categories = [r for r in rows if r["category_names"]]
with_tags = [r for r in rows if r["tag_names"]]

report = []
report.append("ShowTrials master catalog diagnosis")
report.append("")
report.append(f"Posts loaded: {len(posts)}")
report.append(f"Catalog rows: {len(rows)}")
report.append(f"Rows with collection mapping: {len(rows) - len(missing_collection)}")
report.append(f"Rows missing collection mapping: {len(missing_collection)}")
report.append(f"Rows with categories: {len(with_categories)}")
report.append(f"Rows with tags: {len(with_tags)}")
report.append("")
report.append("Top primary processes:")
proc_count = defaultdict(int)
for r in rows:
    proc_count[r["primary_process"] or "UNMAPPED"] += 1
for k, v in sorted(proc_count.items(), key=lambda x: x[1], reverse=True):
    report.append(f"{v}\t{k}")
report.append("")
report.append("Top category names:")
cat_count = defaultdict(int)
for r in rows:
    for c in filter(None, r["category_names"].split(" | ")):
        cat_count[c] += 1
for k, v in sorted(cat_count.items(), key=lambda x: x[1], reverse=True)[:50]:
    report.append(f"{v}\t{k}")
report.append("")
report.append("Top tag names:")
tag_count = defaultdict(int)
for r in rows:
    for t in filter(None, r["tag_names"].split(" | ")):
        tag_count[t] += 1
for k, v in sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:50]:
    report.append(f"{v}\t{k}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
