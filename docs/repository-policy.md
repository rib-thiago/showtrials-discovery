# Repository Policy

## Purpose

This document defines operational rules for the ShowTrials Discovery repository. It is normative rather than historical.

The repository is an evidence-producing system for the ShowTrials corpus. It should preserve reproducibility, traceability, and methodological consistency across the A/B/C/E/G/T/D/R workflow described in [methodological-timeline.md](methodological-timeline.md).

## Core Principles

### Evidence Before Implementation

Architectural decisions should be driven by measurements, reports, validations, sample reviews, and documented discoveries.

Do not implement chunk builders, translation execution, embeddings, RAG, or database migrations before the relevant design and policy work exists.

### Discovery Before Automation

When a new documentary structure, corpus characteristic, or processing workflow appears, discovery should precede automation.

This principle applies to:

- source extraction;
- JSON and text export;
- search;
- catalog and document taxonomy;
- semantic layers;
- glossary;
- translation cost planning;
- structural chunking;
- package and attachment analysis.

### Explicit Policies Over Implicit Assumptions

Important behavior should be represented by reports, validation artifacts, blueprints, policy documents, or Markdown documentation.

Future contributors should not need to reverse-engineer project policy from scripts alone.

## Source Data Policy

Raw corpus material includes:

- exported pages;
- exported posts;
- exported text and Markdown collections;
- crawl outputs;
- JSON exports;
- local export directories.

Raw/exported corpus material should not be versioned in the primary repository for now.

Reasons:

- repository size;
- duplication;
- regeneration capability;
- unresolved long-term storage policy.

Future storage options may include Git LFS, object storage, release artifacts, or a dedicated private corpus repository.

TODO: Define final raw corpus storage policy.

## Derived Artifact Policy

Derived artifacts may be versioned:

- Python scripts;
- derived TSVs;
- validation files;
- reports;
- matrices;
- profiles;
- blueprints;
- inventories;
- Markdown documentation.

Derived artifacts are the primary evidence base of this repository.

## Script Policy

Scripts are first-class artifacts. They represent documented processing logic and should be readable, deterministic when practical, and reviewable.

Historical scripts should not be deleted merely because newer versions exist. Older versions document how taxonomy, glossary, search, and blueprint decisions evolved.

Descriptive prefixes such as `diagnose-`, `plan-`, `validate-`, `build-`, `review-`, `compare-`, and `canonicalize-` should be preserved.

## Validation Policy

Major generated artifacts should have validation outputs whenever practical.

Validation artifacts:

- detect structural errors;
- record artifact state at a point in time;
- support future comparison;
- distinguish failures from expected warnings.

## Search Policy

Search is strategic infrastructure. It was created early as a corpus exploration tool and later evolved to search v2.

Search should be treated as a bridge between:

- corpus discovery;
- metadata analysis;
- semantic layers;
- future retrieval;
- future RAG.

Future retrieval should respect document types, semantic relationships, and chunk boundaries.

## Translation Policy

Translation should remain a controlled workflow.

Future translation implementation should support:

- Google Cloud Translation configuration;
- glossary use;
- batching;
- cache by hash;
- deduplication;
- pending/running/done/failed statuses;
- resumability;
- cost limits per batch;
- validation before and after translation.

Do not run large-scale translation before storage policy, chunk builder design, and pilot criteria are defined.

## Structural Policy

D1 through D4 are subphases of D — Structural Discovery And Chunking Policy.

Blueprint v1.1 is the current policy baseline:

- `interrogation_protocol`: `question_answer_block`;
- `confrontation_protocol`: `confrontation_exchange`;
- `session_transcript`: `speaker_turn`;
- `conversation_recording`: `conversation_segment`;
- `special_report`: `document_package`.

`special_report` requires package detection and attachment-first strategy before chunking.

## Governance Policy

The repository already has local Git commits for inventory and documentation milestones.

Do not manually reorganize files. Physical restructuring should happen only after:

- documentation is committed;
- `gh` or another GitHub workflow is installed and configured;
- a private repository exists;
- the current baseline is pushed;
- a scripted migration plan is written and reviewed.

Do not run `git add` or commit as part of documentation review unless explicitly requested.
