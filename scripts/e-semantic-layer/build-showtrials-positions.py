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
ORG_DOCS = BASE / "showtrials_organization_documents.tsv"
FAMILY_MATRIX = BASE / "showtrials_organization_family_document_matrix.tsv"

OUT_POSITIONS = BASE / "showtrials_positions.tsv"
OUT_DOCS = BASE / "showtrials_position_documents.tsv"
OUT_PERSON_POSITIONS = BASE / "showtrials_person_position_pairs.tsv"
OUT_POSITION_ORGS = BASE / "showtrials_position_organization_pairs.tsv"
OUT_REPORT = BASE / "showtrials_positions_report.txt"

PATTERNS = {
    "нарком": r"\bнарком[а-яё]*\b",
    "наркомвнудел": r"\bнаркомвнудел[а-яё]*\b",
    "следователь": r"\bследовател[ьяеюями]*\b",
    "прокурор": r"\bпрокурор[а-яё]*\b",
    "председатель": r"\bпредседател[ьяеюями]*\b",
    "секретарь": r"\bсекретар[ьяеюями]*\b",
    "член": r"\bчлен[а-яё]*\b",
    "кандидат": r"\bкандидат[а-яё]*\b",
    "начальник": r"\bначальник[а-яё]*\b",
    "заместитель": r"\bзаместител[ьяеюями]*\b|\bзам\.\s*начальник[а-яё]*\b",
    "комиссар": r"\bкомиссар[а-яё]*\b",
    "сотрудник": r"\bсотрудник[а-яё]*\b",
    "агент": r"\bагент[а-яё]*\b",
    "обвиняемый": r"\bобвиняем[а-яё]*\b",
    "подсудимый": r"\bподсудим[а-яё]*\b",
    "свидетель": r"\bсвидетел[ьяеюями]*\b",
    "секретарь_суда": r"\bсекретар[ьяеюями]*\s+суд[а-яё]*\b",
    "судья": r"\bсудь[яеиюями]*\b",
    "адвокат": r"\bадвокат[а-яё]*\b|\bзащитник[а-яё]*\b",
    "редактор": r"\bредактор[а-яё]*\b",
    "корреспондент": r"\bкорреспондент[а-яё]*\b",
    "посол": r"\bпосол[а-яё]*\b|\bпосольств[а-яё]*\b",
    "полпред": r"\bполпред[а-яё]*\b",
    "представитель": r"\bпредставител[ьяеюями]*\b",
    "директор": r"\bдиректор[а-яё]*\b",
    "руководитель": r"\bруководител[ьяеюями]*\b",
    "троцкист": r"\bтроцкист[а-яё]*\b",
    "правый": r"\bправ[ыо][а-яё]*\b",
    "вредитель": r"\bвредител[ьяеюями]*\b",
}

POSITION_FAMILY = {
    "нарком": "state_security_role",
    "наркомвнудел": "state_security_role",
    "следователь": "security_investigation_role",
    "начальник": "administrative_command_role",
    "заместитель": "administrative_command_role",
    "комиссар": "state_or_party_role",
    "сотрудник": "institution_staff_role",
    "агент": "security_or_intelligence_role",

    "прокурор": "judicial_role",
    "судья": "judicial_role",
    "секретарь_суда": "judicial_role",
    "адвокат": "legal_defense_role",

    "председатель": "leadership_role",
    "секретарь": "party_or_administrative_role",
    "член": "membership_role",
    "кандидат": "membership_role",

    "обвиняемый": "trial_role",
    "подсудимый": "trial_role",
    "свидетель": "trial_role",

    "редактор": "press_role",
    "корреспондент": "press_role",

    "посол": "diplomatic_role",
    "полпред": "diplomatic_role",
    "представитель": "representative_role",

    "директор": "administrative_command_role",
    "руководитель": "leadership_role",

    "троцкист": "political_label",
    "правый": "political_label",
    "вредитель": "accusatory_label",
}

def clean_html(s):
    s = s or ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def load_tsv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def load_posts():
    for path in sorted(POSTS_DIR.glob("posts-page-*.json")):
        for p in json.loads(path.read_text(encoding="utf-8")):
            yield p

catalog = {r["document_post_id"]: r for r in load_tsv(CATALOG)}

people_by_doc = defaultdict(set)
for r in load_tsv(PEOPLE_DOCS):
    people_by_doc[r["document_post_id"]].add(r["person"])

orgs_by_doc = defaultdict(set)
for r in load_tsv(ORG_DOCS):
    orgs_by_doc[r["document_post_id"]].add(r["organization"])

families_by_doc = {}
for r in load_tsv(FAMILY_MATRIX):
    families_by_doc[r["document_post_id"]] = r.get("organization_families", "")

position_docs = []
position_counter = Counter()
position_words = Counter()
position_raw = defaultdict(Counter)
position_processes = defaultdict(set)
position_collections = defaultdict(set)
position_dates = defaultdict(list)

for p in load_posts():
    doc_id = str(p.get("id"))
    meta = catalog.get(doc_id, {})
    title = clean_html(p.get("title", {}).get("rendered", ""))
    content = clean_html(p.get("content", {}).get("rendered", ""))
    text = title + "\n" + content
    words = int(meta.get("content_words") or 0)

    seen = set()

    for pos, pattern in PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.I)
        if not matches:
            continue

        raw_forms = []
        for m in matches:
            if isinstance(m, tuple):
                raw_forms.append(" ".join(x for x in m if x))
            else:
                raw_forms.append(m)

        position_docs.append({
            "position": pos,
            "position_family": POSITION_FAMILY.get(pos, "unknown"),
            "document_post_id": doc_id,
            "document_date": meta.get("document_date", ""),
            "document_title": meta.get("document_title", title),
            "primary_process": meta.get("primary_process", ""),
            "primary_collection": meta.get("primary_collection", ""),
            "category_names": meta.get("category_names", ""),
            "tag_names": meta.get("tag_names", ""),
            "organization_families": families_by_doc.get(doc_id, ""),
            "hit_count": len(matches),
            "raw_forms": " | ".join(sorted(set(raw_forms)))[:500],
            "content_words": meta.get("content_words", ""),
            "document_url": meta.get("document_url", ""),
        })

        if pos not in seen:
            position_counter[pos] += 1
            position_words[pos] += words
            position_dates[pos].append(meta.get("document_date", ""))
            if meta.get("primary_process"):
                position_processes[pos].add(meta["primary_process"])
            if meta.get("primary_collection"):
                position_collections[pos].add(meta["primary_collection"])
            seen.add(pos)

        for rf in raw_forms:
            position_raw[pos][rf] += 1

with OUT_DOCS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "position", "position_family", "document_post_id", "document_date",
        "document_title", "primary_process", "primary_collection",
        "category_names", "tag_names", "organization_families",
        "hit_count", "raw_forms", "content_words", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(position_docs, key=lambda r: (r["position"], r["document_date"], r["document_post_id"])))

with OUT_POSITIONS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "position", "position_family", "document_count", "total_words",
        "first_date", "last_date", "raw_forms", "processes", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for pos, count in sorted(position_counter.items(), key=lambda x: (-x[1], x[0])):
        dates = sorted(x for x in position_dates[pos] if x)
        w.writerow({
            "position": pos,
            "position_family": POSITION_FAMILY.get(pos, "unknown"),
            "document_count": count,
            "total_words": position_words[pos],
            "first_date": dates[0] if dates else "",
            "last_date": dates[-1] if dates else "",
            "raw_forms": " | ".join(x for x, _ in position_raw[pos].most_common(20)),
            "processes": " | ".join(sorted(position_processes[pos])),
            "collections": " | ".join(sorted(position_collections[pos])),
        })

person_position = Counter()
person_position_docs = defaultdict(set)

position_org = Counter()
position_org_docs = defaultdict(set)

for r in position_docs:
    doc_id = r["document_post_id"]
    pos = r["position"]

    for person in people_by_doc.get(doc_id, []):
        person_position[(person, pos)] += 1
        person_position_docs[(person, pos)].add(doc_id)

    for org in orgs_by_doc.get(doc_id, []):
        position_org[(pos, org)] += 1
        position_org_docs[(pos, org)].add(doc_id)

with OUT_PERSON_POSITIONS.open("w", encoding="utf-8", newline="") as f:
    fields = ["person", "position", "document_count", "documents"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for (person, pos), count in sorted(person_position.items(), key=lambda x: (-len(person_position_docs[x[0]]), x[0])):
        w.writerow({
            "person": person,
            "position": pos,
            "document_count": len(person_position_docs[(person, pos)]),
            "documents": " | ".join(sorted(person_position_docs[(person, pos)])),
        })

with OUT_POSITION_ORGS.open("w", encoding="utf-8", newline="") as f:
    fields = ["position", "organization", "document_count", "documents"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for (pos, org), count in sorted(position_org.items(), key=lambda x: (-len(position_org_docs[x[0]]), x[0])):
        w.writerow({
            "position": pos,
            "organization": org,
            "document_count": len(position_org_docs[(pos, org)]),
            "documents": " | ".join(sorted(position_org_docs[(pos, org)])),
        })

report = []
report.append("ShowTrials positions index")
report.append("")
report.append(f"Positions: {len(position_counter)}")
report.append(f"Position-document rows: {len(position_docs)}")
report.append(f"Person-position pairs: {len(person_position)}")
report.append(f"Position-organization pairs: {len(position_org)}")
report.append("")
report.append("Top positions:")
for pos, count in sorted(position_counter.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{count}\t{POSITION_FAMILY.get(pos, 'unknown')}\t{pos}")
report.append("")
report.append("Outputs:")
report.append(str(OUT_POSITIONS))
report.append(str(OUT_DOCS))
report.append(str(OUT_PERSON_POSITIONS))
report.append(str(OUT_POSITION_ORGS))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_POSITIONS)
print(OUT_DOCS)
print(OUT_PERSON_POSITIONS)
print(OUT_POSITION_ORGS)
print(OUT_REPORT)
