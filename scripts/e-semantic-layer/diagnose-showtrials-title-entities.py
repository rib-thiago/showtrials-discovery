#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/tmp/showtrials-discovery")
CATALOG = BASE / "showtrials_master_catalog.tsv"

OUT_DOC_ENTITIES = BASE / "showtrials_title_document_entities.tsv"
OUT_ENTITIES = BASE / "showtrials_title_entities.tsv"
OUT_PAIRS = BASE / "showtrials_title_entity_pairs.tsv"
OUT_REPORT = BASE / "showtrials_title_entities_report.txt"

# Padrões simples para títulos russos:
# - iniciais + sobrenome: К.Б. Радека
# - sobrenome + iniciais: Радека К.Б.
# - sobrenomes após preposições ou fórmulas documentais comuns
INITIALS_SURNAME = re.compile(
    r"\b([А-ЯЁ]\.[А-ЯЁ]\.\s*[А-ЯЁ][а-яё-]+)\b"
)

SURNAME_INITIALS = re.compile(
    r"\b([А-ЯЁ][а-яё-]+(?:а|у|ым|ом|ой|ого|ему|е)?\s+[А-ЯЁ]\.[А-ЯЁ]\.)\b"
)

# Captura nomes após palavras documentais frequentes.
AFTER_CUES = re.compile(
    r"(?:"
    r"письмо|заявление|показания|допрос(?:а)?|протокол допроса|"
    r"спецсообщение|сообщение|записка|справка|стенограмма|"
    r"очной ставки между|между|о|об|от|к|в"
    r")\s+([А-ЯЁ][а-яё-]+(?:а|у|ым|ом|ой|ого|ему|е)?)",
    re.I
)

# Sobrenomes muito conhecidos no corpus, úteis para normalizar busca inicial.
KNOWN = [
    "Сталин", "Ежов", "Ягода", "Бухарин", "Рыков", "Радек", "Пятаков",
    "Зиновьев", "Каменев", "Троцкий", "Сокольников", "Крестинский",
    "Раковский", "Смирнов", "Мрачковский", "Ольберг", "Седов",
    "Вышинский", "Молотов", "Киров", "Берман-Юрин", "Томский",
    "Агранов", "Фриновский", "Уборевич", "Тухачевский", "Ромм",
    "Сосновский", "Белобородов", "Радин", "Астров", "Членов",
    "Гавен", "Шемелев", "Дмитриев", "Пригожин", "Тивель",
]

KNOWN_RE = re.compile(r"\b(" + "|".join(re.escape(x) for x in KNOWN) + r")\w*\b", re.I)

STOP = {
    "Письмо", "Заявление", "Показания", "Протокол", "Допрос",
    "Спецсообщение", "Сообщение", "Записка", "Справка", "Стенограмма",
    "Проект", "Обвинительное", "Заключение", "Заседание",
    "Утреннее", "Вечернее", "Дневное", "Материалы",
    "Народному", "Комиссару", "Внутренних", "Дел", "СССР",
    "ЦК", "ВКП", "НКВД", "ОГПУ", "ГУГБ",
}

def split_pipe(v):
    return [x.strip() for x in (v or "").split(" | ") if x.strip()]

def normalize_entity(e):
    e = re.sub(r"\s+", " ", e or "").strip(" .,:;()[]")
    return e

def canonical_known(e):
    low = e.casefold()
    for k in KNOWN:
        if low.startswith(k.casefold()) or k.casefold() in low:
            return k
    return e

def extract_entities(title):
    entities = []

    for m in INITIALS_SURNAME.findall(title):
        entities.append(m)

    for m in SURNAME_INITIALS.findall(title):
        entities.append(m)

    for m in AFTER_CUES.findall(title):
        m = normalize_entity(m)
        if m and m not in STOP and len(m) > 2:
            entities.append(m)

    for m in KNOWN_RE.findall(title):
        entities.append(canonical_known(m))

    cleaned = []
    seen = set()
    for e in entities:
        e = canonical_known(normalize_entity(e))
        if not e or e in STOP:
            continue
        if len(e) < 3:
            continue
        if e not in seen:
            cleaned.append(e)
            seen.add(e)

    return cleaned

with CATALOG.open("r", encoding="utf-8", newline="") as f:
    docs = list(csv.DictReader(f, delimiter="\t"))

doc_rows = []
entity_docs = defaultdict(set)
entity_words = Counter()
entity_processes = defaultdict(set)
entity_collections = defaultdict(set)
pair_docs = defaultdict(set)

for d in docs:
    doc_id = d["document_post_id"]
    title = d["document_title"]
    entities = extract_entities(title)
    words = int(d.get("content_words") or 0)

    for e in entities:
        entity_docs[e].add(doc_id)
        entity_words[e] += words
        if d.get("primary_process"):
            entity_processes[e].add(d["primary_process"])
        if d.get("primary_collection"):
            entity_collections[e].add(d["primary_collection"])

    for i, a in enumerate(entities):
        for b in entities[i+1:]:
            key = tuple(sorted([a, b]))
            pair_docs[key].add(doc_id)

    doc_rows.append({
        "document_post_id": doc_id,
        "document_date": d.get("document_date", ""),
        "document_title": title,
        "primary_process": d.get("primary_process", ""),
        "primary_collection": d.get("primary_collection", ""),
        "entities": " | ".join(entities),
        "entity_count": len(entities),
        "document_url": d.get("document_url", ""),
    })

with OUT_DOC_ENTITIES.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_post_id", "document_date", "document_title",
        "primary_process", "primary_collection",
        "entities", "entity_count", "document_url"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(doc_rows)

with OUT_ENTITIES.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "entity", "document_count", "total_words",
        "process_count", "processes", "collection_count", "collections"
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for e, ids in sorted(entity_docs.items(), key=lambda x: len(x[1]), reverse=True):
        w.writerow({
            "entity": e,
            "document_count": len(ids),
            "total_words": entity_words[e],
            "process_count": len(entity_processes[e]),
            "processes": " | ".join(sorted(entity_processes[e])),
            "collection_count": len(entity_collections[e]),
            "collections": " | ".join(sorted(entity_collections[e])),
        })

with OUT_PAIRS.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["entity_a", "entity_b", "document_count"])
    for (a, b), ids in sorted(pair_docs.items(), key=lambda x: len(x[1]), reverse=True):
        w.writerow([a, b, len(ids)])

with_entities = [r for r in doc_rows if r["entity_count"] > 0]

report = []
report.append("ShowTrials title entity diagnosis")
report.append("")
report.append(f"Documents loaded: {len(docs)}")
report.append(f"Documents with title entities: {len(with_entities)}")
report.append(f"Candidate entities: {len(entity_docs)}")
report.append(f"Candidate pairs: {len(pair_docs)}")
report.append("")
report.append("Top entities:")
for e, ids in sorted(entity_docs.items(), key=lambda x: len(x[1]), reverse=True)[:60]:
    report.append(f"{len(ids)}\t{entity_words[e]}\t{e}")
report.append("")
report.append("Top entity pairs:")
for (a, b), ids in sorted(pair_docs.items(), key=lambda x: len(x[1]), reverse=True)[:60]:
    report.append(f"{len(ids)}\t{a}\t{b}")
report.append("")
report.append("Documents without extracted title entities:")
for r in [x for x in doc_rows if x["entity_count"] == 0][:40]:
    report.append(f"{r['document_post_id']}\t{r['document_title']}")

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_DOC_ENTITIES)
print(OUT_ENTITIES)
print(OUT_PAIRS)
print(OUT_REPORT)
