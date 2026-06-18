#!/usr/bin/env bash
set -u

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2; }
fail() { log "ERROR: $*"; exit 1; }

ROOT="/srv/projects/showtrials-discovery"
SRC="$ROOT/data/t-translation-assets/precursor_perpetrator2004_links.tsv"
OUT_DIR="$ROOT/data/perpetrator2004/manifests"
OUT="$OUT_DIR/perpetrator2004_full_ingestion_manifest.tsv"
TS="$(date '+%Y%m%d-%H%M%S')"

[ -f "$SRC" ] || fail "Fonte não encontrada: $SRC"
mkdir -p "$OUT_DIR"

if [ -f "$OUT" ]; then
  BKP="$OUT.corrupt_backup_$TS"
  log "Backing up existing manifest: $BKP"
  cp -a "$OUT" "$BKP" || fail "Falha ao criar backup"
fi

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

log "Building manifest from: $SRC"

python3 - "$SRC" "$TMP" <<'PY'
import csv
import posixpath
import re
import sys
from urllib.parse import urlparse, unquote

src, out = sys.argv[1], sys.argv[2]

BASE = "http://perpetrator2004.narod.ru/"
INTERNAL_DOMAIN = "perpetrator2004.narod.ru"
TARGET_ROOT = "data/perpetrator2004/raw/mirror"

def clean_cell(value: str) -> str:
    return (value or "").replace("\r", "").strip()

def normalize_href(href: str) -> str:
    href = clean_cell(href)
    href = href.replace("\\", "/")
    return href

def is_yes(value: str) -> bool:
    return clean_cell(value).lower() == "yes"

def safe_internal_path(href: str, resolved_url: str) -> str:
    href = normalize_href(href)

    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        path = parsed.path.lstrip("/")
    else:
        path = href.lstrip("/")

    path = unquote(path)
    path = path.replace("\\", "/")
    path = re.sub(r"/+", "/", path)
    path = posixpath.normpath(path)

    if path in ("", "."):
        path = "index.html"

    if path.startswith("../") or "/../" in path or path == "..":
        raise ValueError(f"unsafe path: {href!r}")

    return path

def external_target_path(resolved_url: str, idx: int) -> str:
    parsed = urlparse(clean_cell(resolved_url))
    host = parsed.netloc.replace(":", "_") or "external"
    path = parsed.path.strip("/")

    if not path:
        path = "index.html"
    elif path.endswith("/"):
        path = path + "index.html"

    path = unquote(path).replace("\\", "/")
    path = re.sub(r"/+", "/", path)
    path = posixpath.normpath(path)

    if path in ("", "."):
        path = "index.html"

    if path.startswith("../") or "/../" in path or path == "..":
        path = f"external_{idx:04d}.html"

    return posixpath.join("external", host, path)

with open(src, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")
    required = {"href", "resolved_url", "label", "is_html", "is_external"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise SystemExit(f"Missing columns in source TSV: {sorted(missing)}")

    rows = []
    seen = set()

    for idx, row in enumerate(reader, start=1):
        href = normalize_href(row.get("href", ""))
        resolved_url = clean_cell(row.get("resolved_url", ""))
        label = clean_cell(row.get("label", ""))
        is_html = clean_cell(row.get("is_html", ""))
        is_external = clean_cell(row.get("is_external", ""))

        if not href and not resolved_url:
            continue

        parsed = urlparse(resolved_url or href)
        domain = parsed.netloc.lower()

        # Classify by resolved URL domain, not inherited flags.
        # Any resource under perpetrator2004.narod.ru is internal,
        # including non-HTML assets such as .doc, .gif, .rar, etc.
        if domain == INTERNAL_DOMAIN or (not domain and href):
            is_external = "no"
            source_class = "internal"
        else:
            is_external = "yes"
            source_class = "external"

        if source_class == "external":
            rel_target = external_target_path(resolved_url or href, idx)
        else:
            rel_target = safe_internal_path(href, resolved_url)

        target_path = posixpath.join(TARGET_ROOT, rel_target)

        item_id = f"P2004-{idx:04d}"

        key = (href, resolved_url, target_path)
        if key in seen:
            continue
        seen.add(key)

        rows.append({
            "item_id": item_id,
            "href": href,
            "resolved_url": resolved_url,
            "label": label,
            "is_html": is_html,
            "is_external": is_external,
            "source_class": source_class,
            "target_path": target_path,
        })

with open(out, "w", encoding="utf-8", newline="") as f:
    fields = [
        "item_id",
        "href",
        "resolved_url",
        "label",
        "is_html",
        "is_external",
        "source_class",
        "target_path",
    ]
    writer = csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print(f"rows={len(rows)}")
PY

mv "$TMP" "$OUT" || fail "Falha ao instalar manifest"
log "Manifest written: $OUT"

printf 'manifest=%s\n' "$OUT"
printf 'rows='
tail -n +2 "$OUT" | wc -l
