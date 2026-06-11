#!/usr/bin/env python3
import csv, json, re, html
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse

BASE = Path("/tmp/showtrials-discovery")
PAGES = BASE / "pages-json/pages-page-1.json"
OUT_TSV = BASE / "showtrials_page_links.tsv"
OUT_REPORT = BASE / "showtrials_page_links_report.txt"

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def norm_url(url):
    url, _frag = urldefrag(url)
    url = url.strip()
    if url.startswith("https://showtrials.ru/"):
        url = "http://" + url[len("https://"):]
    if url.startswith("http://showtrials.ru") and not url.endswith("/"):
        parsed = urlparse(url)
        if "." not in Path(parsed.path).name:
            url += "/"
    return url

pages = json.loads(PAGES.read_text(encoding="utf-8"))

rows = []
for p in pages:
    source_id = p["id"]
    source_url = p.get("link", "")
    source_title = clean(p.get("title", {}).get("rendered", ""))
    content = p.get("content", {}).get("rendered", "")

    for idx, m in enumerate(re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', content, re.I | re.S), start=1):
        href = html.unescape(m.group(1))
        anchor = clean(m.group(2))
        abs_url = norm_url(urljoin(source_url, href))
        parsed = urlparse(abs_url)
        internal = parsed.netloc == "showtrials.ru"

        if not internal:
            kind = "external"
        elif any(x in parsed.path for x in ["/wp-content/", "/wp-json/", "/feed/", "/comments/"]):
            kind = "ignored_internal_asset_or_feed"
        elif parsed.query:
            kind = "internal_with_query"
        else:
            kind = "internal"

        rows.append({
            "source_page_id": source_id,
            "source_title": source_title,
            "source_url": source_url,
            "order_in_page": idx,
            "target_url": abs_url,
            "anchor_text": anchor,
            "link_kind": kind,
        })

with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["source_page_id","source_title","source_url","order_in_page","target_url","anchor_text","link_kind"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

internal = [r for r in rows if r["link_kind"] == "internal"]
report = [
    "ShowTrials page links diagnosis",
    "",
    f"Pages scanned: {len(pages)}",
    f"Links total: {len(rows)}",
    f"Internal clean links: {len(internal)}",
    f"Unique internal clean links: {len(set(r['target_url'] for r in internal))}",
    "",
    "Top source pages by internal links:",
]
counts = {}
for r in internal:
    counts[r["source_title"]] = counts.get(r["source_title"], 0) + 1
for title, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]:
    report.append(f"{count}\t{title}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
