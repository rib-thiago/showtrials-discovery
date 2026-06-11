#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"

OUT_MATRIX = BASE / "showtrials_tag_process_matrix.tsv"
OUT_EXCLUSIVE = BASE / "showtrials_tag_process_exclusive.tsv"
OUT_REPORT = BASE / "showtrials_tag_process_audit_report.txt"

def split_pipe(value):
    return [x.strip() for x in (value or "").split(" | ") if x.strip()]

def to_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

for d in docs:
    d["content_words"] = to_int(d.get("content_words"))
    d["content_chars"] = to_int(d.get("content_chars"))

agg = defaultdict(lambda: {"docs": set(), "words": 0})
tag_processes = defaultdict(set)

for d in docs:
    process = d.get("primary_process") or "UNSET"
    tags = split_pipe(d.get("tag_names"))
    if not tags:
        tags = ["UNSET"]
    for tag in tags:
        key = (tag, process)
        doc_id = d["document_post_id"]
        if doc_id not in agg[key]["docs"]:
            agg[key]["docs"].add(doc_id)
            agg[key]["words"] += d["content_words"]
        tag_processes[tag].add(process)

with OUT_MATRIX.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["tag", "process", "document_count", "total_words"])
    for (tag, process), data in sorted(agg.items(), key=lambda x: (x[0][0], -len(x[1]["docs"]))):
        w.writerow([tag, process, len(data["docs"]), data["words"]])

with OUT_EXCLUSIVE.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["tag", "process_count", "processes"])
    for tag, processes in sorted(tag_processes.items(), key=lambda x: (len(x[1]), x[0])):
        w.writerow([tag, len(processes), " | ".join(sorted(processes))])

exclusive = {tag: ps for tag, ps in tag_processes.items() if len(ps) == 1 and tag != "UNSET"}
shared = {tag: ps for tag, ps in tag_processes.items() if len(ps) > 1 and tag != "UNSET"}

report = []
report.append("ShowTrials tag/process audit")
report.append("")
report.append(f"Documents loaded: {len(docs)}")
report.append(f"Tags including UNSET: {len(tag_processes)}")
report.append(f"Exclusive tags: {len(exclusive)}")
report.append(f"Shared tags: {len(shared)}")
report.append("")
report.append("Exclusive tags:")
for tag, ps in sorted(exclusive.items(), key=lambda x: list(x[1])[0] + x[0]):
    report.append(f"{tag}\t{next(iter(ps))}")
report.append("")
report.append("Shared tags:")
for tag, ps in sorted(shared.items(), key=lambda x: (-len(x[1]), x[0])):
    report.append(f"{tag}\t{len(ps)}\t{' | '.join(sorted(ps))}")
report.append("")
report.append("Top tag-process pairs by document count:")
for (tag, process), data in sorted(agg.items(), key=lambda x: len(x[1]["docs"]), reverse=True)[:40]:
    report.append(f"{len(data['docs'])}\t{data['words']}\t{tag}\t{process}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_MATRIX)
print(OUT_EXCLUSIVE)
print(OUT_REPORT)
