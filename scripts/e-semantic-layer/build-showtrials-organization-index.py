#!/usr/bin/env python3
import csv
import json
import re
import html
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path("/tmp/showtrials-discovery")
POSTS_DIR = BASE / "posts-json"
CATALOG = BASE / "showtrials_master_catalog.tsv"
PEOPLE_DOCS = BASE / "showtrials_literal_person_documents.tsv"

OUT_ORGS = BASE / "showtrials_organizations.tsv"
OUT_DOCS = BASE / "showtrials_organization_documents.tsv"
OUT_PERSON_ORGS = BASE / "showtrials_person_organization_pairs.tsv"
OUT_REPORT = BASE / "showtrials_organizations_report.txt"

PATTERNS = {
    "НКВД": r"\bНКВД\b",
    "ГУГБ": r"\bГУГБ\b",
    "ИНО ГУГБ": r"\bИНО\s+ГУГБ\b",
    "ОО ГУГБ НКВД": r"\bОО\s+ГУГБ\s+НКВД\b",
    "ЦК ВКП(б)": r"\bЦК\s+ВКП\s*\(?б\)?\b|\bЦК\s+ВКП\(б\)\b",
    "ВКП(б)": r"\bВКП\s*\(?б\)?\b|\bВКП\(б\)\b",
    "Политбюро": r"\bПолитбюро\b",
    "КПК": r"\bКПК\b",
    "КПК при ЦК ВКП(б)": r"\bКПК\s+при\s+ЦК\s+ВКП\s*\(?б\)?\b",
    "Коминтерн": r"\bКоминтерн[а-яё]*\b",
    "ИККИ": r"\bИККИ\b",
    "НКИД": r"\bНКИД\b",
    "Прокуратура СССР": r"\bПрокуратур[аы]\s+СССР\b",
    "Верховный Суд СССР": r"\bВерховн[а-яё]+\s+Суд[а-яё]*\s+СССР\b",
    "Верховный Совет СССР": r"\bВерховн[а-яё]+\s+Совет[а-яё]*\s+СССР\b",
    "ЦИК СССР": r"\bЦИК\s+СССР\b|\bЦИК\s+Союза\s+ССР\b",
    "Секретариат ЦИК СССР": r"\bСекретариат[а-яё]*\s+ЦИК\s+СССР\b|\bСекретариат[а-яё]*\s+ЦИК\s+Союза\s+ССР\b",
    "Совнарком": r"\bСовнарком[а-яё]*\b",
    "Правда": r"\bПравд[аы]\b|“ПРАВДА”|“Правда”",
    "Известия": r"\bИзвести[яй]\b|“ИЗВЕСТИЯ”|“Известия”",
    "The New York Times": r"\bTHE\s+NEW\s+YORK\s+TIMES\b|\bThe\s+New\s+York\s+Times\b",
    "United Press International": r"\bUNITED\s+PRESS\s+INTERNATIONAL\b|\bUnited\s+Press\s+International\b",
    "Лига Наций": r"\bЛиг[аеи]\s+Наций\b",
    "Народная Трудовая Демократическая партия России": r"\bНародн[а-яё]+\s+Трудов[а-яё]+\s+Демократическ[а-яё]+\s+парти[яи]\s+России\b",
    "Горьковский крайком ВКП(б)": r"\bГорьковск[а-яё]+\s+крайком[а-яё]*\s+ВКП\s*\(?б\)?\b",
    "УНКВД СССР по Горькраю": r"\bУНКВД\s+СССР\s+по\s+Горькраю\b",
}

ORG_KIND = {
    "НКВД": "security_police",
    "ГУГБ": "security_police",
    "ИНО ГУГБ": "security_police_department",
    "ОО ГУГБ НКВД": "security_police_department",
    "ЦК ВКП(б)": "party_body",
    "ВКП(б)": "party",
    "Политбюро": "party_body",
    "КПК": "party_control_body",
    "КПК при ЦК ВКП(б)": "party_control_body",
    "Коминтерн": "international_communist_body",
    "ИККИ": "international_communist_body",
    "НКИД": "state_body",
    "Прокуратура СССР": "prosecutorial_body",
    "Верховный Суд СССР": "judicial_body",
    "Верховный Совет СССР": "state_body",
    "ЦИК СССР": "state_body",
    "Секретариат ЦИК СССР": "state_body",
    "Совнарком": "state_body",
    "Правда": "newspaper",
    "Известия": "newspaper",
    "The New York Times": "newspaper",
    "United Press International": "news_agency",
    "Лига Наций": "international_body",
    "Народная Трудовая Демократическая партия России": "political_organization",
    "Горьковский крайком ВКП(б)": "party_body",
    "УНКВД СССР по Горькраю": "security_police_department",
}

def clean_html(s):
    s = s or ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def load_catalog():
    with CATALOG.open("r", encoding="utf-8", newline="") as f:
        return {r["document_post_id"]: r for r in csv.DictReader(f, delimiter="\t")}

def load_posts():
    for path in sorted(POSTS_DIR.glob("posts-page-*.json")):
        for p in json.loads(path.read_text(encoding="utf-8")):
            yield p

def load_people_by_doc():
    out = defaultdict(set)
    if not PEOPLE_DOCS.exists():
        return out
    with PEOPLE_DOCS.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["document_post_id"]].add(r["person"])
    return out

catalog = load_catalog()
people_by_doc = load_people_by_doc()

org_docs = []
org_counter = Counter()
org_words = Counter()
org_dates = defaultdict(list)
org_processes = defaultdict(set)
org_collections = defaultdict(set)
org_raw_hits = defaultdict(Counter)

for p in load_posts():
    doc_id = str(p.get("id"))
    meta = catalog.get(doc_id, {})
    title = clean_html(p.get("title", {}).get("rendered", ""))
    content = clean_html(p.get("content", {}).get("rendered", ""))
    searchable = title + "\n" + content
    words = int(meta.get("content_words") or 0)

    seen_in_doc = set()

    for canonical, pattern in PATTERNS.items():
        matches = re.findall(pattern, searchable, flags=re.I)
        if not matches:
            continue

        count = len(matches)
        raw_forms = []
        for m in matches:
            if isinstance(m, tuple):
                raw_forms.append(" ".join(x for x in m if x))
            else:
                raw_forms.append(m)

        org_docs.append({
            "organization": canonical,
            "organization_kind": ORG_KIND.get(canonical, "unknown"),
            "document_post_id": doc_id,
            "document_date": meta.get("document_date", ""),
            "document_title": meta.get("document_title", title),
            "primary_process": meta.get("primary_process", ""),
            "primary_collection": meta.get("primary_collection", ""),
            "category_names": meta.get("category_names", ""),
            "tag_names": meta.get("tag_names", ""),
            "hit_count": count,
            "raw_forms": " | ".join(sorted(set(raw_forms)))[:500],
            "content_words": meta.get("content_words", ""),
            "document_url": meta.get("document_url", ""),
        })

        if canonical not in seen_in_doc:
            org_counter[canonical] += 1
            org_words[canonical] += words
            org_dates[canonical].append(meta.get("document_date", ""))
            if meta.get("primary_process"):
                org_processes[canonical].add(meta.get("primary_process"))
            if meta.get("primary_collection"):
                org_collections[canonical].add(meta.get("primary_collection"))
            seen_in_doc.add(canonical)

        for rf in raw_forms:
            org_raw_hits[canonical][rf] += 1

with OUT_DOCS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "organization", "organization_kind", "document_post_id", "document_date",
        "document_title", "primary_process", "primary_collection",
        "category_names", "tag_names", "hit_count", "raw_forms",
        "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(org_docs, key=lambda r: (r["organization"], r["document_date"], r["document_post_id"])))

with OUT_ORGS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "organization", "organization_kind", "document_count", "total_words",
        "first_date", "last_date", "raw_forms", "processes", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for org, count in sorted(org_counter.items(), key=lambda x: (-x[1], x[0])):
        dates = sorted(x for x in org_dates[org] if x)
        w.writerow({
            "organization": org,
            "organization_kind": ORG_KIND.get(org, "unknown"),
            "document_count": count,
            "total_words": org_words[org],
            "first_date": dates[0] if dates else "",
            "last_date": dates[-1] if dates else "",
            "raw_forms": " | ".join(x for x, _ in org_raw_hits[org].most_common(20)),
            "processes": " | ".join(sorted(org_processes[org])),
            "collections": " | ".join(sorted(org_collections[org])),
        })

pair_counter = Counter()
pair_docs = defaultdict(set)

for r in org_docs:
    doc_id = r["document_post_id"]
    org = r["organization"]
    for person in people_by_doc.get(doc_id, []):
        pair_counter[(person, org)] += 1
        pair_docs[(person, org)].add(doc_id)

with OUT_PERSON_ORGS.open("w", encoding="utf-8", newline="") as f:
    fields = ["person", "organization", "document_count", "documents"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for (person, org), count in sorted(pair_counter.items(), key=lambda x: (-x[1], x[0])):
        w.writerow({
            "person": person,
            "organization": org,
            "document_count": len(pair_docs[(person, org)]),
            "documents": " | ".join(sorted(pair_docs[(person, org)])),
        })

report = []
report.append("ShowTrials organization index")
report.append("")
report.append(f"Organizations: {len(org_counter)}")
report.append(f"Organization-document rows: {len(org_docs)}")
report.append(f"Person-organization pairs: {len(pair_counter)}")
report.append("")
report.append("Top organizations:")
for org, count in sorted(org_counter.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{ORG_KIND.get(org, 'unknown')}\t{org}")
report.append("")
report.append("Outputs:")
report.append(str(OUT_ORGS))
report.append(str(OUT_DOCS))
report.append(str(OUT_PERSON_ORGS))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_ORGS)
print(OUT_DOCS)
print(OUT_PERSON_ORGS)
print(OUT_REPORT)
