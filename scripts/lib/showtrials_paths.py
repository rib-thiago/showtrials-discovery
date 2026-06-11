#!/usr/bin/env python3
"""Central path registry for ShowTrials Discovery."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DOCS_DIR = PROJECT_ROOT / "docs"
LOCAL_DIR = PROJECT_ROOT / "local"

PHASE_DIRS = {
    "a": "a-extraction",
    "b": "b-json-export-search",
    "c": "c-catalog-taxonomy",
    "d": "d-structural-chunking",
    "e": "e-semantic-layer",
    "g": "g-glossary",
    "t": "t-translation-planning",
    "r": "r-governance",
}

def phase_slug(phase: str) -> str:
    key = phase.strip().lower()
    if key not in PHASE_DIRS:
        raise KeyError(f"Unknown phase: {phase}")
    return PHASE_DIRS[key]

def data_dir(phase: str) -> Path:
    return DATA_DIR / phase_slug(phase)

def reports_dir(phase: str) -> Path:
    return REPORTS_DIR / phase_slug(phase)

def scripts_dir(phase: str) -> Path:
    return SCRIPTS_DIR / phase_slug(phase)

def data_path(phase: str, filename: str) -> Path:
    return data_dir(phase) / filename

def report_path(phase: str, filename: str) -> Path:
    return reports_dir(phase) / filename

def local_path(*parts: str) -> Path:
    return LOCAL_DIR.joinpath(*parts)

def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path

def require_dir(path: Path) -> Path:
    if not path.is_dir():
        raise FileNotFoundError(path)
    return path
