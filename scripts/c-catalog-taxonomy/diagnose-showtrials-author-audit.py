#!/usr/bin/env python3
import csv
import json
import subprocess
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"

OUT_USERS_JSON = BASE / "showtrials_users.json"
OUT_TSV = BASE / "showtrials_author_audit.tsv"
OUT_REPORT = BASE / "showtrials_author_audit_report.txt"

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

# Try public WordPress users endpoint; if blocked, continue with author IDs only.
users = []
try:
    subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", "60",
         "http://showtrials.ru/wp-json/wp/v2/users?per_page=100&page=1",
         "-o", str(OUT_USERS_JSON)],
        check=True
    )
    users = json.loads(OUT_USERS_JSON.read_text(encoding="utf-8"))
except Exception:
    OUT_USERS_JSON.write_text("[]\n", encoding="utf-8")
    users = []

user_by_id = {str(u.get("id")): u for u in users}

agg = defaultdict(lambda: {"docs": 0, "words": 0, "chars": 0})
for d in docs:
    author = str(d.get("wp_author", "") or "UNSET")
    agg[author]["docs"] += 1
    agg[author]["words"] += d["content_words"]
    agg[author]["chars"] += d["content_chars"]

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["author_id", "author_name", "author_slug", "document_count", "total_words", "total_chars", "avg_words"])
    for aid, data in sorted(agg.items(), key=lambda x: x[1]["docs"], reverse=True):
        u = user_by_id.get(aid, {})
        avg = round(data["words"] / data["docs"], 2) if data["docs"] else 0
        w.writerow([aid, u.get("name", ""), u.get("slug", ""), data["docs"], data["words"], data["chars"], avg])

report = []
report.append("ShowTrials author audit")
report.append("")
report.append(f"Documents loaded: {len(docs)}")
report.append(f"Author IDs in catalog: {len(agg)}")
report.append(f"Users loaded from API: {len(users)}")
report.append("")
for aid, data in sorted(agg.items(), key=lambda x: x[1]["docs"], reverse=True):
    u = user_by_id.get(aid, {})
    report.append(f"{aid}\t{u.get('name','')}\t{data['docs']}\t{data['words']}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_USERS_JSON)
print(OUT_TSV)
print(OUT_REPORT)
