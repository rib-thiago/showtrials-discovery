#!/usr/bin/env python3
import csv, json, re, html
from pathlib import Path
from urllib.parse import urlparse

BASE = Path("/tmp/showtrials-discovery")
POSTS_DIR = BASE / "posts-json"
PAGES = BASE / "pages-json/pages-page-1.json"
LINKS = BASE / "showtrials_page_links.tsv"

OUT_TSV = BASE / "showtrials_document_collections.tsv"
OUT_REPORT = BASE / "showtrials_document_collections_report.txt"

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

posts = []
for path in sorted(POSTS_DIR.glob("posts-page-*.json")):
    posts.extend(json.loads(path.read_text(encoding="utf-8")))

post_by_url = {}
for p in posts:
    post_by_url[norm_url(p.get("link", ""))] = p

pages = json.loads(PAGES.read_text(encoding="utf-8"))
page_by_id = {p["id"]: p for p in pages}

def page_title(pid):
    p = page_by_id.get(pid)
    if not p:
        return ""
    return clean(p.get("title", {}).get("rendered", ""))

def top_process(pid):
    path = []
    p = page_by_id.get(pid)
    while p:
        path.append(p)
        parent = p.get("parent", 0)
        p = page_by_id.get(parent)
    path = list(reversed(path))
    # first child under ГЛАВНАЯ/root is usually the process
    if len(path) >= 2 and clean(path[0].get("title", {}).get("rendered", "")) == "ГЛАВНАЯ":
        return clean(path[1].get("title", {}).get("rendered", ""))
    if path:
        return clean(path[0].get("title", {}).get("rendered", ""))
    return ""

rows = []
with LINKS.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for link in reader:
        if link["link_kind"] != "internal":
            continue
        target = norm_url(link["target_url"])
        post = post_by_url.get(target)
        if not post:
            continue

        source_page_id = int(link["source_page_id"])
        rows.append({
            "process_title": top_process(source_page_id),
            "collection_page_id": source_page_id,
            "collection_title": page_title(source_page_id),
            "collection_url": link["source_url"],
            "order_in_collection": link["order_in_page"],
            "document_post_id": post.get("id"),
            "document_title": clean(post.get("title", {}).get("rendered", "")),
            "document_url": post.get("link", ""),
            "document_date": post.get("date", ""),
            "document_modified": post.get("modified", ""),
            "anchor_text": link["anchor_text"],
            "content_words": len(clean(post.get("content", {}).get("rendered", "")).split()),
        })

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "process_title","collection_page_id","collection_title","collection_url",
        "order_in_collection","document_post_id","document_title","document_url",
        "document_date","document_modified","anchor_text","content_words"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

unique_docs = set(r["document_post_id"] for r in rows)
by_collection = {}
for r in rows:
    key = (r["process_title"], r["collection_title"])
    by_collection[key] = by_collection.get(key, 0) + 1

report = [
    "ShowTrials document collections diagnosis",
    "",
    f"Posts loaded: {len(posts)}",
    f"Mapped page→post links: {len(rows)}",
    f"Unique mapped posts: {len(unique_docs)}",
    f"Unmapped posts: {len(posts) - len(unique_docs)}",
    "",
    "Collections by mapped document count:",
]
for (proc, coll), count in sorted(by_collection.items(), key=lambda x: x[1], reverse=True):
    report.append(f"{count}\t{proc}\t{coll}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
