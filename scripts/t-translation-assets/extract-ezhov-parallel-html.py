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
TEXT_DIR = Path("/srv/toolbox/shared/showtrials-review/translation-assets/extracted-text/ezhov")

EN_HTML = Path("/srv/toolbox/shared/showtrials-review/translation-assets/source-documents/ezhov/html/1939-ezhov-interrogations-en.html")
RU_HTML = Path("/srv/toolbox/shared/showtrials-review/translation-assets/source-documents/ezhov/html/1939-ezhov-interrogations-ru.html")

class BlockParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self._tag = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"h1", "h2", "h3", "p"}:
            self._tag = tag.lower()
            self._buf = []

    def handle_endtag(self, tag):
        if self._tag and tag.lower() == self._tag:
            text = " ".join(html.unescape("".join(self._buf)).split())
            if text:
                self.blocks.append((self._tag, text))
            self._tag = None
            self._buf = []

    def handle_data(self, data):
        if self._tag:
            self._buf.append(data)

def read_html(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "windows-1251", "iso-8859-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-zа-я0-9]+", "-", s, flags=re.I).strip("-")
    return s[:80] or "doc"

def split_docs(path: Path, lang: str):
    parser = BlockParser()
    parser.feed(read_html(path))

    docs = []
    current_title = None
    current_parts = []

    heading_re = re.compile(
        r"(Ezhov|Ежов|interrog|confession|допрос|показан|04\.|05\.|06\.|July|August|September|October|November|December|April|May|June)",
        re.I,
    )

    for tag, text in parser.blocks:
        is_doc_heading = (
            (
                tag in {"h3", "h2"}
                and heading_re.search(text)
            )
            or (
                tag == "p"
                and re.match(r"^(Ezhov interrog|Ezhov confession|Ezhov protocol|Ezhov’s|Показания|Допрос|Ezhov .*\.doc)", text, re.I)
            )
        )
        if is_doc_heading:
            if current_title and current_parts:
                docs.append((current_title, "\n".join(current_parts).strip()))
            current_title = text
            current_parts = [text]
        else:
            if current_title:
                current_parts.append(text)

    if current_title and current_parts:
        docs.append((current_title, "\n".join(current_parts).strip()))

    rows = []
    out_dir = TEXT_DIR / lang
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, (title, text) in enumerate(docs, start=1):
        doc_id = f"ezhov_1939_{lang}_{idx:03d}"
        out = out_dir / f"{doc_id}__{slugify(title)}.txt"
        out.write_text(text + "\n", encoding="utf-8")
        rows.append({
            "asset_doc_id": doc_id,
            "asset_group": "ezhov_1939_interrogations",
            "language": lang,
            "sequence": str(idx),
            "title": title,
            "text_path": str(out),
            "chars": str(len(text)),
            "words": str(len(re.findall(r'\w+', text))),
            "source_html": str(path),
        })
    return rows

def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    rows.extend(split_docs(EN_HTML, "en"))
    rows.extend(split_docs(RU_HTML, "ru"))

    docs_tsv = DATA_DIR / "ezhov_parallel_documents.tsv"
    corpus_tsv = DATA_DIR / "ezhov_parallel_search_corpus.tsv"
    report = REPORTS_DIR / "ezhov_parallel_extraction_report.txt"

    with docs_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["asset_doc_id", "asset_group", "language", "sequence", "title", "text_path", "chars", "words", "source_html"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    with corpus_tsv.open("w", encoding="utf-8", newline="") as f:
        fields = ["asset_doc_id", "asset_group", "language", "sequence", "title", "text"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for row in rows:
            text = Path(row["text_path"]).read_text(encoding="utf-8").replace("\n", " ")
            w.writerow({k: row[k] for k in fields if k != "text"} | {"text": text})

    with report.open("w", encoding="utf-8") as f:
        f.write("Ezhov Parallel HTML Extraction Report\n")
        f.write(f"documents_tsv\t{docs_tsv}\n")
        f.write(f"search_corpus_tsv\t{corpus_tsv}\n")
        f.write(f"text_dir\t{TEXT_DIR}\n")
        f.write(f"documents\t{len(rows)}\n")
        for lang in ("en", "ru"):
            subset = [r for r in rows if r["language"] == lang]
            f.write(f"{lang}_documents\t{len(subset)}\n")
            f.write(f"{lang}_chars\t{sum(int(r['chars']) for r in subset)}\n")

    print(docs_tsv)
    print(corpus_tsv)
    print(report)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
