#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "local" / "process-dossiers"

MIA_DOCS = ROOT / "data/t-translation-assets/translation_html_documents.tsv"

SHOWTRIALS_CORPUS = ROOT / "local/showtrials_search_corpus.tsv"

PROCESS_LENINGRAD = "ПРОЦЕСС “ЛЕНИНГРАДСКОГО ЦЕНТРА”"
PROCESS_MOSCOW_CENTER = "ПРОЦЕСС “МОСКОВСКОГО ЦЕНТРА”"
COLLECTION_HOD = "ХОД ПРОЦЕССА"

def read_tsv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t")

def read_text_file(path_str: str) -> str:
    p = Path(path_str)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace").strip()

def normalize_sort_title(title: str):
    upper = title.upper()

    if "ОБВИНИТЕЛЬ" in upper:
        return (-20, 0, title)
    if "СООБЩЕНИЕ" in upper:
        return (-10, 0, title)

    m = re.search(r"(\d{1,2})\s+(ЯНВАРЯ|ДЕКАБРЯ|АВГУСТА)", title, re.I)
    day = int(m.group(1)) if m else 999

    session_rank = 0
    if "УТРЕН" in upper:
        session_rank = 1
    elif "ДНЕВ" in upper:
        session_rank = 2
    elif "ВЕЧЕР" in upper:
        session_rank = 3
    elif "ПРИГОВОР" in upper:
        session_rank = 99

    return (day, session_rank, title)

MIA_1936_ORDER = {
    "19/indictment.htm": 1,
    "19/terrorist-centre.htm": 2,
    "19/united-centre.htm": 3,
    "19/organised-centre.htm": 4,
    "19/mrachkovsky.htm": 5,
    "19/evdokimov.htm": 6,
    "19/dreitzer.htm": 7,
    "19/reingold.htm": 8,
    "19/bakayev.htm": 9,
    "19/pickel.htm": 10,
    "20/kamenev.htm": 11,
    "20/yakovlev.htm": 12,
    "20/zinoviev.htm": 13,
    "20/safonova.htm": 14,
    "20/smirnov.htm": 15,
    "20/olberg.htm": 16,
    "20/berman-yurin.htm": 17,
    "21/holtzman.htm": 18,
    "21/nlurye.htm": 19,
    "21/mlurye.htm": 20,
    "21/ter-vaganyan.htm": 21,
    "21/kruglyansky.htm": 22,
    "21/statement.htm": 23,
    "22/prosecution.htm": 24,
    "22/contemptible-terrorists.htm": 25,
    "22/sworn-enemies.htm": 26,
    "22/double-dealing.htm": 27,
    "22/counter-revolutionary.htm": 28,
    "22/killed-kirov.htm": 29,
    "22/torn-masks.htm": 30,
    "22/mad-dogs.htm": 31,
    "22/evening.htm": 32,
    "23/last-pleas.htm": 33,
    "23/last-pleas-td.htm": 34,
    "24/verdict.htm": 35,
}

def sort_href(row):
    href = row.get("href", "")
    return (MIA_1936_ORDER.get(href, 999), href)

def write_header(w, title: str, source: str, count: int):
    w.write(f"# {title}\n\n")
    w.write(f"Source: {source}\n")
    w.write(f"Documents: {count}\n\n")

def build_mia_1936() -> tuple[Path, int]:
    rows = [
        r for r in read_tsv(MIA_DOCS)
        if r.get("source_id") == "mia_1936_trotskyite_zinovievite_index"
    ]
    rows.sort(key=sort_href)

    out = OUT / "1936_moscow_trial_mia_en_combined.txt"
    with out.open("w", encoding="utf-8") as w:
        write_header(w, "1936 Moscow Trial — MIA English Combined Proceedings", str(MIA_DOCS), len(rows))
        for r in rows:
            text = read_text_file(r["text_path"])
            w.write("\n\n" + "=" * 88 + "\n")
            w.write(f"TITLE: {r.get('label') or r.get('title') or r.get('href')}\n")
            w.write(f"URL: {r.get('url','')}\n")
            w.write(f"HREF: {r.get('href','')}\n")
            w.write("=" * 88 + "\n\n")
            w.write(text)
            w.write("\n")
    return out, len(rows)

def select_showtrials_exact(process_name: str):
    rows = []
    for r in read_tsv(SHOWTRIALS_CORPUS):
        if (
            r.get("primary_process") == process_name
            and r.get("primary_collection") == COLLECTION_HOD
        ):
            rows.append(r)
    rows.sort(key=lambda r: normalize_sort_title(r.get("document_title", "")))
    return rows

def build_showtrials_exact(out_name: str, title: str, process_name: str) -> tuple[Path, int]:
    rows = select_showtrials_exact(process_name)
    out = OUT / out_name

    with out.open("w", encoding="utf-8") as w:
        write_header(w, title, str(SHOWTRIALS_CORPUS), len(rows))
        for r in rows:
            text = read_text_file(r.get("text_file", ""))
            w.write("\n\n" + "=" * 88 + "\n")
            w.write(f"ID: {r.get('document_post_id','')}\n")
            w.write(f"DATE: {r.get('document_date','')}\n")
            w.write(f"PROCESS: {r.get('primary_process','')}\n")
            w.write(f"COLLECTION: {r.get('primary_collection','')}\n")
            w.write(f"TITLE: {r.get('document_title','')}\n")
            w.write(f"URL: {r.get('document_url','')}\n")
            w.write(f"TEXT_FILE: {r.get('text_file','')}\n")
            w.write(f"CONTENT_WORDS: {r.get('content_words','')}\n")
            w.write("=" * 88 + "\n\n")
            w.write(text)
            w.write("\n")
    return out, len(rows)

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    outputs = [
        build_mia_1936(),
        build_showtrials_exact(
            "1934_leningrad_center_hod_processa_ru_combined.txt",
            "1934 Leningrad Center Trial — ХОД ПРОЦЕССА Combined",
            PROCESS_LENINGRAD,
        ),
        build_showtrials_exact(
            "1935_moscow_center_hod_processa_ru_combined.txt",
            "1935 Moscow Center Trial — ХОД ПРОЦЕССА Combined",
            PROCESS_MOSCOW_CENTER,
        ),
    ]

    for path, n in outputs:
        print(f"{path}\t{n}\t{path.stat().st_size}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
