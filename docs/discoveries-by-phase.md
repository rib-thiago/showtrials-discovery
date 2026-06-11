# Discoveries By Phase

## Purpose

This document organizes discoveries by the canonical A/B/C/E/G/T/D/R sequence from [methodological-timeline.md](methodological-timeline.md).

It separates discoveries from outputs. Discoveries are conclusions that changed assumptions, architecture, or future implementation plans. Outputs are the scripts, TSVs, reports, and validations that record those conclusions.

## A — Site Reconnaissance And Extraction Strategy

### Discoveries

- The corpus should not be built by blindly scraping rendered HTML pages.
- Multiple HTML samples showed that documentary content had to be separated from navigation, layout, headers, footers, and surrounding page material.
- Curl tests and source inspection helped distinguish page structure from documentary content.
- WordPress/JSON structured data was a better acquisition layer than fragile HTML parsing.

### Outputs

- URL and sitemap/crawl artifacts.
- Source inspection notes and local samples.
- TODO: Identify the exact surviving HTML/curl sample filenames if they are retained in the repository inventory.

### Architectural Impact

The project adopted structured extraction first and HTML as validation/fallback evidence.

## B — JSON Corpus, Text Export, And Local Search

### Discoveries

- JSON fields provided usable titles, slugs, dates, links, metadata, and content.
- Local text and Markdown export became the human-readable inspection layer.
- Search was needed early to explore the corpus, not late as RAG.
- Search v2 became an intermediate step toward evidence-oriented retrieval.

### Outputs

- JSON/page/post artifacts.
- Text and Markdown export directories and export scripts.
- `showtrials_search_corpus.tsv` and search corpus reports.
- Search scripts and search v2 validation artifacts.

### Architectural Impact

The corpus became a local searchable workspace before taxonomy, glossary, or chunking policy was complete.

## C — Catalog, Metadata, And Documentary Taxonomy

### Discoveries

- The corpus required a stable master catalog.
- Document indexes and metadata audits were necessary before reliable analysis.
- Document type classification is foundational.
- Document types evolved through v1, v2, v3, and v4, with comparisons and validations between versions.
- `document_type` became a core property for search, sizing, translation planning, special report analysis, and chunking.

### Outputs

- Master catalog artifacts.
- Document indexes.
- Collection, date, taxonomy, page, and post metadata reports.
- Document type v1 to v4 TSVs.
- Version comparison artifacts and validation outputs.

### Architectural Impact

The corpus shifted from “many texts” to a set of documentary forms with distinct processing requirements.

## E — Entity, People, Organization, Process, And Semantic Layers

### Discoveries

- Metadata alone is insufficient for future retrieval.
- Canonical people and literal people both matter.
- Aliases, truncated persons, and merge candidates require review.
- Organizations, organization families, hierarchy, roles, positions, processes, and process profiles add documentary context.
- Matrices make relationships inspectable.
- Frequency and centrality are not automatically historical or causal centrality.

### Outputs

- Canonical people artifacts.
- Literal people artifacts.
- Alias and truncated-person review artifacts.
- Organization, organization-family, and hierarchy artifacts.
- Role and position artifacts.
- Process layer and process profile artifacts.
- Person-organization-process matrices and validation reports.

### Architectural Impact

Future retrieval should combine text, metadata, and semantic relationships while preserving historical caution.

## G — Glossary And Translation Terminology

### Discoveries

- Translation quality begins before translation.
- Glossary work can reduce ambiguity before paid translation.
- Legal, political, institutional, and historical terminology require canonicalization.
- The glossary should be advanced substantially before incurring monetary translation costs.

### Outputs

- Glossary seeds.
- Initial canonicalization outputs.
- G3 enrichment outputs.
- G4 expansion outputs.
- G4.1 refinement outputs.
- Review files.
- Validation files.
- Freeze-readiness reports.
- Google Translate glossary preparation artifacts.

### Architectural Impact

Glossary work became part of translation architecture, not a post-processing convenience.

## T — Translation Cost And Operational Planning

### Discoveries

- Google Cloud Translation costs make translation operationally serious.
- Model and pricing choices matter.
- Translation must be batched, budgeted, cached, deduplicated, resumable, and validated.
- Status queues such as pending, running, done, and failed are required for safe operation.
- Cost limits per batch are required.
- Future implementation should relate to Toolbox-style `run-jobs` and pipeline workflows.

### Outputs

- Translation cost reports.
- Translation profile artifacts.
- D1 sizing and chunking diagnostics later quantified the operational baseline.

### Architectural Impact

Translation became an engineering workflow rather than a one-shot API call.

## D — Structural Discovery And Chunking Policy

### Discoveries

- D1 measured 2179 documents, 27379787 characters, about 10023 estimated chunks, and about USD 547.60 estimated NMT cost.
- D2 showed that chunking cannot be size-only.
- D2 also showed that lexical markers can create false positives.
- D2.1 structural samples enabled manual inspection by document type.
- D2.2 organized review evidence and drafted a preliminary blueprint.
- Manual sample review confirmed core structures.
- D3 showed that `special_report` is a `document_package`.
- D3.1A normalized special-report attachment relations.
- D3.1B refined attachment taxonomy.
- D4 consolidated chunking blueprint v1.1.

### Outputs

- D1 sizing TSVs and reports.
- D2 structural chunking TSVs and reports.
- D2.1 structural sample index and samples.
- D2.2 review index and blueprint draft.
- D3 special report package artifacts.
- D3.1A attachment matrix, taxonomy, crosswalk, and validation.
- D3.1B refined attachment taxonomy and validation.
- D4 blueprint v1.1, policy document, report, and validation.

### Architectural Impact

Future chunking must preserve document-native semantic units:

- `interrogation_protocol`: `question_answer_block`.
- `confrontation_protocol`: `confrontation_exchange`.
- `session_transcript`: `speaker_turn`.
- `conversation_recording`: `conversation_segment`.
- `special_report`: `document_package`.

Attachment detection must occur before chunking for `special_report`.

## R — Repository Governance, Git, Documentation, And GitHub Preparation

### Discoveries

- The repository had become a substantial workspace rather than a temporary directory.
- Inventory files were required before any physical restructuring.
- `.gitignore` policy matters because raw/exported corpus material should not be versioned yet.
- Existing commits already record inventory and documentation milestones.
- Documentation should precede private GitHub setup and physical reorganization.
- Physical restructuring should happen only later and by script.

### Outputs

- `repo-current-filelist.txt`.
- `repo-current-scripts.txt`.
- `repo-current-tsvs.txt`.
- `repo-current-reports-txt.txt`.
- Markdown documentation.
- Git commits already present in the local repository.

### Architectural Impact

The immediate governance path is: commit documentation, configure `gh`, create a private repository, push the baseline, and only then plan scripted restructuring.

## Consolidated Discoveries

1. The corpus must be understood before it can be translated.
2. Search and text export were early discovery tools, not late RAG work.
3. Document type is a core architectural property.
4. Entity and centrality outputs require historical interpretation.
5. Translation quality starts with glossary control.
6. Translation cost requires batching, caching, status queues, and validation.
7. Chunking must preserve semantic units.
8. Special reports are documentary packages.
9. Interrogation protocols dominate package attachments.
10. Blueprint v1.1 provides the current policy baseline for future chunk builder design.
