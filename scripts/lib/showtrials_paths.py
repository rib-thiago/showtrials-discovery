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

# Common artifacts used by B — JSON Corpus, Text Export, And Local Search.
MASTER_CATALOG = data_path("c", "showtrials_master_catalog.tsv")
MASTER_CATALOG_REPORT = report_path("c", "showtrials_master_catalog_report.txt")
DOCUMENT_INDEX = data_path("c", "showtrials_document_index.tsv")
DOCUMENT_INDEX_REPORT = report_path("c", "showtrials_document_index_report.txt")

DOCUMENT_TYPES = data_path("c", "showtrials_document_types.tsv")
DOCUMENT_TYPES_REPORT = report_path("c", "showtrials_document_types_report.txt")
DOCUMENT_TYPE_SUMMARY = data_path("c", "showtrials_document_type_summary.tsv")

DOCUMENT_TYPES_V2 = data_path("c", "showtrials_document_types_v2.tsv")
DOCUMENT_TYPES_V2_REPORT = report_path("c", "showtrials_document_types_v2_report.txt")
DOCUMENT_TYPE_SUMMARY_V2 = data_path("c", "showtrials_document_type_summary_v2.tsv")
DOCUMENT_TYPE_UNKNOWN_PREFIXES_V2 = data_path("c", "showtrials_document_type_unknown_prefixes_v2.tsv")
DOCUMENT_TYPES_V2_VALIDATION = data_path("c", "showtrials_document_types_v2_validation.tsv")
DOCUMENT_TYPES_V2_VALIDATION_REPORT = report_path("c", "showtrials_document_types_v2_validation_report.txt")

DOCUMENT_TYPES_V3 = data_path("c", "showtrials_document_types_v3.tsv")
DOCUMENT_TYPES_V3_REPORT = report_path("c", "showtrials_document_types_v3_report.txt")
DOCUMENT_TYPE_SUMMARY_V3 = data_path("c", "showtrials_document_type_summary_v3.tsv")
DOCUMENT_TYPE_UNKNOWN_PREFIXES_V3 = data_path("c", "showtrials_document_type_unknown_prefixes_v3.tsv")
DOCUMENT_TYPES_V3_VALIDATION = data_path("c", "showtrials_document_types_v3_validation.tsv")
DOCUMENT_TYPES_V3_VALIDATION_REPORT = report_path("c", "showtrials_document_types_v3_validation_report.txt")

DOCUMENT_TYPES_V4 = data_path("c", "showtrials_document_types_v4.tsv")
DOCUMENT_TYPES_V4_REPORT = report_path("c", "showtrials_document_types_v4_report.txt")
DOCUMENT_TYPE_SUMMARY_V4 = data_path("c", "showtrials_document_type_summary_v4.tsv")
DOCUMENT_TYPE_UNKNOWN_PREFIXES_V4 = data_path("c", "showtrials_document_type_unknown_prefixes_v4.tsv")
DOCUMENT_TYPES_V4_VALIDATION = data_path("c", "showtrials_document_types_v4_validation.tsv")
DOCUMENT_TYPES_V4_VALIDATION_REPORT = report_path("c", "showtrials_document_types_v4_validation_report.txt")

TAXONOMY_TERMS = data_path("c", "showtrials_taxonomy_terms.tsv")
DOCUMENT_COLLECTIONS = data_path("c", "showtrials_document_collections.tsv")

SEARCH_CORPUS = local_path("showtrials_search_corpus.tsv")
SEARCH_CORPUS_REPORT = report_path("b", "showtrials_search_corpus_report.txt")
SEARCH_V2_VALIDATION = data_path("b", "showtrials_search_v2_validation.tsv")
SEARCH_V2_VALIDATION_REPORT = report_path("b", "showtrials_search_v2_validation_report.txt")
USERS_JSON = data_path("b", "showtrials_users.json")

EXPORT_TXT_DIR = local_path("export-txt")
EXPORT_MD_DIR = local_path("export-md")
PAGES_JSON_DIR = local_path("pages-json")
POSTS_JSON_DIR = local_path("posts-json")
POSTS_JSON_EMBED_DIR = local_path("posts-json-embed")

ENTITY_PROCESSES = data_path("e", "showtrials_entities_processes.tsv")
ENTITY_COLLECTIONS = data_path("e", "showtrials_entities_collections.tsv")
ENTITY_CATEGORIES = data_path("e", "showtrials_entities_categories.tsv")
ENTITY_TAGS = data_path("e", "showtrials_entities_tags.tsv")
LITERAL_PERSON_DOCUMENTS = data_path("e", "showtrials_literal_person_documents.tsv")
ORGANIZATION_DOCUMENTS = data_path("e", "showtrials_organization_documents.tsv")
ORGANIZATION_FAMILY_DOCUMENT_MATRIX = data_path("e", "showtrials_organization_family_document_matrix.tsv")
ROLE_DOCUMENTS_V2 = data_path("e", "showtrials_role_documents_v2.tsv")
