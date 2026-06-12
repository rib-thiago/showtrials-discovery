#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    LITERAL_PEOPLE,
    ORGANIZATIONS,
    PROCESSES,
    ROLES_V2,
    TRANSLATION_GLOSSARY_SEEDS_V1,
    TRANSLATION_GLOSSARY_SEEDS_V1_REPORT,
    TRANSLATION_PROFILES_V1,
    ensure_parent,
)

PEOPLE = LITERAL_PEOPLE
ORGS = ORGANIZATIONS
ROLES = ROLES_V2
DOC_TYPES = TRANSLATION_PROFILES_V1

OUT = TRANSLATION_GLOSSARY_SEEDS_V1
REPORT = TRANSLATION_GLOSSARY_SEEDS_V1_REPORT

ORG_CANONICAL = {
    "НКВД": "NKVD",
    "ГУГБ": "GUGB",
    "ИНО ГУГБ": "Foreign Department of the GUGB",
    "ОО ГУГБ НКВД": "Special Department of the GUGB NKVD",
    "ВКП(б)": "All-Union Communist Party (Bolsheviks)",
    "ЦК ВКП(б)": "Central Committee of the All-Union Communist Party (Bolsheviks)",
    "Политбюро": "Politburo",
    "КПК": "Party Control Commission",
    "КПК при ЦК ВКП(б)": "Party Control Commission under the Central Committee of the All-Union Communist Party (Bolsheviks)",
    "Горьковский крайком ВКП(б)": "Gorky Regional Committee of the All-Union Communist Party (Bolsheviks)",
    "Коминтерн": "Comintern",
    "ИККИ": "Executive Committee of the Communist International",
    "ЦИК СССР": "Central Executive Committee of the USSR",
    "Секретариат ЦИК СССР": "Secretariat of the Central Executive Committee of the USSR",
    "Совнарком": "Council of People's Commissars",
    "Верховный Совет СССР": "Supreme Soviet of the USSR",
    "НКИД": "People's Commissariat for Foreign Affairs",
    "Прокуратура СССР": "Prosecutor's Office of the USSR",
    "Верховный Суд СССР": "Supreme Court of the USSR",
    "Правда": "Pravda",
    "Известия": "Izvestia",
    "Лига Наций": "League of Nations",
}

ROLE_CANONICAL = {
    "нарком": "People's Commissar",
    "наркомвнудел": "People's Commissar of Internal Affairs",
    "следователь": "investigator",
    "прокурор": "prosecutor",
    "председатель": "chairman",
    "секретарь": "secretary",
    "начальник": "chief",
    "заместитель": "deputy",
    "комиссар": "commissar",
    "судья": "judge",
    "секретарь_суда": "court secretary",
    "адвокат": "defense attorney",
    "редактор": "editor",
    "корреспондент": "correspondent",
    "посол": "ambassador",
    "полпред": "plenipotentiary representative",
    "директор": "director",
    "руководитель": "leader",
    "обвиняемый": "accused",
    "подсудимый": "defendant",
    "свидетель": "witness",
    "троцкист": "Trotskyist",
    "правый": "Rightist",
    "вредитель": "wrecker",
    "агент": "agent",
    "член": "member",
    "кандидат": "candidate",
    "представитель": "representative",
    "сотрудник": "staff member",
}

PROCESS_CANONICAL = {
    "ПРОЦЕСС 19-23 АВГУСТА 1936 г.": "August 1936 Trial",
    "ПРОЦЕСС 23-29 ЯНВАРЯ 1937 г.": "January 1937 Trial",
    "ПРОЦЕСС 2-12 МАРТА 1938 г.": "March 1938 Trial",
    "ПРОЦЕСС “МОСКОВСКОГО ЦЕНТРА”": "Moscow Center Trial",
    "ПРОЦЕСС “ЛЕНИНГРАДСКОГО ЦЕНТРА”": "Leningrad Center Trial",
    "КРЕМЛЕВСКОЕ ДЕЛО": "Kremlin Case",
    "ТРОЦКИЙ": "Trotsky Dossier",
    "СТАТЬИ": "Articles",
    "РАЗНЫЕ ДОКУМЕНТЫ": "Miscellaneous Documents",
}

DOC_TYPE_CANONICAL = {
    "interrogation_protocol": "interrogation protocol",
    "special_report": "special report",
    "session_transcript": "session transcript",
    "letter": "letter",
    "statement": "statement",
    "confrontation_protocol": "confrontation protocol",
    "testimony": "testimony",
    "memo_note": "memo note",
    "conversation_recording": "conversation recording",
    "telegram": "telegram",
    "indictment": "indictment",
    "verdict_or_sentence": "verdict or sentence",
    "press_summary": "press summary",
    "administrative_report": "administrative report",
    "reference_note": "reference note",
    "list": "list",
}

CYR = {
    "А":"A","Б":"B","В":"V","Г":"G","Д":"D","Е":"E","Ё":"E","Ж":"Zh","З":"Z","И":"I","Й":"I",
    "К":"K","Л":"L","М":"M","Н":"N","О":"O","П":"P","Р":"R","С":"S","Т":"T","У":"U",
    "Ф":"F","Х":"Kh","Ц":"Ts","Ч":"Ch","Ш":"Sh","Щ":"Shch","Ы":"y","Э":"E","Ю":"Yu","Я":"Ya",
    "Ь":"","Ъ":"",
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"i",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u",
    "ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ы":"y","э":"e","ю":"yu","я":"ya",
    "ь":"","ъ":"",
}

def translit(s):
    return "".join(CYR.get(ch, ch) for ch in s)

def tidy(s):
    return re.sub(r"\s+", " ", s or "").strip()

def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

rows = []

def add(source_ru, canonical_en, layer, kind, priority, source_count, status, confidence, notes):
    source_ru = tidy(source_ru)
    canonical_en = tidy(canonical_en)
    if not source_ru:
        return
    rows.append({
        "source_ru": source_ru,
        "canonical_en": canonical_en,
        "layer": layer,
        "glossary_kind": kind,
        "priority": priority,
        "source_count": source_count,
        "status": status,
        "confidence": confidence,
        "notes": notes,
    })

for r in load(PROCESSES):
    src = r["process"]
    add(
        src,
        PROCESS_CANONICAL.get(src, ""),
        "processes",
        "process_name",
        "high",
        r.get("document_count", ""),
        "approved" if src in PROCESS_CANONICAL else "pending",
        "high" if src in PROCESS_CANONICAL else "low",
        "canonical process label",
    )

for r in load(ORGS):
    src = r["organization"]
    add(
        src,
        ORG_CANONICAL.get(src, ""),
        "organizations",
        "organization",
        "high",
        r.get("document_count", ""),
        "approved" if src in ORG_CANONICAL else "pending",
        "high" if src in ORG_CANONICAL else "low",
        "canonical organization/institution label",
    )

for r in load(ROLES):
    src = r["role"]
    add(
        src,
        ROLE_CANONICAL.get(src, ""),
        "roles",
        r.get("role_class", "role_or_label"),
        "medium",
        r.get("document_count", ""),
        "approved" if src in ROLE_CANONICAL else "pending",
        "high" if src in ROLE_CANONICAL else "low",
        "role/label translation; review political and accusatory labels",
    )

for r in load(DOC_TYPES):
    src = r["document_type"]
    add(
        src,
        DOC_TYPE_CANONICAL.get(src, src.replace("_", " ")),
        "document_types",
        "internal_document_type",
        "low",
        r.get("documents", ""),
        "approved",
        "medium",
        "internal UI/reporting label; not necessarily Google glossary entry",
    )

for r in load(PEOPLE):
    src = r["person"]
    count = int(r.get("document_count") or 0)

    if count >= 20:
        priority = "high"
    elif count >= 5:
        priority = "medium"
    else:
        priority = "low"

    add(
        src,
        translit(src),
        "people",
        "person_name",
        priority,
        count,
        "auto_transliterated_needs_review",
        "medium" if count >= 5 else "low",
        "automatic transliteration seed; human review recommended before production glossary",
    )

rows = sorted(
    rows,
    key=lambda r: (
        {"high": 0, "medium": 1, "low": 2}.get(r["priority"], 9),
        {"approved": 0, "auto_transliterated_needs_review": 1, "pending": 2}.get(r["status"], 9),
        -int(r["source_count"] or 0),
        r["layer"],
        r["source_ru"],
    )
)

with ensure_parent(OUT).open("w", encoding="utf-8", newline="") as f:
    fields = [
        "source_ru", "canonical_en", "layer", "glossary_kind",
        "priority", "source_count", "status", "confidence", "notes",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

by_layer = {}
for r in rows:
    by_layer.setdefault(r["layer"], 0)
    by_layer[r["layer"]] += 1

by_status = {}
for r in rows:
    by_status.setdefault(r["status"], 0)
    by_status[r["status"]] += 1

report = []
report.append("ShowTrials translation glossary seeds v1")
report.append("")
report.append(f"Glossary rows: {len(rows)}")
report.append("")
report.append("Rows by layer:")
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("High-priority review queue:")
for r in rows[:80]:
    if r["priority"] != "high":
        continue
    report.append(
        f"{r['source_count']}\t{r['status']}\t{r['layer']}\t{r['source_ru']}\t→\t{r['canonical_en']}"
    )

report.append("")
report.append("Output:")
report.append(str(OUT))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REPORT)
