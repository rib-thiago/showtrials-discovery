#!/usr/bin/env python3
import argparse, csv, json, re, html
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

def safe_slug(s):
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s or "")
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:80] or "document"

def load_tsv(path, key):
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return {str(r[key]): r for r in csv.DictReader(f, delimiter="\t")}

def markdown(meta, text):
    return "\n".join([
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
    ])

def main():
    p = argparse.ArgumentParser(description="Export local ShowTrials documents to text/markdown.")
    p.add_argument("--out-dir", default=str(BASE / "export-texts"))
    p.add_argument("--format", choices=["txt", "md"], default="txt")
    p.add_argument("--limit", type=int)
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index = load_tsv(INDEX, "document_post_id")
    catalog = load_tsv(CATALOG, "document_post_id")

    exported = 0
    skipped = 0
    missing = 0

    for doc_id, idx in index.items():
        if args.limit and exported >= args.limit:
            break

        meta = catalog.get(doc_id, {})
        slug = safe_slug(meta.get("slug") or idx.get("slug") or doc_id)
        out = out_dir / f"{doc_id}_{slug}.{args.format}"

        if out.exists() and not args.overwrite:
            skipped += 1
            continue

        data = json.loads(Path(idx["json_file"]).read_text(encoding="utf-8"))
        post = next((p for p in data if str(p.get("id")) == doc_id), None)
        if not post:
            missing += 1
            continue

        raw_html = post.get("content", {}).get("rendered", "") or ""
        text = clean_html(raw_html)
        content = markdown(meta, text) if args.format == "md" else text + "\n"

        out.write_text(content, encoding="utf-8")
        exported += 1

    print(f"Exported: {exported}")
    print(f"Skipped existing: {skipped}")
    print(f"Missing: {missing}")
    print(f"Output dir: {out_dir}")

if __name__ == "__main__":
    main()
