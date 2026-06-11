# Discoveries By Phase

## Purpose

This document records the major discoveries produced during the ShowTrials Discovery project.

It is not a chronological narrative and it is not an execution guide.

Its purpose is to capture the findings that changed assumptions, influenced architecture, or altered future implementation plans.

The repository contains many scripts, reports, validations, and TSV artifacts. This document focuses only on the conclusions that emerged from that work.

---

# Phase 1 — Inventory And Catalog

## Discovery: The corpus required a canonical catalog

Early exports produced a large quantity of material, but the project lacked a stable documentary reference layer.

The creation of inventory artifacts and the master catalog established:

* unique document identities;
* metadata consistency;
* collection boundaries;
* process associations;
* document counts suitable for measurement.

### Impact

All later phases depend on the catalog.

Without a catalog there can be no reliable:

* sizing;
* taxonomy;
* entity analysis;
* search;
* translation planning;
* chunking policy.

---

# Phase 2 — Documentary Taxonomy

## Discovery: Document type classification is foundational

Initially the corpus was treated primarily as a collection of texts.

Analysis demonstrated that future processing depends heavily on documentary form.

Multiple taxonomy revisions eventually produced the current classification baseline.

### Impact

Document type became a first-class property used by:

* search;
* sizing;
* glossary work;
* translation planning;
* chunking policy;
* package analysis.

---

## Discovery: Not all document types are equally important

Although the blueprint currently tracks 35 document types, later analysis showed that only a subset dominates corpus volume and future engineering effort.

### Impact

The project does not require equally sophisticated handling for every type before progress can be made.

Engineering effort should prioritize dominant structures first.

---

# Phase 3 — Semantic Layer

## Discovery: Metadata alone is insufficient

Document metadata describes documents.

It does not explain relationships between:

* people;
* organizations;
* institutions;
* processes;
* roles;
* positions.

The semantic layer emerged because these relationships are central to understanding the corpus.

### Impact

Future retrieval should combine:

* textual evidence;
* document metadata;
* semantic relationships.

---

## Discovery: Entities create retrieval opportunities

The corpus naturally forms networks.

People participate in organizations.

Organizations participate in processes.

Documents reference both.

### Impact

Future retrieval can move beyond keyword search and support evidence-oriented navigation through documentary relationships.

---

# Phase 4 — Search

## Discovery: Search became its own domain

Search began as a convenience feature.

As the repository accumulated metadata, taxonomies, semantic layers, and validation artifacts, search evolved into a major architectural concern.

The project now includes a second-generation search implementation.

### Impact

Search is no longer simply a utility.

It is a bridge between corpus discovery and future retrieval systems.

---

## Discovery: Retrieval quality depends on documentary structure

Better search results require more than text matching.

Document type, semantic relationships, glossary normalization, and future chunk boundaries all influence retrieval quality.

### Impact

Search architecture and chunking architecture became closely connected.

---

# Phase 5 — Translation Glossary

## Discovery: Translation quality begins before translation

The repository originally considered translation as a future activity.

Glossary work revealed that terminology control must occur before large-scale translation begins.

### Impact

Glossary development became part of the translation architecture rather than a post-processing step.

---

## Discovery: Consistency is a scalability problem

Large corpora naturally generate inconsistent translations when terminology is not controlled.

### Impact

Glossary artifacts became a strategic asset rather than a convenience.

---

# Phase 6 — Sizing And Cost Analysis (D1)

## Discovery: Translation is measurable

Before D1, translation effort was discussed in abstract terms.

D1 produced the first quantitative baseline:

* 2,179 documents;
* 27.4 million characters;
* approximately 10,023 estimated chunks;
* approximately USD 547.60 estimated NMT cost.

### Impact

Translation became an engineering problem rather than a hypothetical future task.

---

## Discovery: Cost control requires structure

The measured translation cost immediately raised questions about:

* batching;
* prioritization;
* chunking;
* glossary usage;
* resumability;
* caching.

### Impact

Future translation architecture must optimize cost rather than simply maximize throughput.

---

# Phase 7 — Structural Discovery (D2)

## Discovery: Size-only chunking is insufficient

A naïve strategy would divide text using character limits.

Document inspection showed that this would destroy meaningful structure.

### Impact

Chunking policy must preserve documentary units.

---

## Discovery: Lexical cues create false positives

Words equivalent to "question" and "answer" may appear in many documents.

Their presence alone does not prove a genuine question-and-answer structure.

### Impact

Chunking decisions must be based on documentary form rather than isolated vocabulary.

---

## Discovery: Different document families require different chunk units

Structural analysis revealed recurring patterns across major document families.

### Impact

Future chunking must become document-aware.

One chunking strategy is insufficient for the corpus.

---

# Phase 8 — Special Report Discovery (D3)

## Discovery: Special reports are not ordinary documents

This was one of the most important discoveries in the project.

The original assumption treated special reports as a document type.

Evidence showed that most special reports behave as documentary containers.

### Impact

Future processing must treat special reports as packages.

---

## Discovery: Attachment analysis is required before chunking

A package can contain multiple documentary units with different structures.

Chunking the entire package as a single document would mix evidence types.

### Impact

Attachment detection became a required preprocessing step.

---

## Discovery: Interrogation protocols dominate special-report attachments

D3.1B showed:

* 448 interrogation protocol attachments;
* approximately 85.17% prevalence among analyzed special reports.

Other attachment types exist, but interrogation protocols overwhelmingly dominate.

### Impact

A future chunk builder that handles interrogation protocols well will immediately cover a large portion of package content.

---

# Phase 9 — Attachment Taxonomy Refinement

## Discovery: Corpus complexity is lower than expected

Before attachment refinement, the project appeared to contain a very large number of unrelated documentary forms.

Taxonomy work revealed that many package attachments belong to a relatively small number of recurring structures.

### Impact

The future implementation burden is significantly lower than initially feared.

---

## Discovery: Dominant attachment types emerged

The refined taxonomy identified recurring attachment families:

* interrogation_protocol;
* memo_note;
* theses;
* list;
* reference_note;
* statement;
* confrontation_protocol;
* letter;
* diary.

### Impact

Future engineering effort can focus on a small number of high-value document structures.

---

# Phase 10 — Blueprint Consolidation (D4)

## Discovery: Semantic chunk units can be defined explicitly

Structural work produced enough evidence to formalize chunking policy.

The blueprint records document-native units such as:

* question_answer_block;
* confrontation_exchange;
* speaker_turn;
* conversation_segment;
* document_package.

### Impact

Future chunk builders can be implemented against a documented policy rather than relying on ad hoc heuristics.

---

## Discovery: The corpus is ready for design work

D4 validation completed without structural failures.

The project now possesses:

* a catalog;
* taxonomy;
* semantic layers;
* search infrastructure;
* glossary artifacts;
* sizing baselines;
* package analysis;
* attachment taxonomy;
* chunking policy.

### Impact

The repository can move from discovery into engineering design.

The next major question is no longer:

"What exists in the corpus?"

The next major question is:

"How should these discoveries be operationalized?"

---

# Consolidated Discoveries

The most important findings across the entire project are:

1. The corpus must be understood before it can be translated.

2. Search quality depends on documentary structure.

3. Translation quality begins with terminology control.

4. Translation cost requires measurement and budgeting.

5. Chunking must preserve semantic units.

6. Special reports are documentary packages.

7. Interrogation protocols dominate package attachments.

8. A small number of document structures account for much of the corpus.

9. Blueprint v1.1 provides a defensible policy baseline.

10. The discovery phase has produced enough evidence to begin engineering design.

These discoveries collectively define the current architectural direction of the project.
