#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[%(%F %T)T] %s\n' -1 "$*" >&2
}

fail() {
  log "ERROR: $*"
  exit 1
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || fail "cannot enter repository root: $ROOT"

command -v python3 >/dev/null || fail "python3 not found"

TS="$(date +%Y%m%d-%H%M%S)"
DIAG_DIR="data/workspace-provenance/diagnostics"
REPORT_DIR="reports/workspace-provenance"

mkdir -p "$DIAG_DIR" "$REPORT_DIR"

INVENTORY="$DIAG_DIR/showtrials_workspace_inventory_${TS}.tsv"
ROOTS="$DIAG_DIR/showtrials_workspace_roots_${TS}.tsv"
DUPLICATES="$DIAG_DIR/showtrials_workspace_duplicates_${TS}.tsv"
NAME_CONFLICTS="$DIAG_DIR/showtrials_workspace_name_conflicts_${TS}.tsv"
GIT_EVIDENCE="$DIAG_DIR/showtrials_workspace_git_evidence_${TS}.tsv"
REPORT="$REPORT_DIR/showtrials_workspace_provenance_report_${TS}.txt"

python3 - "$ROOT" "$INVENTORY" "$ROOTS" "$DUPLICATES" "$NAME_CONFLICTS" "$GIT_EVIDENCE" "$REPORT" <<'PY'
from __future__ import annotations

import csv
import hashlib
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
inventory_path = Path(sys.argv[2])
roots_path = Path(sys.argv[3])
duplicates_path = Path(sys.argv[4])
name_conflicts_path = Path(sys.argv[5])
git_evidence_path = Path(sys.argv[6])
report_path = Path(sys.argv[7])

roots = [
    ("showtrials_project", repo_root),
    ("russian_archives_discovery", Path("/srv/projects/russian-archives-discovery")),
    ("local_process_dossiers", repo_root / "local" / "process-dossiers"),
    ("data_t_translation_assets", repo_root / "data" / "t-translation-assets"),
    ("reports_t_translation_assets", repo_root / "reports" / "t-translation-assets"),
    ("scripts_t_translation_assets", repo_root / "scripts" / "t-translation-assets"),
    ("data_perpetrator2004", repo_root / "data" / "perpetrator2004"),
    ("reports_perpetrator2004", repo_root / "reports" / "perpetrator2004"),
    ("scripts_perpetrator2004", repo_root / "scripts" / "perpetrator2004"),
    ("data_process_dossiers", repo_root / "data" / "process-dossiers"),
    ("reports_process_dossiers", repo_root / "reports" / "process-dossiers"),
    ("scripts_process_dossiers", repo_root / "scripts" / "process-dossiers"),
    ("toolbox_shared_showtrials", Path("/srv/toolbox/shared/showtrials")),
    ("toolbox_shared_showtrials_review", Path("/srv/toolbox/shared/showtrials-review")),
]

git_repos = [
    ("showtrials-discovery", repo_root),
    ("russian-archives-discovery", Path("/srv/projects/russian-archives-discovery")),
]

git_terms = [
    "showtrials",
    "translation",
    "translation-assets",
    "t-translation-assets",
    "process-dossiers",
    "dossier",
    "perpetrator",
    "narod",
    "russian-archives",
    "chunk",
    "semantic",
    "glossary",
    "structural",
]
term_re = re.compile("|".join(re.escape(t) for t in git_terms), re.IGNORECASE)

skip_dir_names = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
}

text_suffixes = {".md", ".txt", ".tsv", ".csv", ".json", ".jsonl", ".html", ".htm", ".xml", ".log", ".sh", ".py", ".yml", ".yaml"}
binary_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".tar", ".gz", ".zip", ".xz", ".bz2", ".7z"}

def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    return p.returncode, p.stdout, p.stderr

def tsv_write(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: "" if row.get(k) is None else row.get(k) for k in fieldnames})

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def git_root(path: Path) -> str:
    if not path.exists():
        return ""
    target = path if path.is_dir() else path.parent
    code, out, _ = run(["git", "-C", str(target), "rev-parse", "--show-toplevel"])
    if code == 0:
        return out.strip()
    return ""

def is_git_repo(path: Path) -> str:
    if not path.exists() or not path.is_dir():
        return "no"
    code, out, _ = run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"])
    return "yes" if code == 0 and out.strip() == "true" else "no"

def ignored_by_showtrials_git(path: Path) -> str:
    try:
        resolved = path.resolve()
    except FileNotFoundError:
        resolved = path
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        return "not_applicable"
    code, _, _ = run(["git", "-C", str(repo_root), "check-ignore", "-q", str(resolved)])
    if code == 0:
        return "yes"
    if code == 1:
        return "no"
    return "unknown"

def should_skip_dir(path: Path) -> bool:
    return path.name in skip_dir_names

def iter_entries(root: Path):
    if not root.exists():
        return
    yield root
    if root.is_file():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in skip_dir_names]
        base = Path(dirpath)
        for d in dirnames:
            yield base / d
        for name in sorted(filenames):
            yield base / name

def file_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix in {".txt", ".text"}:
        return "text"
    if suffix in {".tsv", ".csv"}:
        return "table"
    if suffix in {".json", ".jsonl"}:
        return "json"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".log":
        return "log"
    if suffix in {".sh", ".py"}:
        return "script"
    if suffix in binary_suffixes:
        return "binary"
    return suffix[1:] if suffix else "no_ext"

def read_head(path: Path, limit: int = 8192) -> str:
    if path.is_dir() or path.suffix.lower() not in text_suffixes:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""

def classify(label: str, root: Path, path: Path) -> tuple[str, str, str]:
    rel = "" if path == root else str(path.relative_to(root))
    hay = " ".join([label, str(root), rel, path.name, read_head(path)]).lower()
    suffix = path.suffix.lower()

    def hit(words: list[str]) -> bool:
        return any(w in hay for w in words)

    if path.name.lower() in {"readme.md", "readme.txt"} or label.startswith("reports_") or "/reports/" in str(path).lower() or suffix in {".log"}:
        if suffix in {".sh", ".py"}:
            pass
        elif "report" in hay or label.startswith("reports_") or suffix in {".log"}:
            return "report", "0.88", "report/readme/log path or content"
    if label.startswith("scripts_") or suffix in {".sh", ".py"}:
        return "script", "0.95", "script directory or executable suffix"
    if "perpetrator2004" in hay or "narod" in hay:
        return "perpetrator2004_source", "0.94", "perpetrator2004/narod marker"
    if "local/process-dossiers" in str(path).lower() or label == "local_process_dossiers":
        return "legacy_snapshot", "0.91", "local/process-dossiers is gitignored local snapshot"
    if hit(["process-dossiers", "process dossier", "dossi", "dossier", "resumo.md"]):
        return "process_dossier", "0.90", "dossier marker"
    if hit(["translation-assets", "t-translation-assets", "moscow trials", "ezhov", "parallel", "translation", "glossary", "marxists.org", "mia"]):
        return "translation_asset", "0.86", "translation/corpus control marker"
    if "russian-archives-discovery" in hay:
        return "external_discovery", "0.91", "external russian-archives-discovery project marker"
    if hit(["structural", "structural_samples", "selected batch", "review"]):
        return "structural_review", "0.82", "structural/review marker"
    if hit(["semantic", "entity", "person", "organization", "canonical"]):
        return "semantic_layer", "0.78", "semantic/entity marker"
    if hit(["chunkbuilder", "chunking", "chunk"]):
        return "chunkbuilder_related", "0.78", "chunk/chunking marker"
    if suffix in {".html", ".htm", ".pdf"} or hit(["raw", "mirror", "source text", "original"]):
        return "raw_source_text", "0.70", "raw/source text marker"
    if suffix == ".txt" or hit(["extracted", "ocr", "pdf-text"]):
        return "extracted_text", "0.70", "text extraction marker"
    if suffix in {".tmp", ".bak", ".swp", ".log"} or hit(["checkpoint", "backup", "cache"]):
        return "temporary_or_log", "0.70", "temporary/log marker"
    if "showtrials" in hay:
        return "showtrials_core", "0.60", "showtrials marker"
    return "unknown", "0.30", "no strong provenance marker"

def infer_role(label: str, path: Path, file_count: int) -> tuple[str, str]:
    low = f"{label} {path}".lower()
    if not path.exists():
        return "missing", "path does not exist"
    if label == "toolbox_shared_showtrials":
        return "structural_review", "historical shared showtrials front; likely selected structural review batches/checkpoints"
    if label == "toolbox_shared_showtrials_review":
        return "translation_asset", "broader shared review workspace with Moscow Trials, extracted text, reports, and translation-assets"
    if label == "local_process_dossiers":
        return "legacy_snapshot", "gitignored local/process-dossiers snapshot"
    if "translation" in low:
        return "translation_asset", "translation-assets project area"
    if "perpetrator2004" in low:
        return "perpetrator2004_source", "autonomous perpetrator2004 corpus area"
    if "process-dossiers" in low:
        return "process_dossier", "process dossier diagnostics/reports/scripts area"
    if "russian-archives-discovery" in low:
        return "external_discovery", "separate multi-source discovery/deduplication project"
    if label == "showtrials_project":
        return "showtrials_core", "main showtrials-discovery repository"
    return "unknown", f"files={file_count}"

def root_stats(root: Path) -> tuple[int, int]:
    if not root.exists():
        return 0, 0
    if root.is_file():
        try:
            return 1, root.stat().st_size
        except OSError:
            return 0, 0
    count = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dir_names]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                st = p.stat()
            except OSError:
                continue
            count += 1
            total += st.st_size
    return count, total

inventory_rows: list[dict[str, object]] = []
root_rows: list[dict[str, object]] = []

seen_root_paths: set[str] = set()
for label, root in roots:
    root = root.resolve() if root.exists() else root
    if str(root) in seen_root_paths:
        continue
    seen_root_paths.add(str(root))
    file_count, total_bytes = root_stats(root)
    role, notes = infer_role(label, root, file_count)
    root_rows.append({
        "root_label": label,
        "root_path": str(root),
        "exists": "yes" if root.exists() else "no",
        "git_root": git_root(root),
        "is_git_repo": is_git_repo(root),
        "ignored_by_showtrials_git": ignored_by_showtrials_git(root),
        "file_count": file_count,
        "total_bytes": total_bytes,
        "inferred_role": role,
        "notes": notes,
    })
    if not root.exists():
        continue
    if label == "showtrials_project":
        continue
    for path in iter_entries(root):
        try:
            st = path.stat()
        except OSError:
            continue
        try:
            rel = "." if path == root else str(path.relative_to(root))
        except ValueError:
            rel = str(path)
        kind = file_kind(path)
        digest = ""
        if path.is_file():
            try:
                digest = sha256_file(path)
            except OSError as exc:
                digest = f"ERROR:{type(exc).__name__}"
        inferred_class, confidence, reason = classify(label, root, path)
        inventory_rows.append({
            "root_label": label,
            "root_path": str(root),
            "relpath": rel,
            "abs_path": str(path),
            "kind": kind,
            "suffix": path.suffix.lower(),
            "size_bytes": st.st_size if path.is_file() else "",
            "mtime_epoch": int(st.st_mtime),
            "sha256": digest,
            "inferred_class": inferred_class,
            "confidence": confidence,
            "reason": reason,
        })

duplicate_rows: list[dict[str, object]] = []
by_hash_base: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
by_hash: dict[str, list[dict[str, object]]] = defaultdict(list)
by_base: dict[str, list[dict[str, object]]] = defaultdict(list)
for row in inventory_rows:
    digest = str(row["sha256"])
    if not digest or digest.startswith("ERROR:"):
        continue
    basename = Path(str(row["abs_path"])).name
    by_hash_base[(digest, basename)].append(row)
    by_hash[digest].append(row)
    by_base[basename].append(row)

group_id = 0
for (digest, basename), rows_for_key in sorted(by_hash_base.items()):
    if len(rows_for_key) < 2:
        continue
    group_id += 1
    roots_seen = sorted({str(r["root_label"]) for r in rows_for_key})
    for r in rows_for_key:
        duplicate_rows.append({
            "duplicate_group": f"dup_{group_id:05d}",
            "sha256": digest,
            "basename": basename,
            "root_label": r["root_label"],
            "relpath": r["relpath"],
            "abs_path": r["abs_path"],
            "size_bytes": r["size_bytes"],
            "roots_seen": ",".join(roots_seen),
        })

name_conflict_rows: list[dict[str, object]] = []
conflict_id = 0
interesting_names = {"resumo.md", "readme.md", "readme.txt"}
for basename, rows_for_base in sorted(by_base.items()):
    hashes = sorted({str(r["sha256"]) for r in rows_for_base if str(r["sha256"])})
    lower = basename.lower()
    interesting = lower in interesting_names or bool(re.search(r"(dossier|dossie|process|resumo|readme|\d{2,})", lower))
    if len(hashes) < 2 or not interesting:
        continue
    conflict_id += 1
    for r in rows_for_base:
        name_conflict_rows.append({
            "conflict_group": f"name_{conflict_id:05d}",
            "basename": basename,
            "sha256": r["sha256"],
            "root_label": r["root_label"],
            "relpath": r["relpath"],
            "abs_path": r["abs_path"],
            "size_bytes": r["size_bytes"],
            "mtime_epoch": r["mtime_epoch"],
        })

def parse_git_log(repo_label: str, repo_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not repo_path.exists():
        rows.append({
            "repo": repo_label,
            "command": "repo_exists",
            "commit": "",
            "date": "",
            "subject": "",
            "path_hint": str(repo_path),
            "relevance": "missing",
        })
        return rows

    status_code, status_out, status_err = run(["git", "-C", str(repo_path), "status", "--short"])
    rows.append({
        "repo": repo_label,
        "command": "git status --short",
        "commit": "",
        "date": "",
        "subject": (status_out.strip() or "clean")[:500],
        "path_hint": "",
        "relevance": "status" if status_code == 0 else f"error:{status_err.strip()[:200]}",
    })

    tags_code, tags_out, tags_err = run(["git", "-C", str(repo_path), "tag", "--list"])
    tags = [t for t in tags_out.splitlines() if term_re.search(t)]
    rows.append({
        "repo": repo_label,
        "command": "git tag --list",
        "commit": "",
        "date": "",
        "subject": "; ".join(tags[:50]) if tags else "",
        "path_hint": "",
        "relevance": "matching_tags" if tags_code == 0 and tags else ("no_matching_tags" if tags_code == 0 else f"error:{tags_err.strip()[:200]}"),
    })

    fmt = "--format=COMMIT%x09%H%x09%ad%x09%s"
    code, out, err = run(["git", "-C", str(repo_path), "log", "--all", "--name-status", "--date=iso", fmt])
    if code != 0:
        rows.append({
            "repo": repo_label,
            "command": "git log --all --name-status --date=iso",
            "commit": "",
            "date": "",
            "subject": "",
            "path_hint": "",
            "relevance": f"error:{err.strip()[:300]}",
        })
        return rows

    current = {"commit": "", "date": "", "subject": ""}
    pending_paths: list[str] = []
    for line in out.splitlines() + ["COMMIT\tEND\t\t"]:
        if line.startswith("COMMIT\t"):
            if current["commit"] and (term_re.search(current["subject"]) or any(term_re.search(p) for p in pending_paths)):
                matched = [p for p in pending_paths if term_re.search(p)]
                rows.append({
                    "repo": repo_label,
                    "command": "git log --all --name-status --date=iso",
                    "commit": current["commit"],
                    "date": current["date"],
                    "subject": current["subject"],
                    "path_hint": "; ".join(matched[:30]),
                    "relevance": "matched_subject_or_path",
                })
            parts = line.split("\t", 3)
            if len(parts) == 4:
                current = {"commit": parts[1], "date": parts[2], "subject": parts[3]}
            pending_paths = []
            continue
        if not line.strip():
            continue
        bits = line.split("\t")
        if len(bits) >= 2:
            pending_paths.append("\t".join(bits[1:]))
    return rows

git_rows: list[dict[str, object]] = []
for repo_label, repo_path in git_repos:
    git_rows.extend(parse_git_log(repo_label, repo_path))

inventory_fields = [
    "root_label",
    "root_path",
    "relpath",
    "abs_path",
    "kind",
    "suffix",
    "size_bytes",
    "mtime_epoch",
    "sha256",
    "inferred_class",
    "confidence",
    "reason",
]
root_fields = [
    "root_label",
    "root_path",
    "exists",
    "git_root",
    "is_git_repo",
    "ignored_by_showtrials_git",
    "file_count",
    "total_bytes",
    "inferred_role",
    "notes",
]
duplicate_fields = ["duplicate_group", "sha256", "basename", "root_label", "relpath", "abs_path", "size_bytes", "roots_seen"]
conflict_fields = ["conflict_group", "basename", "sha256", "root_label", "relpath", "abs_path", "size_bytes", "mtime_epoch"]
git_fields = ["repo", "command", "commit", "date", "subject", "path_hint", "relevance"]

tsv_write(inventory_path, inventory_rows, inventory_fields)
tsv_write(roots_path, root_rows, root_fields)
tsv_write(duplicates_path, duplicate_rows, duplicate_fields)
tsv_write(name_conflicts_path, name_conflict_rows, conflict_fields)
tsv_write(git_evidence_path, git_rows, git_fields)

class_counts = Counter(str(r["inferred_class"]) for r in inventory_rows)
root_role_counts = Counter(str(r["inferred_role"]) for r in root_rows)

def top_examples(class_name: str, limit: int = 8) -> list[str]:
    values = []
    for row in inventory_rows:
        if row["inferred_class"] == class_name and row["kind"] != "directory":
            values.append(str(row["abs_path"]))
    return values[:limit]

def root_note(label: str) -> str:
    for row in root_rows:
        if row["root_label"] == label:
            return f"{row['exists']}; files={row['file_count']}; role={row['inferred_role']}; {row['notes']}"
    return "not inspected"

report_lines = [
    "ShowTrials Workspace Provenance Diagnostic Report",
    f"Generated from {repo_root}",
    "",
    "Resumo executivo",
    f"- Inventory rows: {len(inventory_rows)} across {len(root_rows)} roots.",
    f"- Duplicate hash+basename rows: {len(duplicate_rows)}.",
    f"- Name conflict rows: {len(name_conflict_rows)}.",
    f"- Git evidence rows: {len(git_rows)}.",
    "- This is diagnostic only: no files were moved, copied, deleted, reclassified in place, committed, or ignored.",
    "- Current evidence supports treating process dossiers, translation assets, perpetrator2004, and russian-archives-discovery as related but distinct provenance classes until human review.",
    "",
    "O que é /srv/toolbox/shared/showtrials",
    f"- Root evidence: {root_note('toolbox_shared_showtrials')}.",
    "- Inference: likely an earlier structural review / selected batch workspace. The presence of checkpoints and showtrials naming indicates historical review material rather than the canonical current corpus.",
    "",
    "O que é /srv/toolbox/shared/showtrials-review",
    f"- Root evidence: {root_note('toolbox_shared_showtrials_review')}.",
    "- Inference: broader and later review/extraction/curation workspace. Moscow Trials PDFs/text/reports and translation-assets point to mixed corpus support and review activity.",
    "",
    "O que é translation-assets",
    f"- Related roots: {root_note('data_t_translation_assets')} | {root_note('reports_t_translation_assets')} | {root_note('scripts_t_translation_assets')}.",
    "- Inference: translation-assets is a control/parallel corpus and auxiliary-source area, including Moscow Trials EN, Ezhov-related assets, MIA/precursor sites, extraction targets, and reports/scripts.",
    "",
    "O que são os dossiês markdown",
    "- Inference: markdown dossiers are a study/interpretive process-dossier layer, not primary translation assets. Same-name markdown conflicts, especially resumo.md or numbered dossiers if present, require review before any consolidation.",
    "",
    "O que é local/process-dossiers",
    f"- Root evidence: {root_note('local_process_dossiers')}.",
    f"- Gitignore evidence: {ignored_by_showtrials_git(repo_root / 'local' / 'process-dossiers')} for local/process-dossiers.",
    "- Inference: legacy local snapshot under gitignored local/. It should be treated as provenance evidence and not as canonical tracked data without manual review.",
    "",
    "O que é perpetrator2004 dentro de showtrials-discovery",
    f"- Related roots: {root_note('data_perpetrator2004')} | {root_note('reports_perpetrator2004')} | {root_note('scripts_perpetrator2004')}.",
    "- Inference: perpetrator2004 may have begun as a precursor/translation asset, but current repository organization supports treating it as an autonomous source corpus with its own data, reports, and scripts.",
    "",
    "Relação com russian-archives-discovery",
    f"- Root evidence: {root_note('russian_archives_discovery')}.",
    "- Inference: russian-archives-discovery is a separate discovery/deduplication project. It can provide external comparison evidence, but should not become the canonical storage place for ShowTrials corpus payloads or study dossiers.",
    "",
    "Materiais possivelmente redundantes",
    f"- Duplicate rows are listed in {duplicates_path}.",
    f"- Name conflicts are listed in {name_conflicts_path}.",
    "- Redundancy should be evaluated by hash, basename, root role, and mtime together. Equal hashes are overlap evidence, not a deletion instruction.",
    "",
    "Materiais que não devem ser movidos ainda",
    "- Anything under local/process-dossiers, toolbox shared roots, translation-assets, perpetrator2004, and russian-archives-discovery should remain in place until a human validates the inferred role and conflict TSVs.",
    "- READMEs, reports, scripts, logs, and manifests are provenance evidence and should not be discarded during early cleanup.",
    "",
    "Proposta de taxonomia canônica futura",
    "- showtrials_core: canonical tracked ShowTrials corpus/project material.",
    "- translation_asset: parallel/control translation corpora and auxiliary precursor sources.",
    "- process_dossier: markdown study dossiers and derived dossier text.",
    "- perpetrator2004_source: autonomous perpetrator2004 source corpus, manifests, mirror diagnostics, and reports.",
    "- external_discovery: separate discovery/deduplication projects such as russian-archives-discovery.",
    "- structural_review, semantic_layer, chunkbuilder_related: analytical layers with separate ownership from source payloads.",
    "",
    "Riscos de migração",
    "- Same basenames with different hashes can represent revisions, unrelated files, or divergent dossier drafts.",
    "- local/ is intentionally ignored; promoting files from it may add stale snapshots if not compared against shared and tracked outputs.",
    "- Shared workspaces may contain mixed-purpose materials; directory ancestry alone is insufficient for final classification.",
    "- Git history can show naming and timing but does not prove conceptual ownership without content review.",
    "",
    "Próximos passos recomendados",
    "- Review this report and the four diagnostic TSVs manually.",
    "- Inspect name conflicts first, then duplicate groups that cross root boundaries.",
    "- Compare READMEs/reports/scripts with Git evidence to identify authoritative generation paths.",
    "- Decide canonical taxonomy and migration rules only after review; this script intentionally does not implement migration.",
    "",
    "Class counts",
]
for key, value in sorted(class_counts.items()):
    report_lines.append(f"- {key}: {value}")
report_lines.extend(["", "Root role counts"])
for key, value in sorted(root_role_counts.items()):
    report_lines.append(f"- {key}: {value}")
report_lines.extend(["", "Representative examples"])
for class_name in sorted(class_counts):
    examples = top_examples(class_name, 5)
    if not examples:
        continue
    report_lines.append(f"- {class_name}:")
    for ex in examples:
        report_lines.append(f"  - {ex}")
report_lines.extend(["", "Artifacts", f"- {inventory_path}", f"- {roots_path}", f"- {duplicates_path}", f"- {name_conflicts_path}", f"- {git_evidence_path}"])

report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

print(f"inventory_tsv={inventory_path}")
print(f"roots_tsv={roots_path}")
print(f"duplicates_tsv={duplicates_path}")
print(f"name_conflicts_tsv={name_conflicts_path}")
print(f"git_evidence_tsv={git_evidence_path}")
print(f"report={report_path}")
print(f"inventory_rows={len(inventory_rows)}")
print(f"roots={len(root_rows)}")
print(f"duplicate_rows={len(duplicate_rows)}")
print(f"name_conflict_rows={len(name_conflict_rows)}")
print(f"git_evidence_rows={len(git_rows)}")
for key, value in sorted(class_counts.items()):
    print(f"inferred_class.{key}={value}")
PY
