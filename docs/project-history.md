# Project History

## Purpose

This document is the main historical narrative for ShowTrials Discovery. It follows the canonical sequence from [methodological-timeline.md](methodological-timeline.md).

D1 to D4 are not the whole project. They are subphases of D — Structural Discovery And Chunking Policy.

## A — Site Reconnaissance And Extraction Strategy

The project began by investigating how the ShowTrials website exposed documentary content.

The first work was not classification, translation, chunking, or RAG. It was source reconnaissance:

- analysis of multiple HTML samples;
- tests with curl;
- identification of real documentary content inside page structure;
- separation of document content from navigation, layout, headers, footers, and other page noise;
- comparison of direct HTML scraping with structured extraction;
- investigation of WordPress-style structured data.

The key decision was to prefer JSON/WordPress structured data over fragile rendered-HTML scraping. HTML remained useful as evidence and fallback, but not as the primary acquisition layer.

This decision shaped every later artifact.

## B — JSON Corpus, Text Export, And Local Search

After the JSON path became clear, the project inspected JSON fields and converted structured data into local working artifacts.

This phase included:

- inspection of JSON fields;
- extraction of posts and pages;
- identification of titles, slugs, dates, links, metadata, and content fields;
- creation of local JSON/page/post artifacts;
- creation of text and Markdown export mechanisms;
- scripts and script families for textual export;
- generation of exported text suitable for inspection;
- creation of early local search tooling;
- later evolution to search v2 and validation artifacts.

Search was created early as a corpus exploration tool. It was not a late RAG phase. It made the local corpus navigable while the documentary model was still being discovered.

## C — Catalog, Metadata, And Documentary Taxonomy

Once the corpus was locally navigable, the next task was to create a stable documentary reference layer.

This phase produced:

- corpus inventories;
- page and post metadata inspections;
- document indexes;
- document collection artifacts;
- date audits;
- taxonomy reports;
- master catalog artifacts.

The master catalog became the reference layer for later analysis.

Document type classification then evolved through:

- document types v1;
- document types v2;
- document types v3;
- document types v4;
- comparison artifacts between versions;
- validation outputs for taxonomy revisions.

The major discovery was that the corpus is not merely a set of texts. It is a set of documentary forms. `document_type` became a core property used by search, sizing, translation planning, special report analysis, and chunking policy.

## E — Entity, People, Organization, Process, And Semantic Layers

After catalog and taxonomy work, the project expanded into semantic structure.

This phase built artifacts around:

- canonical people;
- literal people;
- aliases;
- truncated persons;
- merge candidates;
- person normalization;
- organizations;
- organization families;
- organization hierarchy;
- roles;
- positions;
- processes;
- process layers;
- process profiles;
- person-organization matrices;
- person-process matrices;
- organization-process matrices.

The goal was not entity extraction for its own sake. The goal was to build a documentary intelligence layer capable of supporting future search, interpretation, translation, and retrieval.

A methodological caution emerged here: frequency and centrality metrics require historical interpretation. They must not be automatically interpreted as historical centrality, causal importance, guilt, influence, or evidentiary weight.

## G — Glossary And Translation Terminology

Translation terminology became a major project front before large-scale translation was attempted.

Glossary work included:

- glossary seeds;
- initial canonicalization;
- G3 enrichment;
- G4 expansion;
- G4.1 refinement;
- review files;
- validation outputs;
- freeze-readiness checks;
- Google Translate glossary preparation.

The glossary was treated as a strategic artifact. Its purpose is to improve Russian-to-English consistency, preserve legal and historical terminology, reduce ambiguity, and lower downstream waste.

The project deliberately advanced glossary work substantially before incurring monetary translation costs.

## T — Translation Cost And Operational Planning

Translation planning began with practical questions about Google Cloud Translation, model choices, prices, billing, quotas, and alternatives.

This phase covered:

- Google Cloud Translation;
- model and pricing distinctions;
- NMT cost estimation;
- character counting;
- batching;
- cache by hash;
- deduplication;
- pending, running, done, and failed queues;
- resumability by status;
- cost limits per batch;
- validation before and after translation;
- backups of TSVs;
- future relation to Toolbox-style `run-jobs` and pipeline workflows.

D1 later quantified the corpus, but the operational concerns were already clear: translation could not be a one-shot process.

## D — Structural Discovery And Chunking Policy

The D-series work is the later structural-discovery cycle. It was motivated by translation planning and the need to preserve documentary meaning.

### D1 — Corpus Sizing And Translation Cost Diagnostics

D1 measured:

- 2179 documents;
- 27379787 characters;
- about 27.4M characters;
- about 10023 estimated chunks by profile target;
- about USD 547.60 estimated NMT translation cost.

This showed that translation had to be staged, budgeted, resumable, and structurally aware.

### D2 — Structural Chunking Discovery

D2 investigated markers such as question/answer patterns, speaker turns, date headers, numbered points, signatures, attachments, salutations, and list density.

It also produced a methodological correction: lexical markers can create false positives. A document can contain words equivalent to question or answer without being structurally organized as a Q/A protocol.

### D2.1 — Structural Sample Audit

D2.1 generated structural samples by document type for manual inspection. The goal was to inspect real document form, not only regex output.

### D2.2 — Structural Review And Blueprint Draft

D2.2 produced review-oriented artifacts and a preliminary chunking blueprint. It organized evidence for human review rather than deciding final policy alone.

### Manual Sample Review

Manual review confirmed:

- interrogation protocols use real question-and-answer blocks;
- session transcripts are organized by speaker turns;
- conversation recordings combine timestamps, speakers, and event notes;
- special reports behave as documentary packages.

### D3 — Special Report Package Analysis

D3 showed that `special_report` should not be treated as a simple document type. Most special reports are packages containing a cover communication plus attached documentary units.

### D3.1A — Attachment Taxonomy Normalization

D3.1A normalized attachment detections into document-to-attachment relations and showed that attachments were dominated by recurring types.

### D3.1B — Attachment Taxonomy Refinement

D3.1B refined attachment classification using Russian document markers.

Key refined results:

- `interrogation_protocol`: 448, 85.17%;
- `memo_note`: 51, 9.70%;
- `theses`: 42, 7.98%;
- `list`: 40, 7.60%;
- `reference_note`: 37, 7.03%;
- `statement`: 30, 5.70%;
- `confrontation_protocol`: 17, 3.23%;
- `letter`: 10, 1.90%;
- `diary`: 8, 1.52%;
- `memo`: 4, 0.76%;
- `draft_project`: 1, 0.19%;
- `unknown_attachment`: 1, 0.19%.

### D4 — Chunking Blueprint v1.1 Consolidation

D4 consolidated the structural discoveries into blueprint v1.1.

The policy includes:

- `interrogation_protocol` uses `question_answer_block`;
- `confrontation_protocol` uses `confrontation_exchange`;
- `session_transcript` uses `speaker_turn`;
- `conversation_recording` uses `conversation_segment`;
- `special_report` uses `document_package`;
- `special_report` requires package detection and attachment-first strategy.

D4 validated 35 document types with `FAIL=0` and 24 expected warnings for residual types requiring future review.

## R — Repository Governance, Git, Documentation, And GitHub Preparation

After the D-series consolidation, the repository required stronger governance.

This phase includes:

- `repo-current-*` inventory files;
- `.gitignore` policy;
- existing documentation and inventory commits;
- documentation baseline;
- decision to avoid manual file reorganization;
- decision to postpone physical restructuring until it can be scripted;
- preparation for `gh` and a private GitHub repository.

The current inventory records:

- 4780 files;
- 101 Python scripts;
- 162 TSV artifacts;
- 101 TXT reports.

The repository is now a substantial discovery and engineering workspace, not a temporary working directory.

## Current State

The project now has:

- a site extraction strategy;
- JSON-based corpus acquisition;
- local text and Markdown export;
- local search and search v2;
- corpus inventories;
- master catalog;
- document taxonomy v1 to v4;
- semantic layers for people, organizations, roles, positions, and processes;
- translation glossary generations;
- translation cost baseline;
- structural chunking diagnostics;
- special report package analysis;
- refined attachment taxonomy;
- chunking blueprint v1.1;
- initial Git governance and documentation.

Future work should build on this sequence rather than flattening it into D1 to D4.
