#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter

BASE = Path("/tmp/showtrials-discovery")

G = BASE / "showtrials_translation_glossary_g4_1.tsv"
GG = BASE / "showtrials_google_translate_glossary_ru_en_v1.tsv"

REPORT = BASE / "showtrials_translation_glossary_g4_1_validation_report.txt"
TSV = BASE / "showtrials_translation_glossary_g4_1_validation.tsv"

rows = list(csv.DictReader(G.open("r", encoding="utf-8", newline=""), delimiter="\t"))
google_rows = list(csv.DictReader(GG.open("r", encoding="utf-8", newline=""), delimiter="\t"))

checks = []
failures = 0
warnings = 0

def add(level, check, detail):
    global failures, warnings
    checks.append({"level": level, "check": check, "detail": detail})
    if level == "FAIL":
        failures += 1
    elif level == "WARN":
        warnings += 1

seen = set()
for r in rows:
    key = (r["source_ru"], r["layer"])
    if key in seen:
        add("FAIL", "duplicate_source_layer", f"{r['layer']} {r['source_ru']}")
    seen.add(key)

    if r["status"] == "approved" and not r["canonical_en"]:
        add("FAIL", "approved_without_canonical", f"{r['layer']} {r['source_ru']}")

    if r["layer"] in {"organizations", "processes"} and r["status"] != "approved":
        add("FAIL", "org_or_process_unapproved", f"{r['layer']} {r['source_ru']}")

    if r["layer"] == "people":
        n = int(r.get("person_document_count") or r.get("source_count") or 0)
        if n >= 10 and r["status"] != "approved":
            add("FAIL", "person_10plus_unapproved", f"{n} {r['source_ru']} → {r['canonical_en']}")
        elif n >= 5 and r["status"] != "approved":
            add("WARN", "person_5plus_unapproved", f"{n} {r['source_ru']} → {r['canonical_en']}")

required = {
    "Е.К. Мухановой": "E.K. Mukhanova",
    "троцкист": "Trotskyist",
    "правый": "Rightist",
    "агент": "agent",
    "вредитель": "wrecker",
}
lookup = {r["source_ru"]: r["canonical_en"] for r in rows}
for src, expected in required.items():
    if lookup.get(src) != expected:
        add("FAIL", "required_patch_missing", f"{src}: expected {expected}, got {lookup.get(src)}")

g_seen = set()
for r in google_rows:
    key = (r["source_ru"], r["target_en"])
    if key in g_seen:
        add("FAIL", "duplicate_google_glossary_row", f"{r['source_ru']} → {r['target_en']}")
    g_seen.add(key)

if not checks:
    add("OK", "all_checks", "passed")

with TSV.open("w", encoding="utf-8", newline="") as f:
    fields = ["level", "check", "detail"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(checks)

by_status = Counter(r["status"] for r in rows)
by_layer = Counter(r["layer"] for r in rows)

report = [
    "ShowTrials translation glossary G4.1 validation",
    "",
    f"Rows: {len(rows)}",
    f"Google glossary rows: {len(google_rows)}",
    f"Failures: {failures}",
    f"Warnings: {warnings}",
    "",
    "Rows by layer:",
]
for k, v in sorted(by_layer.items()):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Rows by status:")
for k, v in sorted(by_status.items()):
    report.append(f"{k}\t{v}")

report.append("")
report.append("Validation rows:")
for c in checks[:120]:
    report.append(f"{c['level']}\t{c['check']}\t{c['detail']}")

REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)
