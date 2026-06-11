# Artifact Inventory

## Purpose

This document explains the major artifact families that exist in the ShowTrials Discovery repository.

The repository contains a large number of generated files, reports, validations, inventories, matrices, and planning artifacts.

Not every file needs to be understood individually.

Most artifacts belong to a small number of documentary families.

This document serves as a map of the repository.

---

# Repository Philosophy

The repository follows an evidence-first workflow.

Most artifacts belong to one of four categories:

1. Discovery
2. Planning
3. Validation
4. Policy

A typical workflow looks like:

Discovery → Plan → Validate → Policy

For example:

* discover document structure;
* create a chunking blueprint;
* validate the blueprint;
* publish chunking policy.

This pattern appears repeatedly throughout the repository.

---

# Core Corpus Artifacts

## Master Catalog

### Primary Files

* `showtrials_master_catalog.tsv`
* `showtrials_master_catalog_report.txt`

### Purpose

The master catalog is the central inventory of documents.

Most later phases depend on it.

It acts as the documentary reference layer for:

* document counts;
* metadata analysis;
* taxonomy work;
* semantic layers;
* sizing analysis;
* chunking discovery.

### Importance

Critical.

Nearly every later artifact depends on the catalog.

---

## Search Corpus

### Primary Files

* `showtrials_search_corpus.tsv`
* `showtrials_search_corpus_report.txt`

### Purpose

Contains searchable textual material extracted from the corpus.

This artifact supports:

* search experiments;
* structural discovery;
* glossary development;
* translation planning;
* future retrieval design.

### Importance

Critical.

Large source artifact.

Not currently versioned.

---

# Documentary Taxonomy Artifacts

## Document Type Classification

### Primary Files

* `showtrials_document_types.tsv`
* `showtrials_document_types_v2.tsv`
* `showtrials_document_types_v3.tsv`
* `showtrials_document_types_v4.tsv`

### Validation

* `showtrials_document_types_v2_validation.tsv`
* `showtrials_document_types_v3_validation.tsv`
* `showtrials_document_types_v4_validation.tsv`

### Reports

* `showtrials_document_types_report.txt`
* `showtrials_document_types_v2_report.txt`
* `showtrials_document_types_v3_report.txt`
* `showtrials_document_types_v4_report.txt`

### Purpose

Defines the documentary taxonomy used throughout the repository.

### Importance

Critical.

Document type classification is one of the foundations of:

* search;
* chunking;
* sizing;
* translation planning.

---

# Semantic Layer Artifacts

## People

### Examples

* `showtrials_canonical_people.tsv`
* `showtrials_person_aliases.tsv`
* `showtrials_person_aliases_reviewed.tsv`
* `showtrials_person_merge_candidates.tsv`

### Reports

* person alias reports
* normalization reports
* centrality reports
* cleanup reports

### Purpose

Creates stable identities for people appearing across the corpus.

### Importance

High.

Supports semantic retrieval and future knowledge layers.

---

## Organizations

### Examples

* `showtrials_organizations.tsv`
* `showtrials_organization_families.tsv`
* `showtrials_organization_process_matrix.tsv`
* `showtrials_organization_family_document_matrix.tsv`

### Purpose

Describes institutions and relationships between organizations.

### Importance

High.

Supports documentary context and retrieval.

---

## Processes

### Examples

* `showtrials_process_document_matrix.tsv`
* `showtrials_process_profiles.tsv`
* `showtrials_process_layer.tsv`

### Purpose

Models documentary participation in broader historical processes.

### Importance

High.

Supports future evidence-oriented retrieval.

---

# Search Artifacts

## Search

### Examples

* `showtrials_search_v2_validation.tsv`
* `showtrials_search_v2_validation_report.txt`

### Purpose

Represents the current generation of repository search work.

Search evolved from simple text lookup toward metadata-aware retrieval.

### Importance

Strategic.

Acts as a bridge between corpus discovery and future retrieval systems.

---

# Translation Artifacts

## Translation Glossary

### Examples

* `showtrials_translation_glossary_v1.tsv`
* `showtrials_translation_glossary_g3.tsv`
* `showtrials_translation_glossary_g4.tsv`
* `showtrials_google_translate_glossary_ru_en_v1.tsv`

### Validation

* glossary review files
* glossary validation files
* freeze-readiness files

### Purpose

Provides terminology control for future Russian-to-English translation.

### Importance

Critical.

Translation quality depends heavily on glossary quality.

---

## Translation Profiles

### Examples

* `showtrials_translation_profiles_v1.tsv`

### Purpose

Defines translation-related planning assumptions.

### Importance

Medium.

Supports future translation execution.

---

# Sizing And Cost Artifacts (D1)

## Corpus Sizing

### Primary Files

* `showtrials_corpus_sizing_by_document_d1.tsv`
* `showtrials_corpus_sizing_by_document_type_d1.tsv`
* `showtrials_corpus_sizing_by_process_d1.tsv`

### Validation

* `showtrials_corpus_sizing_chunking_d1_validation.tsv`

### Reports

* `showtrials_corpus_sizing_chunking_d1_report.txt`
* `showtrials_translation_cost_report.txt`

### Purpose

Measures corpus size and translation scale.

### Importance

Critical.

Provides the quantitative baseline for future translation planning.

---

# Structural Discovery Artifacts (D2)

## Structural Chunking Discovery

### Primary Files

* `showtrials_structural_chunking_d2_by_document.tsv`
* `showtrials_structural_chunking_d2_by_type.tsv`
* `showtrials_structural_chunking_d2_examples.tsv`

### Validation

* `showtrials_structural_chunking_d2_validation.tsv`

### Reports

* `showtrials_structural_chunking_d2_report.txt`
* `showtrials_structural_samples_d2_1_report.txt`
* `showtrials_structural_samples_d2_2_report.txt`

### Purpose

Discovers document-native structure.

### Importance

Critical.

Established that chunking must preserve semantic units.

---

# Package Analysis Artifacts (D3)

## Special Report Discovery

### Primary Files

* `showtrials_special_report_packages_d3_1.tsv`
* `showtrials_special_report_attachment_matrix.tsv`

### Validation

* `showtrials_special_report_packages_d3_1_validation.tsv`

### Reports

* `showtrials_special_report_packages_d3_1_report.txt`

### Purpose

Analyzes special reports as documentary packages.

### Importance

Critical.

Produced one of the most important architectural discoveries in the project.

---

## Attachment Taxonomy

### Primary Files

* `showtrials_attachment_taxonomy_d3_1a.tsv`
* `showtrials_attachment_taxonomy_d3_1b.tsv`

### Supporting Files

* taxonomy refinement files
* taxonomy crosswalk files

### Reports

* attachment taxonomy reports
* refinement reports
* validation reports

### Purpose

Normalizes attachment types contained within documentary packages.

### Importance

High.

Reduced perceived corpus complexity and clarified future chunking requirements.

---

# Blueprint Artifacts (D4)

## Chunking Blueprint

### Primary Files

* `showtrials_chunking_blueprint_v1.tsv`
* `showtrials_chunking_blueprint_v1_1.tsv`

### Validation

* blueprint validation files

### Reports

* blueprint reports
* blueprint validation reports

### Policy

* `showtrials_chunking_policy_v1_1.txt`

### Purpose

Defines document-native chunking policy.

### Importance

Critical.

Represents the formal output of the structural discovery cycle.

---

# Validation Artifacts

## Purpose

Validation artifacts exist throughout the repository.

Typical naming patterns:

* `*_validation.tsv`
* `*_validation_report.txt`

### Role

Validation files are evidence that generated artifacts were checked against explicit rules.

### Importance

High.

The repository treats validation as a first-class activity.

---

# Planning Artifacts

## Purpose

Planning artifacts define future work.

Typical naming patterns:

* `plan-*`
* blueprint files
* policy files

### Role

Capture architectural decisions before implementation.

### Importance

High.

Planning artifacts reduce the need for ad hoc implementation.

---

# Reports

## Purpose

Reports provide human-readable summaries of discovery and validation work.

Typical naming patterns:

* `*_report.txt`

### Role

Serve as executive summaries of generated TSV artifacts.

### Importance

High.

Reports are usually the fastest way to understand the output of a phase.

---

# Most Important Files In The Repository

If a new contributor needed to understand the repository quickly, the recommended reading order would be:

1. `README.md`
2. `docs/project-history.md`
3. `docs/discoveries-by-phase.md`
4. `showtrials_master_catalog.tsv`
5. `showtrials_document_types_v4.tsv`
6. `showtrials_search_v2_validation_report.txt`
7. `showtrials_translation_cost_report.txt`
8. `showtrials_structural_chunking_d2_report.txt`
9. `showtrials_special_report_packages_d3_1_report.txt`
10. `showtrials_attachment_taxonomy_refinement_d3_1b_report.txt`
11. `showtrials_chunking_policy_v1_1.txt`
12. `showtrials_chunking_blueprint_v1_1_report.txt`

Together these artifacts explain most of the repository's current state and architectural direction.
