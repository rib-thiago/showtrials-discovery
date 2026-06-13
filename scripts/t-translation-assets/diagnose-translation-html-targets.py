#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "t-translation-assets"
REPORTS_DIR = PROJECT_ROOT / "reports" / "t-translation-assets"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.links = []
        self._in_title = False
        self._current_href = None
        self._current_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "a":
            self._current_href = attrs.get("href")
            self._current_text = []

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False
        if tag.lower() == "a" and self._current_href:
            label = " ".join("".join(self._current_text).split())
            self.links.append((self._current_href, html.unescape(label)))
            self._current_href = None
            self._current_text = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._current_href:
            self._current_text.append(data)

def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "iso-8859-1", "windows-1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")

def source_id_for(path: Path) -> str:
    name = path.name.lower()
    if "bukharin" in name:
        return "mia_1938_bukharin_case_index"
    if "1936" in name or "moscow" in name or "court" in name:
        return "mia_1936_trotskyite_zinovievite_index"
    return re.sub(r"[^a-z0-9]+", "_", path.stem.lower()).strip("_")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html_files", nargs="+")
    ap.add_argument("--base-url", default="")
    args = ap.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    pages_tsv = DATA_DIR / "translation_html_pages.tsv"
    links_tsv = DATA_DIR / "translation_html_links.tsv"
    report_txt = REPORTS_DIR / "translation_html_diagnostics_report.txt"

    page_rows = []
    link_rows = []

    for item in args.html_files:
        path = Path(item)
        text = read_text(path)
        parser = LinkParser()
        parser.feed(text)

        source_id = source_id_for(path)
        title = " ".join(html.unescape(parser.title).split())

        for href, label in parser.links:
            resolved = urljoin(args.base_url, href) if args.base_url else href
            is_external = "yes" if re.match(r"^https?://", href) else "no"
            is_html = "yes" if href.lower().endswith((".htm", ".html")) else "no"
            link_rows.append({
                "source_id": source_id,
                "source_file": str(path),
                "href": href,
                "resolved_url": resolved,
                "label": label,
                "is_external": is_external,
                "is_relative": "no" if is_external == "yes" else "yes",
                "is_html": is_html,
            })

        page_rows.append({
            "source_id": source_id,
            "source_file": str(path),
            "title": title,
            "bytes": str(path.stat().st_size),
            "links_total": str(len(parser.links)),
            "html_links": str(sum(1 for href, _ in parser.links if href.lower().endswith((".htm", ".html")))),
            "relative_links": str(sum(1 for href, _ in parser.links if not re.match(r"^https?://", href))),
            "external_links": str(sum(1 for href, _ in parser.links if re.match(r"^https?://", href))),
        })

    with pages_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["source_id", "source_file", "title", "bytes", "links_total", "html_links", "relative_links", "external_links"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(page_rows)

    with links_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["source_id", "source_file", "href", "resolved_url", "label", "is_external", "is_relative", "is_html"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(link_rows)

    with report_txt.open("w", encoding="utf-8") as f:
        f.write("Translation HTML Diagnostics Report\n")
        f.write(f"pages_tsv\t{pages_tsv}\n")
        f.write(f"links_tsv\t{links_tsv}\n")
        f.write(f"pages\t{len(page_rows)}\n")
        f.write(f"links\t{len(link_rows)}\n\n")
        for row in page_rows:
            f.write(
                f"{row['source_id']}\t"
                f"links={row['links_total']}\t"
                f"html={row['html_links']}\t"
                f"relative={row['relative_links']}\t"
                f"title={row['title']}\n"
            )

    print(pages_tsv)
    print(links_tsv)
    print(report_txt)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
