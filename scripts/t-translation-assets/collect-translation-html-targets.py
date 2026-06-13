#!/usr/bin/env python3
from __future__ import annotations

import csv
import time
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "t-translation-assets"
REPORTS_DIR = PROJECT_ROOT / "reports" / "t-translation-assets"

PAYLOAD_DIR = Path("/srv/toolbox/shared/showtrials-review/translation-assets/source-documents/mia/html-pages")

SOURCES = {
    "mia_1936_trotskyite_zinovievite_index": {
        "base_url": "https://www.marxists.org/history/ussr/government/law/1936/moscow-trials/",
        "subdir": "1936-trotskyite-zinovievite",
    },
    "mia_1938_bukharin_case_index": {
        "base_url": "https://www.marxists.org/archive/bukharin/works/1938/trial/",
        "subdir": "1938-bukharin",
    },
}

def safe_name(href: str) -> str:
    return href.strip("/").replace("/", "__").replace("..", "up").replace("?", "_") or "index.html"

def download(url: str, out: Path) -> tuple[str, int, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "showtrials-discovery-t2/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        return "ok", len(body), ""
    except Exception as e:
        return "error", 0, str(e)

def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)

    links_tsv = DATA_DIR / "translation_html_links.tsv"
    fetch_tsv = DATA_DIR / "translation_html_fetch.tsv"
    report_txt = REPORTS_DIR / "translation_html_fetch_report.txt"

    rows = []
    with links_tsv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("is_html") != "yes":
                continue
            if row.get("is_external") == "yes":
                continue
            href = row["href"]
            if href.startswith("../"):
                continue
            rows.append(row)

    fetch_rows = []
    for row in rows:
        source_id = row["source_id"]
        source = SOURCES.get(source_id)
        if not source:
            continue

        href = row["href"]
        url = urljoin(source["base_url"], href)
        out = PAYLOAD_DIR / source["subdir"] / safe_name(href)

        status = "exists"
        size = out.stat().st_size if out.exists() else 0
        error = ""

        if not out.exists():
            status, size, error = download(url, out)
            time.sleep(0.4)

        fetch_rows.append({
            "source_id": source_id,
            "href": href,
            "url": url,
            "local_path": str(out),
            "label": row.get("label", ""),
            "status": status,
            "bytes": str(size),
            "error": error,
        })

    with fetch_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["source_id", "href", "url", "local_path", "label", "status", "bytes", "error"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(fetch_rows)

    ok = sum(1 for r in fetch_rows if r["status"] in ("ok", "exists"))
    err = sum(1 for r in fetch_rows if r["status"] == "error")

    with report_txt.open("w", encoding="utf-8") as f:
        f.write("Translation HTML Fetch Report\n")
        f.write(f"links_input\t{links_tsv}\n")
        f.write(f"fetch_tsv\t{fetch_tsv}\n")
        f.write(f"payload_dir\t{PAYLOAD_DIR}\n")
        f.write(f"planned\t{len(fetch_rows)}\n")
        f.write(f"ok_or_exists\t{ok}\n")
        f.write(f"errors\t{err}\n")

    print(fetch_tsv)
    print(report_txt)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
