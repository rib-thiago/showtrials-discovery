#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    CATEGORY_TREE,
    CATEGORY_TREE_REPORT,
    TAXONOMY_TERMS,
    ensure_parent,
)

TERMS = TAXONOMY_TERMS

OUT_TSV = CATEGORY_TREE
OUT_REPORT = CATEGORY_TREE_REPORT

categories = []
with TERMS.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["term_type"] == "category":
            r["count"] = int(r.get("count") or 0)
            r["parent"] = r.get("parent") or "0"
            categories.append(r)

by_id = {r["id"]: r for r in categories}
children = defaultdict(list)
for r in categories:
    children[r["parent"]].append(r["id"])

def depth_of(cid):
    d = 0
    cur = by_id.get(cid)
    seen = set()
    while cur and cur.get("parent") and cur["parent"] != "0" and cur["parent"] in by_id and cur["parent"] not in seen:
        seen.add(cur["parent"])
        d += 1
        cur = by_id.get(cur["parent"])
    return d

def path_of(cid):
    parts = []
    cur = by_id.get(cid)
    seen = set()
    while cur and cur["id"] not in seen:
        seen.add(cur["id"])
        parts.append(cur["name"])
        parent = cur.get("parent") or "0"
        if parent == "0":
            break
        cur = by_id.get(parent)
    return " / ".join(reversed(parts))

rows = []
for r in categories:
    rows.append({
        "category_id": r["id"],
        "parent_id": r["parent"],
        "depth": depth_of(r["id"]),
        "name": r["name"],
        "slug": r["slug"],
        "count": r["count"],
        "child_count": len(children.get(r["id"], [])),
        "path": path_of(r["id"]),
        "link": r["link"],
    })

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
    fields = ["category_id","parent_id","depth","name","slug","count","child_count","path","link"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: (r["path"], r["name"])))

def render_tree(pid="0", level=0):
    lines = []
    for cid in sorted(children.get(pid, []), key=lambda i: by_id[i]["name"]):
        r = by_id[cid]
        lines.append("  " * level + f"- {r['name']} [{r['id']}] count={r['count']}")
        lines.extend(render_tree(cid, level + 1))
    return lines

zero_doc = [r for r in categories if r["count"] == 0]
leaf = [r for r in categories if len(children.get(r["id"], [])) == 0]

report = []
report.append("ShowTrials category tree audit")
report.append("")
report.append(f"Categories: {len(categories)}")
report.append(f"Root categories: {len(children.get('0', []))}")
report.append(f"Zero-document categories: {len(zero_doc)}")
report.append(f"Leaf categories: {len(leaf)}")
report.append("")
report.append("Tree:")
report.extend(render_tree())
report.append("")
report.append("Zero-document categories:")
for r in zero_doc:
    report.append(f"{r['id']}\t{r['name']}\tparent={r['parent']}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
