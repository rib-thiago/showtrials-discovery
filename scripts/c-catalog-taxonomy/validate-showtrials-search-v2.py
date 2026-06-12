#!/usr/bin/env python3
import csv
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    PROJECT_ROOT,
    SEARCH_V2_SCRIPT,
    SEARCH_V2_VALIDATION,
    SEARCH_V2_VALIDATION_REPORT,
    ensure_parent,
)

BASE = PROJECT_ROOT
SEARCH = SEARCH_V2_SCRIPT
REPORT = SEARCH_V2_VALIDATION_REPORT
TSV = SEARCH_V2_VALIDATION

TESTS = [
    {
        "name": "text_radek_yagoda",
        "args": ["Радек", "Ягода", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "person_stalin",
        "args": ["--person", "Сталин", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "organization_nkvd",
        "args": ["--organization", "НКВД", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "family_security",
        "args": ["--family", "security_apparatus", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "process_march_1938",
        "args": ["--process", "МАРТА 1938", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "doctype_interrogation",
        "args": ["--doctype", "interrogation_protocol", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "role_prosecutor",
        "args": ["--role", "прокурор", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "combined_bukharin_march",
        "args": ["--person", "Бухарин", "--process", "МАРТА 1938", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
    {
        "name": "combined_security_special_report",
        "args": ["--family", "security_apparatus", "--doctype", "special_report", "--limit", "5", "--format", "tsv"],
        "min_rows": 1,
    },
]

rows = []
failures = 0

for t in TESTS:
    cmd = [str(SEARCH)] + t["args"]
    proc = subprocess.run(
        cmd,
        cwd=str(BASE),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    status = "PASS"
    detail = ""

    if proc.returncode != 0:
        status = "FAIL"
        detail = proc.stderr.strip()
    else:
        lines = [x for x in proc.stdout.splitlines() if x.strip()]
        data_rows = max(0, len(lines) - 1) if lines else 0
        if data_rows < t["min_rows"]:
            status = "FAIL"
            detail = f"expected >= {t['min_rows']} data rows, got {data_rows}"
        else:
            detail = f"rows={data_rows}"

    if status == "FAIL":
        failures += 1

    rows.append({
        "test": t["name"],
        "status": status,
        "command": " ".join(cmd),
        "detail": detail,
    })

with ensure_parent(TSV).open("w", encoding="utf-8", newline="") as f:
    fields = ["test", "status", "command", "detail"]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(rows)

report = []
report.append("ShowTrials search v2 validation")
report.append("")
report.append(f"Tests: {len(rows)}")
report.append(f"Failures: {failures}")
report.append("")
for r in rows:
    report.append(f"{r['status']}\t{r['test']}\t{r['detail']}")

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)

sys.exit(1 if failures else 0)
