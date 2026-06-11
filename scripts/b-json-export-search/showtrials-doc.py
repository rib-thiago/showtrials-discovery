#!/usr/bin/env python3
import argparse, csv, json, re, html, sys
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"
INDEX = BASE / "showtrials_document_index.tsv"

def clean_html(s):
    s = s or ""
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p\s*>", "\n\n", s, flags=re.I)
    s = re.sub(r"</div\s*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def load_tsv(path, key):
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return {str(r[key]): r for r in csv.DictReader(f, delimiter="\t")}

def load_post(doc_id, index):
    row = index.get(str(doc_id))
    if not row:
        raise SystemExit(f"Document ID not found: {doc_id}")

    path = Path(row["json_file"])
    data = json.loads(path.read_text(encoding="utf-8"))
    for p in data:
        if str(p.get("id")) == str(doc_id):
            return p
    raise SystemExit(f"Document ID {doc_id} listed in index but not found in {path}")

def markdown(meta, text):
    lines = [
        f"# {meta.get('document_title', '')}",
        "",
        f"- ID: {meta.get('document_post_id', '')}",
        f"- Date: {meta.get('document_date', '')}",
        f"- Process: {meta.get('primary_process', '')}",
        f"- Collection: {meta.get('primary_collection', '')}",
        f"- Categories: {meta.get('category_names', '')}",
        f"- Tags: {meta.get('tag_names', '')}",
        f"- URL: {meta.get('document_url', '')}",
        "",
        "---",
        "",
        text,
        "",
    ]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser(description="Show a local ShowTrials document by WordPress post ID.")
    p.add_argument("--id", required=True, help="WordPress post/document ID")
    p.add_argument("--text", action="store_true", help="Print clean text only")
    p.add_argument("--html", action="store_true", help="Print raw content.rendered HTML")
    p.add_argument("--markdown", action="store_true", help="Print markdown with metadata")
    p.add_argument("--save-text", help="Save clean text to file")
    p.add_argument("--save-html", help="Save raw HTML to file")
    p.add_argument("--save-markdown", help="Save markdown to file")
    args = p.parse_args()

    index = load_tsv(INDEX, "document_post_id")
    catalog = load_tsv(CATALOG, "document_post_id")

    post = load_post(args.id, index)
    meta = catalog.get(str(args.id), {})
    raw_html = post.get("content", {}).get("rendered", "") or ""
    text = clean_html(raw_html)
    md = markdown(meta, text)

    if args.save_text:
        Path(args.save_text).write_text(text + "\n", encoding="utf-8")
    if args.save_html:
        Path(args.save_html).write_text(raw_html + "\n", encoding="utf-8")
    if args.save_markdown:
        Path(args.save_markdown).write_text(md, encoding="utf-8")

    if args.html:
        print(raw_html)
        return

    if args.text:
        print(text)
        return

    if args.markdown:
        print(md)
        return

    print(f"ID: {meta.get('document_post_id', args.id)}")
    print(f"DATE: {meta.get('document_date', '')}")
    print(f"WORDS: {meta.get('content_words', '')}")
    print(f"TITLE: {meta.get('document_title', '')}")
    print(f"PROCESS: {meta.get('primary_process', '')}")
    print(f"COLLECTION: {meta.get('primary_collection', '')}")
    print(f"CATEGORIES: {meta.get('category_names', '')}")
    print(f"TAGS: {meta.get('tag_names', '')}")
    print(f"URL: {meta.get('document_url', '')}")
    print()
    print(text[:4000])
    if len(text) > 4000:
        print()
        print(f"[TRUNCATED PREVIEW: {len(text)} characters total]")

if __name__ == "__main__":
    main()
