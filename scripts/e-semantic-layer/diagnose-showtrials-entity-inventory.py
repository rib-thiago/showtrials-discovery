#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"
TERMS = BASE / "showtrials_taxonomy_terms.tsv"

OUT_PROCESSES = BASE / "showtrials_entities_processes.tsv"
OUT_COLLECTIONS = BASE / "showtrials_entities_collections.tsv"
OUT_CATEGORIES = BASE / "showtrials_entities_categories.tsv"
OUT_TAGS = BASE / "showtrials_entities_tags.tsv"
OUT_REPORT = BASE / "showtrials_entity_inventory_report.txt"

def split_pipe(value):
    return [x.strip() for x in (value or "").split(" | ") if x.strip()]

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

for d in docs:
    d["content_words"] = int(d.get("content_words") or 0)
    d["content_chars"] = int(d.get("content_chars") or 0)

term_meta = {}
with TERMS.open("r", encoding="utf-8", newline="") as f:
    for t in csv.DictReader(f, delimiter="\t"):
        term_meta[(t["term_type"], t["name"])] = t

def aggregate_single(field):
    agg = defaultdict(lambda: {"docs": set(), "words": 0, "chars": 0})
    for d in docs:
        key = d.get(field) or "UNSET"
        doc_id = d["document_post_id"]
        if doc_id not in agg[key]["docs"]:
            agg[key]["docs"].add(doc_id)
            agg[key]["words"] += d["content_words"]
            agg[key]["chars"] += d["content_chars"]
    return agg

def aggregate_multi(field):
    agg = defaultdict(lambda: {"docs": set(), "words": 0, "chars": 0})
    for d in docs:
        values = split_pipe(d.get(field))
        if not values:
            values = ["UNSET"]
        for key in values:
            doc_id = d["document_post_id"]
            if doc_id not in agg[key]["docs"]:
                agg[key]["docs"].add(doc_id)
                agg[key]["words"] += d["content_words"]
                agg[key]["chars"] += d["content_chars"]
    return agg

def write_entities(path, label, agg, term_type=None):
    with path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "entity_type", "entity_name", "document_count",
            "total_words", "total_chars", "avg_words",
            "wp_term_id", "wp_slug", "wp_parent", "wp_link"
        ]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()

        for name, data in sorted(agg.items(), key=lambda x: x[1]["words"], reverse=True):
            docs_count = len(data["docs"])
            avg_words = round(data["words"] / docs_count, 2) if docs_count else 0
            meta = term_meta.get((term_type, name), {}) if term_type else {}
            w.writerow({
                "entity_type": label,
                "entity_name": name,
                "document_count": docs_count,
                "total_words": data["words"],
                "total_chars": data["chars"],
                "avg_words": avg_words,
                "wp_term_id": meta.get("id", ""),
                "wp_slug": meta.get("slug", ""),
                "wp_parent": meta.get("parent", ""),
                "wp_link": meta.get("link", ""),
            })

process_agg = aggregate_single("primary_process")
collection_agg = aggregate_single("primary_collection")
category_agg = aggregate_multi("category_names")
tag_agg = aggregate_multi("tag_names")

write_entities(OUT_PROCESSES, "process", process_agg)
write_entities(OUT_COLLECTIONS, "collection", collection_agg)
write_entities(OUT_CATEGORIES, "category", category_agg, "category")
write_entities(OUT_TAGS, "tag", tag_agg, "tag")

report = []
report.append("ShowTrials entity inventory diagnosis")
report.append("")
report.append(f"Documents loaded: {len(docs)}")
report.append(f"Processes: {len(process_agg)}")
report.append(f"Collections: {len(collection_agg)}")
report.append(f"Categories: {len(category_agg)}")
report.append(f"Tags including UNSET: {len(tag_agg)}")
report.append("")
report.append("Top processes:")
for k, v in sorted(process_agg.items(), key=lambda x: x[1]["words"], reverse=True):
    report.append(f"{len(v['docs'])}\t{v['words']}\t{k}")
report.append("")
report.append("Top collections:")
for k, v in sorted(collection_agg.items(), key=lambda x: x[1]["words"], reverse=True):
    report.append(f"{len(v['docs'])}\t{v['words']}\t{k}")
report.append("")
report.append("Top categories:")
for k, v in sorted(category_agg.items(), key=lambda x: x[1]["words"], reverse=True)[:40]:
    report.append(f"{len(v['docs'])}\t{v['words']}\t{k}")
report.append("")
report.append("Top tags:")
for k, v in sorted(tag_agg.items(), key=lambda x: x[1]["words"], reverse=True)[:40]:
    report.append(f"{len(v['docs'])}\t{v['words']}\t{k}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PROCESSES)
print(OUT_COLLECTIONS)
print(OUT_CATEGORIES)
print(OUT_TAGS)
print(OUT_REPORT)
