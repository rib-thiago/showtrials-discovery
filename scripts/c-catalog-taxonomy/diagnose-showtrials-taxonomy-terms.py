#!/usr/bin/env python3
import csv
import json
import subprocess
from pathlib import Path
from urllib.parse import quote

BASE = Path("/tmp/showtrials-discovery")
OUT_CATEGORIES_JSON = BASE / "showtrials_categories.json"
OUT_TAGS_JSON = BASE / "showtrials_tags.json"
OUT_TSV = BASE / "showtrials_taxonomy_terms.tsv"
OUT_REPORT = BASE / "showtrials_taxonomy_terms_report.txt"

def curl_json(url, out):
    subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", "60", url, "-o", str(out)],
        check=True
    )
    return json.loads(out.read_text(encoding="utf-8"))

categories = curl_json(
    "http://showtrials.ru/wp-json/wp/v2/categories?per_page=100&page=1",
    OUT_CATEGORIES_JSON
)

tags = curl_json(
    "http://showtrials.ru/wp-json/wp/v2/tags?per_page=100&page=1",
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

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
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

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
