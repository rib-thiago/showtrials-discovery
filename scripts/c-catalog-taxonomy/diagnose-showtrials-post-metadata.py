#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    POSTS_JSON_DIR,
    POST_METADATA_FIELDS,
    POST_METADATA_REPORT,
    POST_METADATA_SAMPLE,
    POST_METADATA_TERMS,
    ensure_parent,
)

POSTS_DIR = POSTS_JSON_DIR

OUT_FIELDS = POST_METADATA_FIELDS
OUT_TERMS = POST_METADATA_TERMS
OUT_SAMPLE = POST_METADATA_SAMPLE
OUT_REPORT = POST_METADATA_REPORT

posts = []
for path in sorted(POSTS_DIR.glob("posts-page-*.json")):
    posts.extend(json.loads(path.read_text(encoding="utf-8")))

field_counter = Counter()
type_counter = Counter()
category_counter = Counter()
tag_counter = Counter()
format_counter = Counter()
status_counter = Counter()
template_counter = Counter()

meta_keys = Counter()
acf_keys = Counter()
embedded_keys = Counter()

samples = []

for p in posts:
    for key, value in p.items():
        field_counter[key] += 1
        type_counter[f"{key}:{type(value).__name__}"] += 1

    for cat in p.get("categories", []) or []:
        category_counter[str(cat)] += 1

    for tag in p.get("tags", []) or []:
        tag_counter[str(tag)] += 1

    format_counter[str(p.get("format", ""))] += 1
    status_counter[str(p.get("status", ""))] += 1
    template_counter[str(p.get("template", ""))] += 1

    meta = p.get("meta", {})
    if isinstance(meta, dict):
        for key, value in meta.items():
            meta_keys[f"{key}:{type(value).__name__}"] += 1

    acf = p.get("acf", {})
    if isinstance(acf, dict):
        for key, value in acf.items():
            acf_keys[f"{key}:{type(value).__name__}"] += 1

    emb = p.get("_embedded", {})
    if isinstance(emb, dict):
        for key, value in emb.items():
            embedded_keys[f"{key}:{type(value).__name__}"] += 1

    if len(samples) < 50:
        samples.append({
            "id": p.get("id"),
            "date": p.get("date"),
            "modified": p.get("modified"),
            "slug": p.get("slug"),
            "link": p.get("link"),
            "status": p.get("status"),
            "type": p.get("type"),
            "format": p.get("format"),
            "template": p.get("template"),
            "categories": ",".join(map(str, p.get("categories", []) or [])),
            "tags": ",".join(map(str, p.get("tags", []) or [])),
            "meta_keys": ",".join(sorted((p.get("meta") or {}).keys())) if isinstance(p.get("meta"), dict) else "",
            "acf_keys": ",".join(sorted((p.get("acf") or {}).keys())) if isinstance(p.get("acf"), dict) else "",
            "top_level_keys": ",".join(sorted(p.keys())),
        })

with ensure_parent(OUT_FIELDS).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["field", "count"])
    for key, count in sorted(field_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow([key, count])

with ensure_parent(OUT_TERMS).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["term_type", "term_id_or_value", "count"])
    for key, count in sorted(category_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["category", key, count])
    for key, count in sorted(tag_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["tag", key, count])
    for key, count in sorted(format_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["format", key, count])
    for key, count in sorted(status_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["status", key, count])
    for key, count in sorted(template_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow(["template", key, count])

with ensure_parent(OUT_SAMPLE).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "id","date","modified","slug","link","status","type","format","template",
        "categories","tags","meta_keys","acf_keys","top_level_keys"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(samples)

report = []
report.append("ShowTrials post metadata diagnosis")
report.append("")
report.append(f"Posts loaded: {len(posts)}")
report.append("")
report.append("Top-level fields:")
for key, count in sorted(field_counter.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{key}")
report.append("")
report.append("Field Python types:")
for key, count in sorted(type_counter.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{key}")
report.append("")
report.append("Categories:")
for key, count in sorted(category_counter.items(), key=lambda x: (-x[1], x[0]))[:50]:
    report.append(f"{count}\tcategory\t{key}")
report.append("")
report.append("Tags:")
for key, count in sorted(tag_counter.items(), key=lambda x: (-x[1], x[0]))[:50]:
    report.append(f"{count}\ttag\t{key}")
report.append("")
report.append("Meta keys:")
if meta_keys:
    for key, count in sorted(meta_keys.items(), key=lambda x: (-x[1], x[0])):
        report.append(f"{count}\t{key}")
else:
    report.append("none")
report.append("")
report.append("ACF keys:")
if acf_keys:
    for key, count in sorted(acf_keys.items(), key=lambda x: (-x[1], x[0])):
        report.append(f"{count}\t{key}")
else:
    report.append("none")
report.append("")
report.append("Embedded keys:")
if embedded_keys:
    for key, count in sorted(embedded_keys.items(), key=lambda x: (-x[1], x[0])):
        report.append(f"{count}\t{key}")
else:
    report.append("none")

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_FIELDS)
print(OUT_TERMS)
print(OUT_SAMPLE)
print(OUT_REPORT)
