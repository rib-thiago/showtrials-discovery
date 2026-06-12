#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from collections import defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.showtrials_paths import (  # noqa: E402
    ORGANIZATION_HIERARCHY,
    ORGANIZATION_HIERARCHY_VALIDATION,
    ORGANIZATION_HIERARCHY_VALIDATION_REPORT,
    ORGANIZATIONS,
    ensure_parent,
)

ORGS = ORGANIZATIONS
HIER = ORGANIZATION_HIERARCHY

REPORT = ORGANIZATION_HIERARCHY_VALIDATION_REPORT
TSV = ORGANIZATION_HIERARCHY_VALIDATION

def load_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

orgs = {r["organization"]: r for r in load_tsv(ORGS)}
rows = load_tsv(HIER)

failures = []
warnings = []

seen = set()
graph = defaultdict(list)

for r in rows:
    child = r["child_organization"]
    parent = r["parent_organization"]

    key = (child, parent, r["relation_type"])
    if key in seen:
        failures.append(("duplicate_relation", child, parent))
    seen.add(key)

    if child not in orgs:
        failures.append(("missing_child", child, parent))
    if parent not in orgs:
        failures.append(("missing_parent", child, parent))

    if child == parent:
        failures.append(("self_relation", child, parent))

    graph[child].append(parent)

def has_cycle():
    visiting = set()
    visited = set()

    def visit(node, path):
        if node in visiting:
            return path + [node]
        if node in visited:
            return None
        visiting.add(node)
        for parent in graph.get(node, []):
            cycle = visit(parent, path + [node])
            if cycle:
                return cycle
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node, [])
        if cycle:
            return cycle
    return None

cycle = has_cycle()
if cycle:
    failures.append(("cycle", " -> ".join(cycle), ""))

if not rows:
    warnings.append(("empty_hierarchy", "", ""))

medium = [r for r in rows if r["confidence"] != "high"]
if medium:
    warnings.append(("manual_review_recommended", str(len(medium)), ""))

with ensure_parent(TSV).open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["level", "check", "subject", "detail"])
    for item in failures:
        w.writerow(["FAIL", *item])
    for item in warnings:
        w.writerow(["WARN", *item])
    if not failures and not warnings:
        w.writerow(["OK", "all_checks", "passed", ""])

report = []
report.append("ShowTrials organization hierarchy validation")
report.append("")
report.append(f"Organizations: {len(orgs)}")
report.append(f"Hierarchy rows: {len(rows)}")
report.append(f"Failures: {len(failures)}")
report.append(f"Warnings: {len(warnings)}")
report.append("")
if failures:
    report.append("Failures:")
    for item in failures:
        report.append("\t".join(item))
if warnings:
    report.append("Warnings:")
    for item in warnings:
        report.append("\t".join(item))

ensure_parent(REPORT).write_text("\n".join(report) + "\n", encoding="utf-8")

print(REPORT)
print(TSV)
