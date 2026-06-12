#!/usr/bin/env python3
"""Diagnose script readiness for centralized ShowTrials path handling."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OUT = ROOT / "data/r-governance/path-audit/showtrials_path_normalization_readiness.tsv"
REPORT = ROOT / "reports/r-governance/path-audit/showtrials_path_normalization_readiness_report.txt"

SCRIPT_GLOBS = ["scripts/**/*.py", "scripts/**/*.sh"]

PATTERNS = {
    "tmp_base": re.compile(r"/tmp/" + "showtrials-discovery"),
    "srv_base": re.compile(r"/srv/projects/" + "showtrials-discovery"),
    "root_artifact_tsv": re.compile(r"""["']showtrials_[^"']+\.tsv["']"""),
    "root_artifact_txt": re.compile(r"""["']showtrials_[^"']+\.txt["']"""),
    "root_artifact_json": re.compile(r"""["']showtrials_[^"']+\.json["']"""),
    "old_export_dir": re.compile(r"""["'](?:export-txt|export-md|pages-json|posts-json|posts-json-embed|showtrials\.ru|structural_samples_d2_1)["']"""),
    "path_constructor": re.compile(r"Path\("),
    "open_call": re.compile(r"\.open\(|\bopen\("),
    "uses_showtrials_paths": re.compile(r"showtrials_paths|from scripts\.lib|from lib\.showtrials_paths|import showtrials_paths"),
}

def script_files() -> list[Path]:
    files: list[Path] = []
    for glob in SCRIPT_GLOBS:
        files.extend(ROOT.glob(glob))
    return sorted(set(p for p in files if p.is_file()))

def classify_priority(counts: Counter[str]) -> str:
    critical = counts["tmp_base"] + counts["srv_base"] + counts["root_artifact_tsv"] + counts["root_artifact_txt"] + counts["root_artifact_json"]
    if critical >= 10:
        return "critical"
    if critical > 0:
        return "high"
    if counts["old_export_dir"] > 0:
        return "medium"
    return "low"

def main() -> int:
    rows = []
    totals = Counter()
    phase_counts = defaultdict(Counter)

    for path in script_files():
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8", errors="replace")
        counts = Counter()

        for name, pattern in PATTERNS.items():
            counts[name] = len(pattern.findall(text))

        phase = rel.split("/")[1] if rel.startswith("scripts/") and "/" in rel else "-"
        if rel.startswith("scripts/lib/"):
            priority = "low"
        else:
            priority = classify_priority(counts)

        row = {
            "script_path": rel,
            "phase": phase,
            "priority": priority,
            "uses_showtrials_paths": "yes" if counts["uses_showtrials_paths"] else "no",
            "tmp_base_refs": counts["tmp_base"],
            "srv_base_refs": counts["srv_base"],
            "root_tsv_refs": counts["root_artifact_tsv"],
            "root_txt_refs": counts["root_artifact_txt"],
            "root_json_refs": counts["root_artifact_json"],
            "old_export_dir_refs": counts["old_export_dir"],
            "path_constructor_refs": counts["path_constructor"],
            "open_call_refs": counts["open_call"],
            "notes": "needs_path_normalization" if priority in {"critical", "high", "medium"} else "no_obvious_legacy_paths",
        }
        rows.append(row)

        totals.update({
            "scripts_scanned": 1,
            "tmp_base_refs": counts["tmp_base"],
            "srv_base_refs": counts["srv_base"],
            "root_tsv_refs": counts["root_artifact_tsv"],
            "root_txt_refs": counts["root_artifact_txt"],
            "root_json_refs": counts["root_artifact_json"],
            "old_export_dir_refs": counts["old_export_dir"],
            "uses_showtrials_paths": 1 if counts["uses_showtrials_paths"] else 0,
        })
        phase_counts[phase][priority] += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "script_path", "phase", "priority", "uses_showtrials_paths",
            "tmp_base_refs", "srv_base_refs", "root_tsv_refs", "root_txt_refs",
            "root_json_refs", "old_export_dir_refs", "path_constructor_refs",
            "open_call_refs", "notes",
        ]
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    priority_counts = Counter(row["priority"] for row in rows)

    lines = [
        "ShowTrials Path Normalization Readiness Report",
        f"scripts_scanned\t{totals['scripts_scanned']}",
        f"uses_showtrials_paths\t{totals['uses_showtrials_paths']}",
        f"tmp_base_refs\t{totals['tmp_base_refs']}",
        f"srv_base_refs\t{totals['srv_base_refs']}",
        f"root_tsv_refs\t{totals['root_tsv_refs']}",
        f"root_txt_refs\t{totals['root_txt_refs']}",
        f"root_json_refs\t{totals['root_json_refs']}",
        f"old_export_dir_refs\t{totals['old_export_dir_refs']}",
        "",
        "priority_counts",
    ]

    for key in ["critical", "high", "medium", "low"]:
        lines.append(f"{key}\t{priority_counts.get(key, 0)}")

    lines.append("")
    lines.append("phase_priority_counts")
    for phase in sorted(phase_counts):
        for key in ["critical", "high", "medium", "low"]:
            if phase_counts[phase].get(key, 0):
                lines.append(f"{phase}\t{key}\t{phase_counts[phase][key]}")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(OUT)
    print(REPORT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
