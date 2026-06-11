#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"

OUT_YEAR = BASE / "showtrials_dates_by_year.tsv"
OUT_MONTH = BASE / "showtrials_dates_by_month.tsv"
OUT_OUTLIERS = BASE / "showtrials_date_outliers.tsv"
OUT_REPORT = BASE / "showtrials_date_audit_report.txt"

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

by_year = defaultdict(lambda: {"docs": 0, "words": 0, "chars": 0})
by_month = defaultdict(lambda: {"docs": 0, "words": 0, "chars": 0})
outliers = []

for d in docs:
    date = d.get("document_date", "")
    year = date[:4] if len(date) >= 4 else "unknown"
    month = date[:7] if len(date) >= 7 else "unknown"

    by_year[year]["docs"] += 1
    by_year[year]["words"] += d["content_words"]
    by_year[year]["chars"] += d["content_chars"]

    by_month[month]["docs"] += 1
    by_month[month]["words"] += d["content_words"]
    by_month[month]["chars"] += d["content_chars"]

    try:
        y = int(year)
        if y < 1927 or y > 1938:
            outliers.append(d)
    except Exception:
        outliers.append(d)

with OUT_YEAR.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["year", "document_count", "total_words", "total_chars", "avg_words"])
    for year, data in sorted(by_year.items()):
        avg = round(data["words"] / data["docs"], 2) if data["docs"] else 0
        w.writerow([year, data["docs"], data["words"], data["chars"], avg])

with OUT_MONTH.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["month", "document_count", "total_words", "total_chars", "avg_words"])
    for month, data in sorted(by_month.items()):
        avg = round(data["words"] / data["docs"], 2) if data["docs"] else 0
        w.writerow([month, data["docs"], data["words"], data["chars"], avg])

with OUT_OUTLIERS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title", "primary_process",
        "primary_collection", "category_names", "tag_names", "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for d in sorted(outliers, key=lambda r: r.get("document_date", "")):
        w.writerow({k: d.get(k, "") for k in fields})

report = []
report.append("ShowTrials date audit")
report.append("")
report.append(f"Documents loaded: {len(docs)}")
report.append(f"Years: {len(by_year)}")
report.append(f"Months: {len(by_month)}")
report.append(f"Outliers outside 1927-1938: {len(outliers)}")
report.append("")
report.append("Documents by year:")
for year, data in sorted(by_year.items()):
    report.append(f"{year}\t{data['docs']}\t{data['words']}")
report.append("")
report.append("Top months by document count:")
for month, data in sorted(by_month.items(), key=lambda x: x[1]["docs"], reverse=True)[:40]:
    report.append(f"{month}\t{data['docs']}\t{data['words']}")
report.append("")
report.append("Outliers:")
for d in sorted(outliers, key=lambda r: r.get("document_date", ""))[:50]:
    report.append(f"{d.get('document_date')}\t{d.get('primary_process')}\t{d.get('document_title')}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_YEAR)
print(OUT_MONTH)
print(OUT_OUTLIERS)
print(OUT_REPORT)
