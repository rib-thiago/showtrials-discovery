# Repository Policy

## Purpose

This document defines the operational rules of the ShowTrials Discovery repository.

The repository is not merely a collection of scripts and outputs.

It is an evidence-producing system whose purpose is to transform a large historical corpus into a documented, measurable, searchable, and structurally understood knowledge source.

The primary goal of this policy is to preserve reproducibility, traceability, and architectural consistency as the repository continues to evolve.

---

# Core Principles

## Evidence Before Implementation

The repository follows a strict evidence-first approach.

Architectural decisions should be driven by:

* measurements;
* reports;
* validations;
* sample reviews;
* documented discoveries.

Implementation should follow evidence.

Evidence should not be created to justify implementation decisions that have already been made.

---

## Discovery Before Automation

The project prioritizes understanding before automation.

Whenever a new documentary structure, corpus characteristic, or processing workflow is encountered, discovery should occur before large-scale automation.

This principle guided:

* document classification;
* semantic layer creation;
* glossary development;
* structural chunking;
* package analysis.

---

## Explicit Policies Over Implicit Assumptions

Important repository behavior should be documented.

When a workflow becomes important enough to influence multiple phases, it should be represented by:

* a report;
* a validation;
* a blueprint;
* a policy document.

Future contributors should not be required to reverse-engineer repository behavior from scripts alone.

---

# Artifact Lifecycle

Most repository work follows a common lifecycle.

1. Discovery
2. Planning
3. Validation
4. Policy
5. Implementation

Examples:

* structural discovery → chunking blueprint → blueprint validation → chunking policy;
* glossary discovery → glossary review → glossary validation → glossary freeze readiness;
* package discovery → taxonomy refinement → taxonomy validation → package policy.

The repository should preserve this progression.

---

# Source Data Policy

## Raw Corpus Material

Raw corpus material includes:

* exported pages;
* exported posts;
* exported text collections;
* crawl outputs;
* local export directories.

Examples include:

* export-md;
* export-txt;
* pages-json;
* posts-json;
* posts-json-embed;
* showtrials.ru.

These artifacts are considered source material.

---

## Current Versioning Policy

Raw corpus exports should not be versioned in the primary repository at the current stage.

Reasons include:

* repository size;
* duplication;
* regeneration capability;
* future storage-policy uncertainty.

Future storage strategies may include:

* Git LFS;
* object storage;
* release artifacts;
* dedicated corpus repositories.

This decision remains open.

---

# Derived Artifact Policy

Derived artifacts are the primary products of the repository.

Examples include:

* TSV outputs;
* validation files;
* reports;
* matrices;
* profiles;
* blueprints;
* inventories.

Derived artifacts may be versioned.

They are generally preferred over versioning large raw exports.

---

# Script Policy

## Scripts Are First-Class Artifacts

Scripts are not disposable utilities.

Scripts represent documented processing logic.

They should be:

* readable;
* reproducible;
* deterministic when practical;
* reviewable.

---

## Preserve Historical Scripts

Historical scripts should not be deleted simply because newer versions exist.

Older scripts often explain how discoveries evolved.

Examples include:

* document type version progression;
* glossary generations;
* blueprint revisions.

Deprecation is preferable to silent removal.

---

## Script Naming

Repository naming conventions should remain descriptive.

Common prefixes include:

* diagnose-
* plan-
* validate-

These prefixes communicate intent and should be preserved.

---

# Validation Policy

## Validation Is Mandatory

Major generated artifacts should have validation outputs whenever practical.

Validation files serve two purposes:

1. detect structural errors;
2. provide confidence in downstream work.

Examples include:

* taxonomy validation;
* glossary validation;
* blueprint validation;
* search validation.

---

## Validation Artifacts Are Permanent Evidence

Validation outputs should generally be retained.

They document the state of an artifact at a specific point in time.

Future changes can then be compared against historical baselines.

---

# Search Policy

## Search Is Strategic Infrastructure

Search is not considered a convenience feature.

The repository already contains a second-generation search implementation.

Search serves as an intermediate layer between:

* corpus discovery;
* semantic analysis;
* future retrieval;
* future RAG systems.

Search artifacts should therefore be treated as architectural components.

---

## Retrieval Should Respect Documentary Structure

Future retrieval should not operate solely on arbitrary text fragments.

Retrieval quality improves when it incorporates:

* document types;
* entities;
* organizations;
* processes;
* semantic chunk boundaries.

Search evolution should remain aligned with documentary structure.

---

# Translation Policy

## Translation Is Not Yet An Active Processing Stage

The repository currently prepares for translation.

It does not yet perform large-scale translation.

Preparation includes:

* glossary development;
* cost estimation;
* structural discovery;
* chunking policy development.

---

## Translation Must Be Cost-Aware

D1 demonstrated that translation has measurable cost.

Future translation work should therefore include:

* budgeting;
* batching;
* resumability;
* validation;
* glossary integration.

Translation should never be treated as an unlimited resource.

---

## Translation Must Respect Documentary Structure

Translation should occur after documentary structure is understood.

The repository explicitly rejects size-only translation chunking.

Translation units should be informed by chunking policy.

---

# Chunking Policy Governance

## Blueprint Before Builder

The repository deliberately produced a blueprint before implementing a chunk builder.

This ordering should be preserved.

Policy should define behavior before implementation exists.

---

## Semantic Units Are Canonical

Current blueprint v1.1 defines the canonical semantic units for future chunking.

Examples include:

* question_answer_block;
* confrontation_exchange;
* speaker_turn;
* conversation_segment;
* document_package.

Future chunk builders should implement these concepts rather than redefining them.

---

# Package Processing Policy

## Special Reports Are Documentary Packages

The repository treats special reports as documentary containers.

This is a documented discovery rather than an implementation preference.

Future processing must assume:

* attachment detection occurs first;
* package structure is preserved;
* attached documentary units remain identifiable.

---

## Package Boundaries Are Evidence Boundaries

A package may contain multiple documentary forms.

These forms should remain distinguishable.

Package boundaries should not be destroyed by chunking or translation.

---

# Documentation Policy

## Documentation Is Part Of The System

Documentation is not supplementary.

Documentation is one of the repository outputs.

Important discoveries should appear in:

* reports;
* policies;
* project history;
* discovery summaries.

---

## Historical Context Must Be Preserved

Future contributors should be able to understand:

* what was discovered;
* why it mattered;
* which decision it changed.

The repository should document reasoning, not merely results.

---

# Reorganization Policy

## No Manual Reorganization

Large-scale file moves should not be performed manually.

Repository restructuring should be:

* planned;
* scripted;
* reviewed;
* validated;
* committed separately.

---

## Preserve Traceability

Historical file locations and artifact relationships should remain traceable.

The repository should avoid disruptive reorganizations that obscure project history.

---

# Future Architecture Policy

The repository currently stops at the discovery baseline.

The following systems remain future work:

* chunk builder;
* translation execution;
* SQLite persistence;
* retrieval layer;
* RAG layer.

These systems should build upon existing discoveries rather than bypassing them.

---

# Decision Framework

When uncertainty exists, the preferred decision order is:

1. preserve evidence;
2. preserve reproducibility;
3. preserve traceability;
4. validate assumptions;
5. automate only after understanding.

This hierarchy reflects the philosophy that guided the repository from its earliest discovery work through the current blueprint baseline.

The repository exists to understand the corpus before attempting to transform it.
