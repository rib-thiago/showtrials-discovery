#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    CATEGORIES_JSON,
    TAGS_JSON,
    TAXONOMY_TERMS,
    TAXONOMY_TERMS_REPORT,
    WP_CATEGORIES_ENDPOINT,
    WP_TAGS_ENDPOINT,
    ensure_parent,
)

OUT_CATEGORIES_JSON = CATEGORIES_JSON
OUT_TAGS_JSON = TAGS_JSON
OUT_TSV = TAXONOMY_TERMS
OUT_REPORT = TAXONOMY_TERMS_REPORT

def curl_json(url, out):
    subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", "60", url, "-o", str(ensure_parent(out))],
        check=True
    )
    return json.loads(out.read_text(encoding="utf-8"))

categories = curl_json(
    WP_CATEGORIES_ENDPOINT,
    OUT_CATEGORIES_JSON
)

tags = curl_json(
    WP_TAGS_ENDPOINT,
    OUT_TAGS_JSON
)

rows = []

for term_type, items in [("category", categories), ("tag", tags)]:
    for t in items:
        rows.append({
            "term_type": term_type,
            "id": t.get("id"),
            "count": t.get("count"),
            "name": t.get("name"),
            "slug": t.get("slug"),
            "link": t.get("link"),
            "parent": t.get("parent", ""),
            "description": t.get("description", ""),
        })

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
    fields = ["term_type", "id", "count", "name", "slug", "link", "parent", "description"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials taxonomy terms diagnosis")
report.append("")
report.append(f"Categories loaded: {len(categories)}")
report.append(f"Tags loaded: {len(tags)}")
report.append("")
report.append("Categories:")
for t in sorted(categories, key=lambda x: x.get("count", 0), reverse=True):
    report.append(f"{t.get('count')}\t{t.get('id')}\t{t.get('name')}\t{t.get('slug')}")
report.append("")
report.append("Tags:")
for t in sorted(tags, key=lambda x: x.get("count", 0), reverse=True):
    report.append(f"{t.get('count')}\t{t.get('id')}\t{t.get('name')}\t{t.get('slug')}")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
