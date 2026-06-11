#!/usr/bin/env python3
import csv, json, re, html
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")
POSTS_DIR = BASE / "posts-json"
OUT_TSV = BASE / "showtrials_document_index.tsv"
OUT_REPORT = BASE / "showtrials_document_index_report.txt"

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

rows = []
seen = set()

for path in sorted(POSTS_DIR.glob("posts-page-*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    for p in data:
        pid = str(p.get("id"))
        rows.append({
            "document_post_id": pid,
            "json_file": str(path),
            "title": clean(p.get("title", {}).get("rendered", "")),
            "date": p.get("date", ""),
            "modified": p.get("modified", ""),
            "slug": p.get("slug", ""),
            "url": p.get("link", ""),
            "content_chars_html": len(p.get("content", {}).get("rendered", "") or ""),
            "duplicate_id": "yes" if pid in seen else "no",
        })
        seen.add(pid)

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    fields = list(rows[0].keys())
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

dupes = [r for r in rows if r["duplicate_id"] == "yes"]

report = [
    "ShowTrials document index diagnosis",
    "",
    f"JSON files: {len(list(POSTS_DIR.glob('posts-page-*.json')))}",
    f"Rows indexed: {len(rows)}",
    f"Unique IDs: {len(seen)}",
    f"Duplicate IDs: {len(dupes)}",
]

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
