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

def script_path(phase: str, filename: str) -> Path:
    return scripts_dir(phase) / filename

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
DOCUMENT_COLLECTIONS_REPORT = report_path("c", "showtrials_document_collections_report.txt")

DOCUMENT_TYPE_V1_V2_CHANGES = data_path("c", "showtrials_document_type_v1_v2_changes.tsv")
DOCUMENT_TYPE_V1_V2_COMPARE_REPORT = report_path("c", "showtrials_document_type_v1_v2_compare_report.txt")
DOCUMENT_TYPE_V2_V3_CHANGES = data_path("c", "showtrials_document_type_v2_v3_changes.tsv")
DOCUMENT_TYPE_V2_V3_COMPARE_REPORT = report_path("c", "showtrials_document_type_v2_v3_compare_report.txt")
DOCUMENT_TYPE_V3_V4_CHANGES = data_path("c", "showtrials_document_type_v3_v4_changes.tsv")
DOCUMENT_TYPE_V3_V4_COMPARE_REPORT = report_path("c", "showtrials_document_type_v3_v4_compare_report.txt")

CATEGORIES_JSON = data_path("c", "showtrials_categories.json")
TAGS_JSON = data_path("c", "showtrials_tags.json")
AUTHOR_AUDIT = data_path("c", "showtrials_author_audit.tsv")
AUTHOR_AUDIT_REPORT = report_path("c", "showtrials_author_audit_report.txt")
CATEGORY_TREE = data_path("c", "showtrials_category_tree.tsv")
CATEGORY_TREE_REPORT = report_path("c", "showtrials_category_tree_report.txt")
COLLECTION_INVENTORY = data_path("c", "showtrials_collection_inventory.tsv")
CORPUS_AUDIT_DOCUMENTS = data_path("c", "showtrials_corpus_audit_documents.tsv")
CORPUS_AUDIT_SUMMARY = data_path("c", "showtrials_corpus_audit_summary.tsv")
CORPUS_AUDIT_REPORT = report_path("c", "showtrials_corpus_audit_report.txt")
CORPUS_INVENTORY_REPORT = report_path("c", "showtrials_corpus_inventory_report.txt")
CORPUS_LARGEST_DOCUMENTS = data_path("c", "showtrials_corpus_largest_documents.tsv")
CORPUS_SMALLEST_DOCUMENTS = data_path("c", "showtrials_corpus_smallest_documents.tsv")
CORPUS_STATISTICS_OVERVIEW = data_path("c", "showtrials_corpus_statistics_overview.tsv")
CORPUS_STATISTICS_BY_COLLECTION = data_path("c", "showtrials_corpus_statistics_by_collection.tsv")
CORPUS_STATISTICS_BY_TAG = data_path("c", "showtrials_corpus_statistics_by_tag.tsv")
CORPUS_STATISTICS_REPORT = report_path("c", "showtrials_corpus_statistics_report.txt")
DATES_BY_YEAR = data_path("c", "showtrials_dates_by_year.tsv")
DATES_BY_MONTH = data_path("c", "showtrials_dates_by_month.tsv")
DATE_OUTLIERS = data_path("c", "showtrials_date_outliers.tsv")
DATE_AUDIT_REPORT = report_path("c", "showtrials_date_audit_report.txt")
LARGEST_DOCUMENTS = data_path("c", "showtrials_largest_documents.tsv")
PAGE_HIERARCHY = data_path("c", "showtrials_page_hierarchy.tsv")
PAGE_HIERARCHY_REPORT = report_path("c", "showtrials_page_hierarchy_report.txt")
PAGE_LINKS = data_path("c", "showtrials_page_links.tsv")
PAGE_LINKS_REPORT = report_path("c", "showtrials_page_links_report.txt")
POST_METADATA_FIELDS = data_path("c", "showtrials_post_metadata_fields.tsv")
POST_METADATA_TERMS = data_path("c", "showtrials_post_metadata_terms.tsv")
POST_METADATA_SAMPLE = data_path("c", "showtrials_post_metadata_sample.tsv")
POST_METADATA_REPORT = report_path("c", "showtrials_post_metadata_report.txt")
TAXONOMY_ANOMALIES = data_path("c", "showtrials_taxonomy_anomalies.tsv")
TAXONOMY_DOCUMENT_MATRIX = data_path("c", "showtrials_taxonomy_document_matrix.tsv")
TAXONOMY_REPORT = report_path("c", "showtrials_taxonomy_report.txt")
TAXONOMY_TERMS_REPORT = report_path("c", "showtrials_taxonomy_terms_report.txt")
TEXT_CLEANLINESS = data_path("c", "showtrials_text_cleanliness.tsv")
TEXT_CLEANLINESS_REPORT = report_path("c", "showtrials_text_cleanliness_report.txt")
TIMELINE = data_path("c", "showtrials_timeline.tsv")

PROCESS_INVENTORY = data_path("e", "showtrials_process_inventory.tsv")
CORPUS_STATISTICS_BY_PROCESS = data_path("e", "showtrials_corpus_statistics_by_process.tsv")

SEARCH_V2_SCRIPT = script_path("b", "showtrials-search-v2.py")
SHOWTRIALS_HOST = "showtrials.ru"
SHOWTRIALS_HTTP = "http://" + SHOWTRIALS_HOST
SHOWTRIALS_HTTPS = "https://" + SHOWTRIALS_HOST
WP_USERS_ENDPOINT = SHOWTRIALS_HTTP + "/wp-json/wp/v2/users?per_page=100&page=1"
WP_CATEGORIES_ENDPOINT = SHOWTRIALS_HTTP + "/wp-json/wp/v2/categories?per_page=100&page=1"
WP_TAGS_ENDPOINT = SHOWTRIALS_HTTP + "/wp-json/wp/v2/tags?per_page=100&page=1"

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
PAGES_PAGE_1_JSON = PAGES_JSON_DIR / "pages-page-1.json"

ENTITY_PROCESSES = data_path("e", "showtrials_entities_processes.tsv")
ENTITY_COLLECTIONS = data_path("e", "showtrials_entities_collections.tsv")
ENTITY_CATEGORIES = data_path("e", "showtrials_entities_categories.tsv")
ENTITY_TAGS = data_path("e", "showtrials_entities_tags.tsv")
ENTITY_CANDIDATES = data_path("e", "showtrials_entity_candidates.tsv")
TITLE_DOCUMENT_ENTITIES = data_path("e", "showtrials_title_document_entities.tsv")
TITLE_ENTITY_PAIRS = data_path("e", "showtrials_title_entity_pairs.tsv")
PEOPLE = data_path("e", "showtrials_people.tsv")
PEOPLE_INDEX_REPORT = report_path("e", "showtrials_people_index_report.txt")
PERSON_DOCUMENTS = data_path("e", "showtrials_person_documents.tsv")
PERSON_PAIRS = data_path("e", "showtrials_person_pairs.tsv")
PERSON_NORMALIZATION_CANDIDATES = data_path("e", "showtrials_person_normalization_candidates.tsv")
PERSON_NORMALIZATION_REPORT = report_path("e", "showtrials_person_normalization_report.txt")
CANONICAL_PEOPLE = data_path("e", "showtrials_canonical_people.tsv")
CANONICAL_PEOPLE_REPORT = report_path("e", "showtrials_canonical_people_report.txt")
CANONICAL_PERSON_DOCUMENTS = data_path("e", "showtrials_canonical_person_documents.tsv")
CANONICAL_PERSON_PAIRS = data_path("e", "showtrials_canonical_person_pairs.tsv")
LITERAL_PEOPLE = data_path("e", "showtrials_literal_people.tsv")
LITERAL_PEOPLE_REPORT = report_path("e", "showtrials_literal_people_report.txt")
LITERAL_PERSON_DOCUMENTS = data_path("e", "showtrials_literal_person_documents.tsv")
LITERAL_PERSON_PAIRS = data_path("e", "showtrials_literal_person_pairs.tsv")
ORGANIZATIONS = data_path("e", "showtrials_organizations.tsv")
ORGANIZATIONS_REPORT = report_path("e", "showtrials_organizations_report.txt")
ORGANIZATION_DOCUMENTS = data_path("e", "showtrials_organization_documents.tsv")
PERSON_ORGANIZATION_PAIRS = data_path("e", "showtrials_person_organization_pairs.tsv")
ORGANIZATION_FAMILIES = data_path("e", "showtrials_organization_families.tsv")
ORGANIZATION_FAMILIES_REPORT = report_path("e", "showtrials_organization_families_report.txt")
ORGANIZATION_FAMILIES_VALIDATION_REPORT = report_path("e", "showtrials_organization_families_validation_report.txt")
ORGANIZATION_FAMILY_DOCUMENT_MATRIX = data_path("e", "showtrials_organization_family_document_matrix.tsv")
ORGANIZATION_FAMILY_DOCUMENT_MATRIX_REPORT = report_path("e", "showtrials_organization_family_document_matrix_report.txt")
ORGANIZATION_FAMILY_DOCUMENT_SUMMARY = data_path("e", "showtrials_organization_family_document_summary.tsv")
ORGANIZATION_FAMILY_CROSSPAIRS = data_path("e", "showtrials_organization_family_crosspairs.tsv")
ORGANIZATION_HIERARCHY = data_path("e", "showtrials_organization_hierarchy.tsv")
ORGANIZATION_HIERARCHY_REPORT = report_path("e", "showtrials_organization_hierarchy_report.txt")
ORGANIZATION_HIERARCHY_REVIEW = data_path("e", "showtrials_organization_hierarchy_review.tsv")
ORGANIZATION_HIERARCHY_VALIDATION = data_path("e", "showtrials_organization_hierarchy_validation.tsv")
ORGANIZATION_HIERARCHY_VALIDATION_REPORT = report_path("e", "showtrials_organization_hierarchy_validation_report.txt")
PERSON_ALIASES = data_path("e", "showtrials_person_aliases.tsv")
PERSON_ALIASES_REPORT = report_path("e", "showtrials_person_aliases_report.txt")
PERSON_ALIASES_MANUAL = data_path("e", "showtrials_person_aliases_manual.tsv")
PERSON_ALIASES_REVIEWED = data_path("e", "showtrials_person_aliases_reviewed.tsv")
PERSON_ALIASES_REVIEWED_REPORT = report_path("e", "showtrials_person_aliases_reviewed_report.txt")
PERSON_MERGE_CANDIDATES = data_path("e", "showtrials_person_merge_candidates.tsv")
PERSON_MERGE_CANDIDATES_REPORT = report_path("e", "showtrials_person_merge_candidates_report.txt")
PERSON_ORGANIZATION_SUMMARY = data_path("e", "showtrials_person_organization_summary.tsv")
PERSON_PROCESS_MATRIX = data_path("e", "showtrials_person_process_matrix.tsv")
PROCESSES = data_path("e", "showtrials_processes.tsv")
ROLES_V2 = data_path("e", "showtrials_roles_v2.tsv")
ROLE_DOCUMENTS_V2 = data_path("e", "showtrials_role_documents_v2.tsv")
TRUNCATED_PERSON_CANDIDATES = data_path("e", "showtrials_truncated_person_candidates.tsv")
TRUNCATED_PERSON_CANDIDATES_REPORT = report_path("e", "showtrials_truncated_person_candidates_report.txt")
TRUNCATED_PERSON_REVIEW = data_path("e", "showtrials_truncated_person_review.tsv")
UNMERGED_PERSONS = data_path("e", "showtrials_unmerged_persons.tsv")
UNMERGED_PERSONS_REPORT = report_path("e", "showtrials_unmerged_persons_report.txt")

TRANSLATION_GLOSSARY_SEEDS_V1 = data_path("g", "showtrials_translation_glossary_seeds_v1.tsv")
TRANSLATION_GLOSSARY_SEEDS_V1_REPORT = report_path("g", "showtrials_translation_glossary_seeds_v1_report.txt")
TRANSLATION_GLOSSARY_SEEDS_V1_VALIDATION_REPORT = report_path("g", "showtrials_translation_glossary_seeds_v1_validation_report.txt")
TRANSLATION_GLOSSARY_V1 = data_path("g", "showtrials_translation_glossary_v1.tsv")
TRANSLATION_GLOSSARY_V1_REVIEW = data_path("g", "showtrials_translation_glossary_v1_review.tsv")
TRANSLATION_GLOSSARY_V1_REPORT = report_path("g", "showtrials_translation_glossary_v1_report.txt")
TRANSLATION_GLOSSARY_V1_VALIDATION_REPORT = report_path("g", "showtrials_translation_glossary_v1_validation_report.txt")
TRANSLATION_GLOSSARY_G3 = data_path("g", "showtrials_translation_glossary_g3.tsv")
TRANSLATION_GLOSSARY_G3_REVIEW = data_path("g", "showtrials_translation_glossary_g3_review.tsv")
TRANSLATION_GLOSSARY_G3_REPORT = report_path("g", "showtrials_translation_glossary_g3_report.txt")
TRANSLATION_GLOSSARY_G3_VALIDATION = data_path("g", "showtrials_translation_glossary_g3_validation.tsv")
TRANSLATION_GLOSSARY_G3_VALIDATION_REPORT = report_path("g", "showtrials_translation_glossary_g3_validation_report.txt")
TRANSLATION_GLOSSARY_G4 = data_path("g", "showtrials_translation_glossary_g4.tsv")
TRANSLATION_GLOSSARY_G4_REVIEW = data_path("g", "showtrials_translation_glossary_g4_review.tsv")
TRANSLATION_GLOSSARY_G4_REPORT = report_path("g", "showtrials_translation_glossary_g4_report.txt")
TRANSLATION_GLOSSARY_G4_1 = data_path("g", "showtrials_translation_glossary_g4_1.tsv")
TRANSLATION_GLOSSARY_G4_1_REVIEW = data_path("g", "showtrials_translation_glossary_g4_1_review.tsv")
TRANSLATION_GLOSSARY_G4_1_REPORT = report_path("g", "showtrials_translation_glossary_g4_1_report.txt")
TRANSLATION_GLOSSARY_G4_1_VALIDATION = data_path("g", "showtrials_translation_glossary_g4_1_validation.tsv")
TRANSLATION_GLOSSARY_G4_1_VALIDATION_REPORT = report_path("g", "showtrials_translation_glossary_g4_1_validation_report.txt")
TRANSLATION_GLOSSARY_FREEZE_READINESS = data_path("g", "showtrials_translation_glossary_freeze_readiness.tsv")
TRANSLATION_GLOSSARY_FREEZE_READINESS_REPORT = report_path("g", "showtrials_translation_glossary_freeze_readiness_report.txt")
GOOGLE_TRANSLATE_GLOSSARY_RU_EN_V1 = data_path("g", "showtrials_google_translate_glossary_ru_en_v1.tsv")

TRANSLATION_COST_BY_DOCUMENT = data_path("t", "showtrials_translation_cost_by_document.tsv")
TRANSLATION_COST_BY_DOCUMENT_TYPE = data_path("t", "showtrials_translation_cost_by_document_type.tsv")
TRANSLATION_COST_BY_PROCESS = data_path("t", "showtrials_translation_cost_by_process.tsv")
TRANSLATION_COST_REPORT = report_path("t", "showtrials_translation_cost_report.txt")
TRANSLATION_PROFILES_V1 = data_path("t", "showtrials_translation_profiles_v1.tsv")
TRANSLATION_PROFILES_V1_REPORT = report_path("t", "showtrials_translation_profiles_v1_report.txt")
TRANSLATION_GLOSSARY_SEED_PLAN_V1 = data_path("t", "showtrials_translation_glossary_seed_plan_v1.tsv")
