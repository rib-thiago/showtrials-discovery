# Project History

## Introduction

ShowTrials Discovery did not begin as a chunking project, a translation project, or a RAG project.

It began as a corpus-discovery effort.

The original challenge was simple: understand what existed inside the ShowTrials corpus before making architectural decisions about translation, indexing, storage, retrieval, or semantic search.

Over time, the project evolved into a documentary engineering workflow whose primary objective is to replace assumptions with evidence.

The repository therefore records not only outputs, but also the reasoning process that produced them.

---

## Phase 0 — Collection and Export

The first phase focused on obtaining a workable local corpus.

This work included:

* URL collection and inspection;
* page and post exports;
* local corpus generation;
* export validation;
* corpus cleanliness checks.

The objective was not yet classification or analysis.

The objective was simply to create a stable local corpus that could be inspected repeatedly without depending on a live website.

This phase produced the raw material used by all later stages.

A deliberate decision was made to keep exported corpus material outside the version-controlled discovery baseline until a long-term storage policy is defined.

---

## Phase 1 — Inventory and Catalog

Once corpus material was available locally, the next challenge was understanding what actually existed.

This phase produced:

* document inventories;
* document indexes;
* metadata reports;
* date audits;
* collection summaries;
* corpus statistics;
* master catalog artifacts.

The master catalog became the central reference layer for later analysis.

The repository moved from a collection of exported files to a documented corpus with identifiable records.

This phase established the universe of documents that would later be classified, measured, and analyzed.

---

## Phase 2 — Documentary Taxonomy

The next step was determining what kinds of documents existed.

Document classification evolved through multiple iterations.

Several generations of document-type artifacts were produced and validated before arriving at the current taxonomy baseline.

This work transformed the corpus from:

"many documents"

into:

"a set of document families with identifiable structural characteristics."

Document type classification later became one of the foundations of:

* translation planning;
* chunking policy;
* package analysis;
* retrieval design.

---

## Phase 3 — Semantic Layer

After document types became stable enough, attention shifted toward semantic structure.

The repository accumulated artifacts describing:

* people;
* aliases;
* organizations;
* organization families;
* hierarchy relationships;
* roles;
* positions;
* processes;
* process profiles;
* entity matrices.

The goal was not named-entity extraction for its own sake.

The goal was to understand how documentary evidence connects across the corpus.

This phase laid the groundwork for future retrieval systems that can reason about relationships rather than relying exclusively on text matching.

---

## Phase 4 — Search Evolution

As metadata and semantic layers matured, search became a natural next step.

Early search capabilities focused primarily on text lookup.

Over time, the project moved toward richer retrieval models that could incorporate:

* metadata;
* document type information;
* people;
* organizations;
* process relationships;
* taxonomy artifacts.

The repository now contains a second-generation search implementation and validation artifacts.

Search became an important bridge between corpus discovery and future retrieval.

The long-term objective is not keyword search alone.

The objective is evidence-oriented retrieval capable of supporting historical research, translation workflows, and future RAG systems.

---

## Phase 5 — Translation Glossary Development

Translation was identified as one of the major future costs of the project.

Rather than immediately translating documents, the repository first focused on terminology.

Several glossary generations were produced.

This work included:

* glossary seeds;
* glossary review cycles;
* canonicalization;
* freeze-readiness analysis;
* translation profiles.

The glossary effort had two purposes.

First, improve future translation consistency.

Second, reduce ambiguity in historically and politically sensitive terminology.

The glossary became one of the foundational control mechanisms for future translation work.

---

## Phase 6 — Corpus Sizing and Cost Analysis (D1)

Once the corpus structure became sufficiently understood, the project moved from assumptions to measurement.

D1 established the first quantitative baseline.

Key results:

* 2,179 documents;
* 27,379,787 characters;
* approximately 10,023 estimated chunks;
* approximately USD 547.60 estimated NMT translation cost.

This phase changed the discussion dramatically.

Translation was no longer an abstract future task.

It became a measurable engineering problem.

The results demonstrated that translation would require:

* budgeting;
* batching;
* resumability;
* cost controls;
* structure-aware processing.

---

## Phase 7 — Structural Discovery (D2)

The next challenge was understanding how documents should be divided.

Initial assumptions suggested chunking could be driven primarily by size limits.

Investigation showed that approach would be inadequate.

Documents contain meaningful internal structure that must be preserved.

Examples include:

* question-and-answer exchanges;
* speaker turns;
* documentary sections;
* lists;
* procedural records.

An important outcome of D2 was the rejection of lexical false positives.

Words such as "question" and "answer" inside a document do not necessarily imply a genuine question-and-answer structure.

Structural evidence must come from documentary form, not isolated vocabulary.

This phase established the principle that chunking must preserve semantic units.

---

## Phase 8 — Special Report Discovery (D3)

D3 produced one of the most important discoveries in the project.

Originally, `special_report` was treated as a document type.

Investigation demonstrated that this model was incomplete.

Most special reports behave as documentary containers.

They frequently contain:

* a forwarding document;
* a cover note;
* attached documentary evidence;
* interrogation protocols;
* statements;
* memoranda;
* lists;
* reference materials.

This discovery changed the architecture of the future pipeline.

Instead of treating special reports as ordinary documents, the repository now treats them as documentary packages.

Subsequent attachment analysis revealed that interrogation protocols appear inside special reports in approximately 85% of observed cases.

This result fundamentally altered future chunking strategy.

---

## Phase 9 — Attachment Taxonomy Refinement

After identifying special reports as packages, attention shifted toward the attached documentary units.

Several rounds of normalization and refinement produced a much clearer attachment taxonomy.

The analysis showed that a relatively small number of attachment types dominate the corpus.

The most common attachment type is:

* interrogation_protocol.

Other recurring attachment types include:

* memo_note;
* theses;
* list;
* reference_note;
* statement;
* confrontation_protocol;
* letter;
* diary.

This phase significantly reduced perceived complexity.

The project no longer needed to assume that every document type would require unique handling.

Instead, it became clear that a smaller number of dominant structures account for much of the corpus.

---

## Phase 10 — Chunking Blueprint Consolidation (D4)

D4 consolidated discoveries from all previous structural phases.

The result was chunking blueprint v1.1.

This blueprint records document-native semantic units.

Examples include:

* interrogation_protocol → question_answer_block;
* confrontation_protocol → confrontation_exchange;
* session_transcript → speaker_turn;
* conversation_recording → conversation_segment;
* special_report → document_package.

The blueprint represents policy rather than implementation.

Its purpose is to define how future chunk builders should behave.

Validation completed with:

* 35 document types reviewed;
* zero structural failures;
* expected warnings for document types requiring future review.

This phase marks the end of the initial discovery cycle.

---

## Current State

At the current milestone, the repository contains:

* a documented corpus baseline;
* document taxonomy;
* semantic layers;
* search infrastructure;
* glossary artifacts;
* sizing and cost analysis;
* structural chunking discoveries;
* package analysis;
* attachment taxonomy;
* chunking blueprint policy.

The project now possesses enough evidence to move from discovery into engineering design.

The next major stage is not additional classification.

The next major stage is designing the systems that will operationalize these discoveries.

---

## Planned Future Stages

The expected sequence after the discovery baseline is:

1. repository consolidation and governance;
2. chunk builder design;
3. translation pilot design;
4. corpus persistence strategy;
5. SQLite data model design;
6. retrieval architecture design;
7. evidence-oriented RAG design.

These stages will build upon the documentary knowledge accumulated throughout the discovery process.

The guiding principle remains unchanged:

evidence before implementation.
