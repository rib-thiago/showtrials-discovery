# Roadmap

## Purpose

This document describes the expected evolution of the ShowTrials Discovery project after completion of the initial discovery baseline.

The roadmap is not a task list.

It is a strategic view of the major engineering stages that are expected to follow the discovery work already completed.

Future priorities may change as new evidence emerges.

However, the general direction described here reflects the current architectural understanding of the project.

---

# Current Milestone

The repository has completed its first major discovery cycle.

Completed areas include:

* corpus collection and export;
* inventory and catalog generation;
* documentary taxonomy development;
* semantic layer construction;
* search evolution;
* translation glossary development;
* corpus sizing and cost analysis;
* structural discovery;
* documentary package analysis;
* attachment taxonomy refinement;
* chunking blueprint consolidation.

The repository now possesses sufficient evidence to move from discovery into engineering design.

The primary question is no longer:

"What exists in the corpus?"

The primary question is now:

"How should these discoveries be operationalized?"

---

# Phase C1 — Chunk Builder Design

## Objective

Design a chunk builder that implements the policies established by blueprint v1.1.

This phase focuses on architecture rather than implementation.

The goal is to define:

* inputs;
* outputs;
* processing stages;
* validation rules;
* storage assumptions.

---

## Key Requirements

The future chunk builder must:

* preserve semantic units;
* preserve package boundaries;
* support resumable processing;
* support validation;
* support future translation workflows.

It should not begin as a size-only chunker.

Document structure must remain the primary driver.

---

## Expected Deliverables

* chunk builder architecture document;
* chunk builder workflow specification;
* chunk validation strategy;
* chunk metadata schema;
* implementation blueprint.

---

# Phase C2 — Translation Architecture

## Objective

Design the translation workflow that will operate on chunked documentary units.

The project has already demonstrated that translation has measurable cost.

Translation therefore requires engineering controls.

---

## Key Requirements

Future translation workflows should support:

* glossary integration;
* batching;
* resumability;
* cost controls;
* validation;
* translation provenance.

Translation should preserve relationships between:

* documents;
* packages;
* chunks;
* translated outputs.

---

## Translation Pilot

A controlled pilot should be performed before large-scale translation.

Recommended scope:

* document types marked translation_ready=yes;
* small budget;
* glossary-enabled workflow;
* full validation.

The pilot should exist to validate assumptions rather than maximize throughput.

---

# Phase C3 — Corpus Persistence Strategy

## Objective

Define how corpus artifacts should be stored long term.

The repository currently contains:

* source exports;
* derived TSVs;
* reports;
* validation artifacts;
* planning artifacts.

Future systems will require stronger persistence guarantees.

---

## Open Questions

Topics that remain unresolved include:

* raw corpus storage;
* versioning strategy;
* archival strategy;
* backup strategy;
* reproducibility guarantees.

Potential solutions may include:

* Git repositories;
* Git LFS;
* SQLite;
* object storage;
* release artifacts.

No final decision has been made.

---

# Phase C4 — SQLite Design

## Objective

Design a structured persistence model for documentary data.

SQLite is currently considered the most likely initial persistence layer.

---

## Candidate Entities

Likely entities include:

* documents;
* document types;
* people;
* organizations;
* processes;
* glossary terms;
* packages;
* attachments;
* chunks;
* translations.

---

## Design Principle

The database should reflect documentary structure rather than merely storing text blobs.

Relationships discovered during repository analysis should become explicit database relationships.

---

# Phase C5 — Search Evolution

## Objective

Expand the current search capabilities into a more mature retrieval system.

The repository already contains second-generation search work.

Future efforts should build upon that foundation.

---

## Desired Capabilities

Future retrieval should support:

* metadata-aware search;
* document-type filtering;
* process filtering;
* organization filtering;
* people filtering;
* glossary-aware search;
* package-aware retrieval;
* chunk-aware retrieval.

The goal is evidence retrieval rather than simple text matching.

---

# Phase C6 — Retrieval Architecture

## Objective

Design retrieval mechanisms that operate on documentary evidence units.

This phase represents the transition from discovery artifacts toward knowledge-system architecture.

---

## Guiding Principle

Retrieval should return meaningful documentary structures.

Examples include:

* question-answer exchanges;
* speaker turns;
* confrontation exchanges;
* documentary sections;
* package attachments.

Retrieval quality should improve as documentary structure becomes more explicit.

---

# Phase C7 — Evidence-Oriented RAG

## Objective

Create a retrieval-augmented workflow grounded in documentary evidence.

The repository has never treated RAG as an immediate goal.

Instead, RAG is viewed as a downstream consequence of successful discovery work.

---

## Why Discovery Came First

The project deliberately avoided beginning with embeddings and vector databases.

Several prerequisite questions had to be answered first:

* What is a document?
* What is a package?
* What is a chunk?
* What is a valid evidence unit?
* Which entities matter?
* Which relationships matter?

The discovery process produced answers to those questions.

---

## Desired Characteristics

Future RAG should:

* retrieve documentary units;
* preserve provenance;
* preserve package context;
* support citations;
* expose evidence boundaries clearly.

The goal is not conversational convenience.

The goal is evidence-oriented retrieval.

---

# Repository Consolidation

## Objective

Improve repository organization while preserving traceability.

The current repository evolved through active discovery work and therefore reflects historical development rather than final structure.

---

## Requirements

Future reorganization should:

* be scripted;
* be documented;
* be validated;
* preserve history;
* preserve discoverability.

Manual large-scale file movement should be avoided.

---

## Expected Future Structure

A likely future organization may separate:

* scripts;
* reports;
* TSV artifacts;
* documentation;
* policies;
* validation outputs.

This work should occur only after current documentation and version-control goals are completed.

---

# Git And Collaboration

## Objective

Improve governance and reproducibility.

Near-term priorities include:

* GitHub integration;
* private repository hosting;
* commit discipline;
* release checkpoints;
* repository documentation.

The goal is to ensure that discoveries remain reproducible and auditable.

---

# Long-Term Vision

The long-term vision is not merely to translate documents.

The long-term vision is to create a documentary knowledge platform built on explicit evidence.

Such a platform would combine:

* documentary structure;
* semantic relationships;
* glossary control;
* translation workflows;
* retrieval systems;
* evidence-oriented RAG.

The discovery repository is the foundation upon which that platform can eventually be constructed.

---

# Guiding Principle

The roadmap follows a simple progression:

Discovery → Policy → Design → Implementation → Retrieval → Knowledge Systems

Every completed phase of the repository has reinforced the same lesson:

understanding the corpus before transforming the corpus produces better architectural decisions.

The roadmap therefore preserves the project's original philosophy:

evidence before implementation.
