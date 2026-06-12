#!/usr/bin/env python3
import csv, json, re, html
import sys
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PAGE_LINKS,
    PAGE_LINKS_REPORT,
    PAGES_PAGE_1_JSON,
    SHOWTRIALS_HOST,
    SHOWTRIALS_HTTP,
    SHOWTRIALS_HTTPS,
    ensure_parent,
)

PAGES = PAGES_PAGE_1_JSON
OUT_TSV = PAGE_LINKS
OUT_REPORT = PAGE_LINKS_REPORT

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def norm_url(url):
    url, _frag = urldefrag(url)
    url = url.strip()
    if url.startswith(SHOWTRIALS_HTTPS + "/"):
        url = SHOWTRIALS_HTTP + url[len(SHOWTRIALS_HTTPS):]
    if url.startswith(SHOWTRIALS_HTTP) and not url.endswith("/"):
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
        internal = parsed.netloc == SHOWTRIALS_HOST

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

with ensure_parent(OUT_TSV).open("w", encoding="utf-8", newline="") as f:
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

ensure_parent(OUT_REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_TSV)
print(OUT_REPORT)
