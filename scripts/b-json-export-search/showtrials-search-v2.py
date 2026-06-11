#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from pathlib import Path

BASE = Path("/tmp/showtrials-discovery")

CATALOG = BASE / "showtrials_master_catalog.tsv"
CORPUS = BASE / "showtrials_search_corpus.tsv"
PERSON_DOCS = BASE / "showtrials_literal_person_documents.tsv"
ORG_DOCS = BASE / "showtrials_organization_documents.tsv"
FAMILY_DOCS = BASE / "showtrials_organization_family_document_matrix.tsv"
DOC_TYPES = BASE / "showtrials_document_types_v4.tsv"
ROLE_DOCS = BASE / "showtrials_role_documents_v2.tsv"

def field_limit():
    import csv as _csv
    max_int = sys.maxsize
    while True:
        try:
            _csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int / 10)

def load_tsv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def index_by_doc(rows, field):
    out = {}
    for r in rows:
        out[r["document_post_id"]] = r.get(field, "")
    return out

def set_by_doc(rows, value_field):
    out = {}
    for r in rows:
        out.setdefault(r["document_post_id"], set()).add(r[value_field])
    return out

def norm(s):
    return (s or "").casefold()

def contains(value, needle):
    return norm(needle) in norm(value)

def split_pipe(s):
    return [x.strip() for x in (s or "").split("|") if x.strip()]

def load_documents():
    catalog = {r["document_post_id"]: r for r in load_tsv(CATALOG)}

    corpus_rows = load_tsv(CORPUS)
    corpus = {r["document_post_id"]: r for r in corpus_rows}

    people = set_by_doc(load_tsv(PERSON_DOCS), "person")
    orgs = set_by_doc(load_tsv(ORG_DOCS), "organization")

    families = {}
    for r in load_tsv(FAMILY_DOCS):
        families[r["document_post_id"]] = set(split_pipe(r.get("organization_families", "")))

    doctypes = index_by_doc(load_tsv(DOC_TYPES), "document_type")

    roles = {}
    role_classes = {}
    for r in load_tsv(ROLE_DOCS):
        doc_id = r["document_post_id"]
        roles.setdefault(doc_id, set()).add(r["role"])
        role_classes.setdefault(doc_id, set()).add(r["role_class"])

    docs = []
    for doc_id, meta in catalog.items():
        c = corpus.get(doc_id, {})
        text = c.get("search_text") or c.get("content_text") or c.get("text") or ""

        docs.append({
            "document_post_id": doc_id,
            "document_date": meta.get("document_date", ""),
            "document_title": meta.get("document_title", ""),
            "document_url": meta.get("document_url", ""),
            "primary_process": meta.get("primary_process", ""),
            "primary_collection": meta.get("primary_collection", ""),
            "document_type": doctypes.get(doc_id, ""),
            "people": people.get(doc_id, set()),
            "organizations": orgs.get(doc_id, set()),
            "families": families.get(doc_id, set()),
            "roles": roles.get(doc_id, set()),
            "role_classes": role_classes.get(doc_id, set()),
            "content_words": meta.get("content_words", ""),
            "text": text,
        })

    return docs

def match_any_set(values, needles):
    if not needles:
        return True
    return any(any(contains(v, n) for v in values) for n in needles)

def match_any_text(value, needles):
    if not needles:
        return True
    return any(contains(value, n) for n in needles)

def score_doc(doc, terms):
    if not terms:
        return 0
    text = norm(" ".join([
        doc["document_title"],
        doc["primary_process"],
        doc["primary_collection"],
        doc["document_type"],
        " ".join(doc["people"]),
        " ".join(doc["organizations"]),
        " ".join(doc["families"]),
        " ".join(doc["roles"]),
        doc["text"],
    ]))
    return sum(text.count(norm(t)) for t in terms)

def snippet(doc, terms, width=180):
    text = re.sub(r"\s+", " ", doc["text"] or doc["document_title"]).strip()
    if not text:
        return ""
    lower = norm(text)
    positions = [lower.find(norm(t)) for t in terms if norm(t) in lower]
    pos = min([p for p in positions if p >= 0], default=0)
    start = max(0, pos - 50)
    return text[start:start+width]

def parse_args():
    p = argparse.ArgumentParser(
        description="Search ShowTrials corpus with semantic TSV filters."
    )
    p.add_argument("terms", nargs="*", help="Full-text terms. Default: no text filter.")
    p.add_argument("--person", action="append", default=[])
    p.add_argument("--organization", action="append", default=[])
    p.add_argument("--family", action="append", default=[])
    p.add_argument("--process", action="append", default=[])
    p.add_argument("--collection", action="append", default=[])
    p.add_argument("--doctype", action="append", default=[])
    p.add_argument("--role", action="append", default=[])
    p.add_argument("--role-class", action="append", default=[])
    p.add_argument("--all", action="store_true", help="Require all text terms instead of any.")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--format", choices=["brief", "detail", "tsv"], default="brief")
    return p.parse_args()

def main():
    field_limit()
    args = parse_args()
    docs = load_documents()

    results = []

    for doc in docs:
        if args.terms:
            hay = norm(" ".join([
                doc["document_title"],
                doc["primary_process"],
                doc["primary_collection"],
                doc["document_type"],
                doc["text"],
            ]))
            if args.all:
                if not all(norm(t) in hay for t in args.terms):
                    continue
            else:
                if not any(norm(t) in hay for t in args.terms):
                    continue

        if not match_any_set(doc["people"], args.person):
            continue
        if not match_any_set(doc["organizations"], args.organization):
            continue
        if not match_any_set(doc["families"], args.family):
            continue
        if not match_any_text(doc["primary_process"], args.process):
            continue
        if not match_any_text(doc["primary_collection"], args.collection):
            continue
        if not match_any_text(doc["document_type"], args.doctype):
            continue
        if not match_any_set(doc["roles"], args.role):
            continue
        if not match_any_set(doc["role_classes"], args.role_class):
            continue

        doc["_score"] = score_doc(doc, args.terms)
        results.append(doc)

    results.sort(key=lambda d: (-d["_score"], d["document_date"], d["document_post_id"]))

    if args.limit and args.limit > 0:
        results = results[:args.limit]

    if args.format == "tsv":
        fields = [
            "document_post_id", "document_date", "document_title",
            "primary_process", "primary_collection", "document_type",
            "people", "organizations", "families", "roles",
            "content_words", "document_url", "score"
        ]
        w = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for d in results:
            w.writerow({
                "document_post_id": d["document_post_id"],
                "document_date": d["document_date"],
                "document_title": d["document_title"],
                "primary_process": d["primary_process"],
                "primary_collection": d["primary_collection"],
                "document_type": d["document_type"],
                "people": " | ".join(sorted(d["people"])),
                "organizations": " | ".join(sorted(d["organizations"])),
                "families": " | ".join(sorted(d["families"])),
                "roles": " | ".join(sorted(d["roles"])),
                "content_words": d["content_words"],
                "document_url": d["document_url"],
                "score": d["_score"],
            })
        return

    print(f"Results: {len(results)}")
    for d in results:
        print("=" * 80)
        print(f"[{d['document_post_id']}] {d['document_title']}")
        print(f"Date: {d['document_date']}")
        print(f"Process: {d['primary_process']}")
        print(f"Collection: {d['primary_collection']}")
        print(f"Type: {d['document_type']}")
        print(f"Families: {' | '.join(sorted(d['families']))}")
        print(f"Organizations: {' | '.join(sorted(d['organizations']))}")
        print(f"People: {' | '.join(sorted(d['people']))}")
        print(f"URL: {d['document_url']}")
        if args.format == "detail":
            print()
            print(snippet(d, args.terms))

if __name__ == "__main__":
    main()
