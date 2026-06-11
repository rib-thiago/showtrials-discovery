# Methodological Timeline

## Purpose

This document records the methodological sequence of the ShowTrials Discovery project.

It exists to correct a simplification that appeared in earlier documentation: D1 to D4 are not the whole history of the project. They are a later structural-discovery and translation-planning subcycle.

The full project began earlier, with site reconnaissance, HTML inspection, curl tests, JSON discovery, local export, and search.

This timeline should be treated as the reference narrative for future documentation.

## A — Site Reconnaissance And Extraction Strategy

The project began by investigating how to extract documentary content from the ShowTrials website.

This was not a generic scraping task. The first problem was to understand the site itself.

The initial work included:

- inspection of multiple HTML samples;
- identification of where documentary content appeared in the page structure;
- separation of real document content from navigation, layout, headers, footers, and surrounding site material;
- tests with curl;
- comparison between direct HTML scraping and structured data extraction;
- investigation of WordPress-style data structures;
- decision to prefer JSON-derived extraction over fragile HTML parsing.

The important discovery of this phase was that the corpus should not be built by blindly scraping rendered pages. The better path was to use structured JSON data when possible and treat HTML as evidence for validation and fallback, not as the primary extraction layer.

This phase established the extraction strategy for everything that followed.

## B — JSON Corpus, Text Export, And Local Search

After the JSON path became clear, the next step was to identify usable fields and convert structured data into a workable local corpus.

This phase included:

- inspection of JSON fields;
- extraction of posts and pages;
- identification of titles, slugs, dates, links, metadata, and content fields;
- creation of local JSON/page/post artifacts;
- creation of text and Markdown export mechanisms;
- generation of exported text suitable for inspection;
- creation of local search tooling.

The local search mechanism was created early, soon after the useful JSON fields were identified. It was not a late RAG feature. It was a practical exploration tool that made the corpus navigable while the documentary model was still being discovered.

The project later evolved this into a second-generation search implementation with validation artifacts.

Important concepts from this phase:

- JSON became the structured acquisition layer.
- Text and Markdown export became the human-readable inspection layer.
- Search became the local navigation and discovery layer.
- Search v2 became an intermediate step toward future evidence-oriented retrieval.

This phase is central to the project history because it transformed the corpus from remote website content into a local searchable workspace.

## C — Catalog, Metadata, And Documentary Taxonomy

Once the corpus became locally navigable, the next challenge was to create a stable documentary reference layer.

This phase produced:

- corpus inventories;
- page and post metadata inspections;
- document indexes;
- document collection artifacts;
- date audits;
- taxonomy reports;
- master catalog artifacts.

The master catalog became the reference layer for later work.

The document taxonomy then evolved through multiple versions:

- initial document types;
- document types v2;
- document types v3;
- document types v4;
- comparison artifacts between versions;
- validation outputs.

This work clarified that the corpus is not merely a set of texts. It is a set of documentary forms.

Document type became a core property used by:

- search;
- cost estimation;
- translation planning;
- chunking policy;
- special report analysis;
- future retrieval design.

## E — Entity, People, Organization, Process, And Semantic Layers

After cataloging and taxonomy work, the project expanded into semantic structure.

This phase built artifacts around:

- literal people;
- canonical people;
- person aliases;
- truncated names;
- merge candidates;
- person normalization;
- people indexes;
- people-document relations;
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

The goal was not entity extraction for its own sake.

The goal was to build a documentary intelligence layer capable of supporting future search, interpretation, translation, and retrieval.

A key methodological caution also emerged in this phase: semantic metrics require historical interpretation. For example, a figure can be frequently mentioned because of institutional position, addressee status, accusation, or narrative role. Frequency and centrality are not automatically historical causality.

This caution remains important for future RAG and retrieval work.

## G — Glossary And Translation Terminology

Translation preparation became a major project front before any large-scale translation was attempted.

The glossary work passed through several generations, including:

- seed generation;
- initial canonicalization;
- G3 enrichment;
- G4 expansion;
- G4.1 refinement;
- review TSVs;
- validation outputs;
- freeze-readiness checks;
- Google Translate glossary preparation.

The glossary was treated as a strategic artifact, not a convenience file.

Its purposes include:

- improving Russian-to-English translation consistency;
- preserving legal, political, institutional, and historical terminology;
- reducing ambiguity before paid translation;
- supporting future translation pilots;
- improving later retrieval consistency.

A major decision in this phase was to push glossary canonicalization as far as practical before incurring translation costs, because glossary work had no direct monetary cost and could reduce downstream waste.

## T — Translation Cost And Operational Planning

The translation discussion began with practical questions about Google Cloud Translation, API access, models, billing, quotas, and alternatives.

Important topics included:

- Google Cloud Translation setup;
- model and pricing distinctions;
- NMT pricing;
- LLM translation pricing differences;
- character counting;
- batch translation billing;
- input and output character considerations;
- number of target languages;
- cost estimation;
- possible alternatives to Google Translate;
- quality versus cost tradeoffs.

The estimated translation cost made the problem operationally serious.

Translation could not be treated as a one-shot activity.

The project identified the need for:

- batching;
- budget limits;
- cache by hash;
- deduplication;
- avoiding repeated translation of metadata;
- resumable status fields;
- pending/running/done/failed queues;
- validation before and after translation;
- backups of TSVs;
- eventual integration with Toolbox-style run-jobs and pipelines.

This operational translation planning directly motivated the later sizing and chunking phases.

## D — Structural Discovery And Chunking Policy

The D-series phases are not the beginning of the project. They are the later structural-discovery cycle that emerged from translation planning.

### D1 — Corpus Sizing And Translation Cost Diagnostics

D1 measured the corpus and produced the first quantitative translation baseline.

Key results:

- 2,179 documents;
- 27,379,787 characters;
- approximately 27.4 million characters;
- approximately 10,023 estimated chunks by profile target;
- approximately USD 547.60 estimated NMT translation cost.

This phase showed that translation needed to be staged, budgeted, and structurally aware.

### D2 — Structural Chunking Discovery

D2 investigated whether document structure could be detected automatically.

It examined markers such as:

- question and answer patterns;
- speaker turns;
- date headers;
- numbered points;
- signatures;
- attachments;
- salutations;
- list density.

An implementation issue appeared when large TSV fields exceeded Python CSV defaults. This led to the use of csv.field_size_limit with sys.maxsize in later scripts.

D2 produced an important methodological discovery: lexical markers can create false positives.

A document can contain words equivalent to question or answer without being structurally organized as a question-and-answer protocol.

This discovery prevented the project from confusing vocabulary with documentary structure.

### D2.1 — Structural Sample Audit

D2.1 generated structural samples for manual inspection.

The goal was to inspect real document form, not merely regex output.

Samples were generated by document type and included beginning and ending excerpts.

This enabled manual review of major document families.

### D2.2 — Structural Review And Blueprint Draft

D2.2 produced review-oriented artifacts and a preliminary chunking blueprint.

It did not decide final policy alone.

Its role was to organize evidence for human review and later consolidation.

### Manual Sample Review

Manual inspection of selected samples confirmed key structures:

- interrogation protocols use real question-and-answer blocks;
- session transcripts are organized by speaker turns;
- conversation recordings combine timestamps, speakers, and event notes;
- special reports behave as documentary packages.

This manual review was a turning point.

It showed that automation was useful for discovery, but policy required documentary interpretation.

### D3 — Special Report Package Analysis

D3 focused on special reports.

The key discovery was that special_report should not be treated as a simple document type.

Most special reports are packages containing a cover communication plus attached documentary units.

D3.1 found that the vast majority of special reports showed package behavior.

### D3.1A — Attachment Taxonomy Normalization

D3.1A normalized attachment detections into document-to-attachment relations.

This showed that special-report attachments were dominated by recurring types, especially interrogation protocols.

### D3.1B — Attachment Taxonomy Refinement

D3.1B refined attachment classification using more specific Russian document markers.

It distinguished, among other things:

- interrogation protocols;
- confrontation protocols;
- statements;
- letters;
- memo notes;
- reference notes;
- lists;
- diaries;
- theses;
- draft projects.

Key refined results included:

- interrogation_protocol: 448;
- memo_note: 51;
- theses: 42;
- list: 40;
- reference_note: 37;
- statement: 30;
- confrontation_protocol: 17;
- letter: 10;
- diary: 8;
- memo: 4;
- draft_project: 1;
- unknown_attachment: 1.

This significantly reduced perceived complexity.

### D4 — Chunking Blueprint v1.1 Consolidation

D4 consolidated the structural discoveries into blueprint v1.1.

The current policy includes:

- interrogation_protocol uses question_answer_block;
- confrontation_protocol uses confrontation_exchange;
- session_transcript uses speaker_turn;
- conversation_recording uses conversation_segment;
- special_report uses document_package;
- special_report requires package detection;
- special_report uses attachment-first strategy.

D4 validated 35 document types with zero failures and expected warnings for residual types requiring future review.

## R — Repository Governance, Git, Documentation, And GitHub Preparation

After D1 through D4, the project reached a point where further engineering required better repository governance.

This phase included:

- repository inventory;
- .gitignore policy;
- initial Git setup;
- first inventory commit;
- documentation baseline;
- decision to avoid manual reorganization;
- decision to postpone physical restructuring until it can be scripted;
- preparation for a private GitHub repository.

The repository inventory showed:

- 4,780 files;
- 101 Python scripts;
- 162 TSV artifacts;
- 101 TXT reports.

This proved that the repository was no longer a temporary working directory. It had become a substantial discovery and engineering workspace.

## Current Project State

At this point, the project has completed a broad discovery baseline.

It has:

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

The next phase should not erase this history.

Future work should build on it.

## Correct Global Phase Model

The current preferred global model is:

- A — Site reconnaissance and extraction strategy;
- B — JSON corpus, text export, and local search;
- C — Catalog, metadata, and documentary taxonomy;
- E — Entity, organization, process, and semantic layers;
- G — Glossary and translation terminology;
- T — Translation cost and operational planning;
- D — Structural discovery and chunking policy;
- R — Repository governance and GitHub preparation.

This model is retrospective, but it is more accurate than treating D1 through D4 as the whole project.

D1 through D4 should be understood as subphases of the D-series structural and translation-planning cycle.

They are not the beginning of ShowTrials Discovery.
