#!/usr/bin/env bash
set -euo pipefail

log(){ printf '[%(%F %T)T] %s\n' -1 "$*" >&2; }
fail(){ log "ERROR: $*"; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MANIFEST="${1:-data/perpetrator2004/manifests/perpetrator2004_full_ingestion_manifest.tsv}"

[[ -f "$MANIFEST" ]] || fail "manifest not found: $MANIFEST"

TS="$(date +%Y%m%d-%H%M%S)"
DIAG_DIR="data/perpetrator2004/diagnostics"
REPORT_DIR="reports/perpetrator2004"
NORM_DIR="data/perpetrator2004/manifests"

mkdir -p "$DIAG_DIR" "$REPORT_DIR" "$NORM_DIR"

DIAG="$DIAG_DIR/perpetrator2004_manifest_diagnostics_v2_${TS}.tsv"
SUMMARY="$DIAG_DIR/perpetrator2004_manifest_summary_v2_${TS}.tsv"
NORMALIZED="$NORM_DIR/perpetrator2004_full_ingestion_manifest.normalized_${TS}.tsv"
REPORT="$REPORT_DIR/perpetrator2004_manifest_diagnostics_v2_report_${TS}.txt"

log "Diagnosing manifest: $ROOT/$MANIFEST"

python3 - "$MANIFEST" "$DIAG" "$SUMMARY" "$NORMALIZED" "$REPORT" <<'PY'
import csv
import os
import sys
from collections import Counter
from urllib.parse import urlparse

manifest, diag_path, summary_path, normalized_path, report_path = sys.argv[1:]
internal_domain = "perpetrator2004.narod.ru"

required = [
    "item_id", "href", "resolved_url", "label",
    "is_html", "is_external", "source_class", "target_path"
]

diagnostics = []
summary = Counter()
rows = []

def emit(level, item_id, field, problem, value="", line_no=""):
    diagnostics.append({
        "level": level,
        "item_id": item_id,
        "field": field,
        "problem": problem,
        "value": value,
        "line_no": str(line_no),
    })

with open(manifest, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")
    header = reader.fieldnames or []

    if header != required:
        emit("ERROR", "__header__", "__header__", "invalid_header", "|".join(header), 1)

    seen_ids = set()
    seen_targets = set()

    for line_no, row in enumerate(reader, start=2):
        clean = {k: (row.get(k) or "").strip() for k in required}
        rows.append(clean)

        item = clean["item_id"]
        href = clean["href"]
        resolved = clean["resolved_url"]
        label = clean["label"]
        is_html = clean["is_html"]
        is_external = clean["is_external"]
        source_class = clean["source_class"]
        target = clean["target_path"]

        summary["rows"] += 1

        for col in required:
            if not clean[col] and col not in {"label"}:
                emit("ERROR", item or "__blank__", col, "blank_required_field", "", line_no)

        if item in seen_ids:
            emit("ERROR", item, "item_id", "duplicate_item_id", item, line_no)
        seen_ids.add(item)

        if target in seen_targets:
            emit("ERROR", item, "target_path", "duplicate_target_path", target, line_no)
        seen_targets.add(target)

        if is_html not in {"yes", "no"}:
            emit("ERROR", item, "is_html", "invalid_boolean_expected_yes_no", is_html, line_no)

        if is_external not in {"yes", "no"}:
            emit("ERROR", item, "is_external", "invalid_boolean_expected_yes_no", is_external, line_no)

        if source_class not in {"internal", "external"}:
            emit("ERROR", item, "source_class", "invalid_source_class_expected_internal_external", source_class, line_no)

        parsed = urlparse(resolved or href)
        domain = parsed.netloc.lower()
        extension = os.path.splitext(parsed.path)[1].lower() or "__no_ext__"

        summary[f"domain.{domain or '__blank__'}"] += 1
        summary[f"extension.{extension}"] += 1
        summary[f"is_html.{is_html or '__blank__'}"] += 1
        summary[f"is_external.{is_external or '__blank__'}"] += 1
        summary[f"source_class.{source_class or '__blank__'}"] += 1

        expected_external = "no" if domain == internal_domain else "yes"
        expected_class = "internal" if expected_external == "no" else "external"

        if is_external in {"yes", "no"} and is_external != expected_external:
            emit("WARN", item, "is_external", f"external_flag_mismatch_expected_{expected_external}", resolved, line_no)

        if source_class in {"internal", "external"} and source_class != expected_class:
            emit("WARN", item, "source_class", f"source_class_mismatch_expected_{expected_class}", resolved, line_no)

        if source_class == "internal" and not target.startswith("data/perpetrator2004/raw/mirror/"):
            emit("ERROR", item, "target_path", "internal_target_outside_mirror_root", target, line_no)

        if source_class == "external" and not target.startswith("data/perpetrator2004/raw/mirror/external/"):
            emit("ERROR", item, "target_path", "external_target_outside_external_mirror_root", target, line_no)

        if label in {"", "-"}:
            if source_class == "external":
                emit("INFO", item, "label", "blank_or_dash_label_accepted_for_external", label, line_no)
            else:
                emit("WARN", item, "label", "blank_label", label, line_no)

errors = sum(1 for d in diagnostics if d["level"] == "ERROR")
warns = sum(1 for d in diagnostics if d["level"] == "WARN")
infos = sum(1 for d in diagnostics if d["level"] == "INFO")
problems_total = errors + warns

with open(diag_path, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, delimiter="\t", fieldnames=["level", "item_id", "field", "problem", "value", "line_no"])
    w.writeheader()
    w.writerows(diagnostics)

with open(summary_path, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["metric", "value"])
    w.writerow(["manifest", os.path.abspath(manifest)])
    w.writerow(["rows", summary["rows"]])
    w.writerow(["problems_total", problems_total])
    w.writerow(["errors", errors])
    w.writerow(["warnings", warns])
    w.writerow(["infos", infos])
    w.writerow(["header_status", "ok" if not any(d["item_id"] == "__header__" for d in diagnostics) else "bad"])
    w.writerow(["diagnostics_tsv", os.path.abspath(diag_path)])
    w.writerow(["summary_tsv", os.path.abspath(summary_path)])
    w.writerow(["normalized_tsv", os.path.abspath(normalized_path)])
    for k in sorted(summary):
        if k != "rows":
            w.writerow([k, summary[k]])

with open(normalized_path, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, delimiter="\t", fieldnames=required)
    w.writeheader()
    w.writerows(rows)

with open(report_path, "w", encoding="utf-8") as f:
    f.write("Perpetrator2004 Manifest Diagnostics v2\n")
    f.write(f"manifest\t{os.path.abspath(manifest)}\n")
    f.write(f"diagnostics_tsv\t{os.path.abspath(diag_path)}\n")
    f.write(f"summary_tsv\t{os.path.abspath(summary_path)}\n")
    f.write(f"normalized_tsv\t{os.path.abspath(normalized_path)}\n\n")
    f.write("Summary\n")
    f.write(f"rows\t{summary['rows']}\n")
    f.write(f"problems_total\t{problems_total}\n")
    f.write(f"errors\t{errors}\n")
    f.write(f"warnings\t{warns}\n")
    f.write(f"infos\t{infos}\n\n")
    f.write("Top diagnostics\n")
    for d in diagnostics[:25]:
        f.write("\t".join([d["level"], d["item_id"], d["field"], d["problem"], d["value"], d["line_no"]]) + "\n")

print(f"rows={summary['rows']}")
print(f"problems={problems_total}")
print(f"errors={errors}")
print(f"warnings={warns}")
print(f"infos={infos}")
print(f"diagnostics_tsv={os.path.abspath(diag_path)}")
print(f"summary_tsv={os.path.abspath(summary_path)}")
print(f"normalized_tsv={os.path.abspath(normalized_path)}")
print(f"report={os.path.abspath(report_path)}")
PY
