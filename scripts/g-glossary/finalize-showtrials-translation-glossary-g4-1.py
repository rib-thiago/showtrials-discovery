#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import Counter

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    GOOGLE_TRANSLATE_GLOSSARY_RU_EN_V1,
    TRANSLATION_GLOSSARY_G4,
    TRANSLATION_GLOSSARY_G4_1,
    TRANSLATION_GLOSSARY_G4_1_REPORT,
    TRANSLATION_GLOSSARY_G4_1_REVIEW,
    ensure_parent,
)

G4 = TRANSLATION_GLOSSARY_G4

OUT = TRANSLATION_GLOSSARY_G4_1
REVIEW = TRANSLATION_GLOSSARY_G4_1_REVIEW
GOOGLE_GLOSSARY = GOOGLE_TRANSLATE_GLOSSARY_RU_EN_V1
REPORT = TRANSLATION_GLOSSARY_G4_1_REPORT

PATCHES = {
    "Е.К. Мухановой": {
        "canonical_en": "E.K. Mukhanova",
        "status": "approved",
        "confidence": "high",
        "g4_action": "approved_by_g4_1_external_confirmation",
        "notes": "Confirmed as Е.К. Муханова / Ekaterina Konstantinovna Mukhanova in Kremlin Case references.",
    },
}

ROLE_POLICY = {
    "троцкист": {
        "canonical_en": "Trotskyist",
        "status": "approved",
        "confidence": "high",
        "notes": "Political/accusatory label. Preserve as Trotskyist; do not neutralize as ordinary party affiliation.",
    },
    "правый": {
        "canonical_en": "Rightist",
        "status": "approved",
        "confidence": "high",
        "notes": "Political label in Soviet opposition context. Preserve as Rightist.",
    },
    "агент": {
        "canonical_en": "agent",
        "status": "approved",
        "confidence": "medium",
        "notes": "Context-sensitive term: may mean agent, operative, or accused intelligence/foreign agent.",
    },
    "вредитель": {
        "canonical_en": "wrecker",
        "status": "approved",
        "confidence": "high",
        "notes": "Accusatory Stalinist term. Preserve conventional historical rendering: wrecker.",
    },
}

rows = list(csv.DictReader(G4.open("r", encoding="utf-8", newline=""), delimiter="\t"))

out_rows = []
review_rows = []

for r in rows:
    row = dict(r)
    src = row["source_ru"]

    if src in PATCHES and row["layer"] == "people":
        p = PATCHES[src]
        row["canonical_en"] = p["canonical_en"]
        row["status"] = p["status"]
        row["confidence"] = p["confidence"]
        row["g4_action"] = p["g4_action"]
        row["g4_review_priority"] = ""
        row["g4_review_reason"] = ""
        row["historical_person_tier"] = "tier2_significant"
        row["notes"] = p["notes"]

    if src in ROLE_POLICY and row["layer"] == "roles":
        p = ROLE_POLICY[src]
        row["canonical_en"] = p["canonical_en"]
        row["status"] = p["status"]
        row["confidence"] = p["confidence"]
        row["g4_review_priority"] = ""
        row["g4_review_reason"] = ""
        row["g4_action"] = "approved_by_g4_1_semantic_role_policy"
        row["notes"] = p["notes"]

    if row.get("g4_review_reason"):
        review_rows.append(row)

    out_rows.append(row)

fields = rows[0].keys()

with ensure_parent(OUT).open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(out_rows)

with ensure_parent(REVIEW).open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(review_rows)

# Arquivo simples para importação/adaptação em glossário RU→EN.
# Inclui somente entradas aprovadas e úteis para tradução, excluindo document_types internos.
google_rows = []
for r in out_rows:
    if r["status"] != "approved":
        continue
    if r["layer"] == "document_types":
        continue
    if not r["source_ru"] or not r["canonical_en"]:
        continue
    google_rows.append({
        "source_ru": r["source_ru"],
        "target_en": r["canonical_en"],
        "layer": r["layer"],
        "glossary_kind": r["glossary_kind"],
        "confidence": r["confidence"],
    })

with ensure_parent(GOOGLE_GLOSSARY).open("w", encoding="utf-8", newline="") as f:
    fields2 = ["source_ru", "target_en", "layer", "glossary_kind", "confidence"]
    w = csv.DictWriter(f, fieldnames=fields2, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(google_rows, key=lambda x: (x["layer"], x["source_ru"])))

by_status = Counter(r["status"] for r in out_rows)
by_layer = Counter(r["layer"] for r in out_rows)
review_by_reason = Counter(r.get("g4_review_reason", "") for r in review_rows)

report = []
report.append("ShowTrials translation glossary G4.1 finalization")
report.append("")
report.append(f"Input rows: {len(rows)}")
report.append(f"Output rows: {len(out_rows)}")
report.append(f"Remaining review rows: {len(review_rows)}")
report.append(f"Google glossary candidate rows: {len(google_rows)}")
report.append("")
report.append("Rows by layer:")
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")
report.append("")
report.append("Remaining review by reason:")
for k, v in sorted(review_by_reason.items(), key=lambda x: (-x[1], x[0])):
    report.append(f"{k or 'NONE'}\t{v}")
report.append("")
report.append("Applied patches:")
for k, v in PATCHES.items():
    report.append(f"{k}\t→\t{v['canonical_en']}")
for k, v in ROLE_POLICY.items():
    report.append(f"{k}\t→\t{v['canonical_en']}")
report.append("")
report.append("Outputs:")
report.append(str(OUT))
report.append(str(REVIEW))
report.append(str(GOOGLE_GLOSSARY))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT)
print(REVIEW)
print(GOOGLE_GLOSSARY)
print(REPORT)
