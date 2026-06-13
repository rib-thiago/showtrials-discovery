#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import re
from html.parser import HTMLParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "t-translation-assets"
REPORTS_DIR = PROJECT_ROOT / "reports" / "t-translation-assets"

TEXT_DIR = Path("/srv/toolbox/shared/showtrials-review/translation-assets/extracted-text/mia/en-txt")

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.parts = []
        self._in_title = False
        self._skip = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._skip = True
        if tag in {"p", "br", "div", "h1", "h2", "h3", "h4", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style"}:
            self._skip = False
        if tag in {"p", "div", "h1", "h2", "h3", "h4", "li"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
        self.parts.append(data)

def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "iso-8859-1", "windows-1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")

def normalize_text(s: str) -> str:
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    lines = [" ".join(line.split()) for line in s.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip() + "\n"

def text_filename(source_id: str, href: str) -> str:
    slug = href.strip("/").replace("/", "__").replace(".htm", "").replace(".html", "")
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug).strip("_")
    return f"{source_id}__{slug}.txt"

def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    fetch_tsv = DATA_DIR / "translation_html_fetch.tsv"
    docs_tsv = DATA_DIR / "translation_html_documents.tsv"
    corpus_tsv = DATA_DIR / "translation_html_search_corpus.tsv"
    report_txt = REPORTS_DIR / "translation_html_extraction_report.txt"

    doc_rows = []
    corpus_rows = []

    with fetch_tsv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["status"] not in {"ok", "exists"}:
                continue

            html_path = Path(row["local_path"])
            if not html_path.exists():
                continue

            parser = TextParser()
            parser.feed(read_text(html_path))
            text = normalize_text("".join(parser.parts))
            title = " ".join(html.unescape(parser.title).split()) or row["label"]

            out = TEXT_DIR / text_filename(row["source_id"], row["href"])
            out.write_text(text, encoding="utf-8")

            words = len(re.findall(r"\w+", text))
            chars = len(text)

            doc_id = f"{row['source_id']}::{row['href']}"
            doc_rows.append({
                "asset_doc_id": doc_id,
                "source_id": row["source_id"],
                "href": row["href"],
                "url": row["url"],
                "label": row["label"],
                "title": title,
                "html_path": str(html_path),
                "text_path": str(out),
                "chars": str(chars),
                "words": str(words),
            })
            corpus_rows.append({
                "asset_doc_id": doc_id,
                "source_id": row["source_id"],
                "title": title,
                "label": row["label"],
                "url": row["url"],
                "text": text.replace("\n", " "),
            })

    with docs_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["asset_doc_id", "source_id", "href", "url", "label", "title", "html_path", "text_path", "chars", "words"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(doc_rows)

    with corpus_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["asset_doc_id", "source_id", "title", "label", "url", "text"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(corpus_rows)

    with report_txt.open("w", encoding="utf-8") as f:
        f.write("Translation HTML Extraction Report\n")
        f.write(f"documents_tsv\t{docs_tsv}\n")
        f.write(f"search_corpus_tsv\t{corpus_tsv}\n")
        f.write(f"text_dir\t{TEXT_DIR}\n")
        f.write(f"documents\t{len(doc_rows)}\n")
        f.write(f"total_chars\t{sum(int(r['chars']) for r in doc_rows)}\n")
        f.write(f"total_words\t{sum(int(r['words']) for r in doc_rows)}\n")

    print(docs_tsv)
    print(corpus_tsv)
    print(report_txt)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
