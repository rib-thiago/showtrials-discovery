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

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.links = []
        self.text = []
        self._in_title = False
        self._skip = False
        self._href = None
        self._label = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._skip = True
        if tag == "a":
            self._href = attrs.get("href")
            self._label = []
        if tag in {"p", "br", "div", "h1", "h2", "h3", "li"}:
            self.text.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style"}:
            self._skip = False
        if tag == "a" and self._href:
            self.links.append((self._href, " ".join("".join(self._label).split())))
            self._href = None
            self._label = []
        if tag in {"p", "div", "h1", "h2", "h3", "li"}:
            self.text.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._href:
            self._label.append(data)
        if not self._skip:
            self.text.append(data)

def read_html(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "windows-1251", "iso-8859-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")

def clean_text(s: str) -> str:
    s = html.unescape(s).replace("\xa0", " ")
    lines = [" ".join(x.split()) for x in s.splitlines()]
    return "\n".join(x for x in lines if x).strip()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html_file")
    ap.add_argument("--base-url", default="http://perpetrator2004.narod.ru/")
    args = ap.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    path = Path(args.html_file)
    raw = read_html(path)
    parser = Parser()
    parser.feed(raw)

    text = clean_text("".join(parser.text))
    links_tsv = DATA_DIR / "precursor_perpetrator2004_links.tsv"
    report = REPORTS_DIR / "precursor_perpetrator2004_diagnostics_report.txt"
    text_out = Path("/srv/toolbox/shared/showtrials-review/translation-assets/extracted-text/precursor-sites/perpetrator2004")
    text_out.mkdir(parents=True, exist_ok=True)
    text_file = text_out / "perpetrator2004-index-sample.txt"
    text_file.write_text(text + "\n", encoding="utf-8")

    rows = []
    for href, label in parser.links:
        rows.append({
            "href": href,
            "resolved_url": urljoin(args.base_url, href),
            "label": label,
            "is_html": "yes" if href.lower().endswith((".htm", ".html")) else "no",
            "is_external": "yes" if re.match(r"^https?://", href) else "no",
        })

    with links_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["href", "resolved_url", "label", "is_html", "is_external"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    with report.open("w", encoding="utf-8") as f:
        f.write("Perpetrator2004 Precursor Diagnostics Report\n")
        f.write(f"source_file\t{path}\n")
        f.write(f"title\t{' '.join(html.unescape(parser.title).split())}\n")
        f.write(f"bytes\t{path.stat().st_size}\n")
        f.write(f"links\t{len(rows)}\n")
        f.write(f"html_links\t{sum(1 for r in rows if r['is_html'] == 'yes')}\n")
        word_count = len(re.findall(r"\w+", text))
        f.write(f"chars_clean_text\t{len(text)}\n")
        f.write(f"words_clean_text\t{word_count}\n")
        f.write(f"contains_ucoz_scripts\t{'yes' if 'ucoz' in raw.lower() or 'narod' in raw.lower() else 'no'}\n")
        f.write(f"contains_word_html\t{'yes' if 'Word.Document' in raw or 'Microsoft Word' in raw else 'no'}\n")
        f.write(f"links_tsv\t{links_tsv}\n")
        f.write(f"text_file\t{text_file}\n")

    print(links_tsv)
    print(report)
    print(text_file)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
