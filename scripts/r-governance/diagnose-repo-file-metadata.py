#!/usr/bin/env python3
from pathlib import Path
import csv
import time

OUT = Path("repo-file-metadata.tsv")
IGNORE_DIRS = {".git", "__pycache__", ".codex", ".agents"}

rows = []

for p in sorted(Path(".").rglob("*")):
    if not p.is_file():
        continue
    if set(p.parts) & IGNORE_DIRS:
        continue

    st = p.stat()
    rows.append({
        "path": str(p).lstrip("./"),
        "suffix": p.suffix,
        "size_bytes": st.st_size,
        "mtime_epoch": int(st.st_mtime),
        "mtime_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
        "ctime_epoch": int(st.st_ctime),
        "ctime_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_ctime)),
    })

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {OUT} ({len(rows)} rows)")
