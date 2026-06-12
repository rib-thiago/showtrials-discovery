#!/usr/bin/env python3
import csv, json, re, html
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    DOCUMENT_INDEX,
    DOCUMENT_INDEX_REPORT,
    POSTS_JSON_DIR,
    ensure_parent,
)

POSTS_DIR = POSTS_JSON_DIR
OUT_TSV = DOCUMENT_INDEX
OUT_REPORT = DOCUMENT_INDEX_REPORT

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

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
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

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
