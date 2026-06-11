#!/usr/bin/env python3
import csv, json, re, html
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
PAGES = BASE / "pages-json/pages-page-1.json"
OUT_TSV = BASE / "showtrials_page_hierarchy.tsv"
OUT_REPORT = BASE / "showtrials_page_hierarchy_report.txt"

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

pages = json.loads(PAGES.read_text(encoding="utf-8"))
by_id = {p["id"]: p for p in pages}
children = defaultdict(list)

for p in pages:
    children[p.get("parent", 0)].append(p["id"])

def depth_of(pid):
    d = 0
    p = by_id.get(pid)
    while p and p.get("parent", 0) in by_id:
        d += 1
        p = by_id.get(p.get("parent", 0))
    return d

rows = []
for p in sorted(pages, key=lambda x: (depth_of(x["id"]), x.get("parent", 0), clean(x["title"]["rendered"]))):
    rows.append({
        "page_id": p["id"],
        "parent_id": p.get("parent", 0),
        "depth": depth_of(p["id"]),
        "slug": p.get("slug", ""),
        "title": clean(p.get("title", {}).get("rendered", "")),
        "url": p.get("link", ""),
        "content_chars": len(clean(p.get("content", {}).get("rendered", ""))),
        "content_words": len(clean(p.get("content", {}).get("rendered", "")).split()),
    })

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
    w.writeheader()
    w.writerows(rows)

def render_tree(pid=0, level=0):
    lines = []
    for cid in sorted(children.get(pid, []), key=lambda i: clean(by_id[i]["title"]["rendered"])):
        p = by_id[cid]
        lines.append("  " * level + f"- {clean(p['title']['rendered'])} [{cid}]")
        lines.extend(render_tree(cid, level + 1))
    return lines

report = []
report.append("ShowTrials page hierarchy diagnosis")
report.append("")
report.append(f"Pages: {len(pages)}")
report.append(f"Root pages: {len(children.get(0, []))}")
report.append("")
report.append("Tree:")
report.extend(render_tree())

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
