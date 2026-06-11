# Project Overview

## Mission

ShowTrials Discovery is a documentary engineering project focused on understanding, organizing, searching, measuring, and preparing the ShowTrials corpus for future translation and retrieval work.

The repository is evidence-first. It does not start from translation, embeddings, databases, or RAG. It starts from source inspection, extraction strategy, local export, search, cataloging, taxonomy, semantic layers, glossary work, cost planning, and structural policy.

The canonical historical sequence is documented in [methodological-timeline.md](methodological-timeline.md).

## What The Repository Is

This repository is a discovery and policy workspace. It contains:

- scripts;
- derived TSVs;
- reports;
- inventories;
- validation outputs;
- review artifacts;
- policy documents;
- Markdown documentation.

It is not yet a production corpus application.

## What The Project Has Already Built

The project already includes:

- site reconnaissance and extraction strategy;
- local JSON/page/post artifacts;
- local text and Markdown export;
- local search and search v2;
- master catalog and document indexes;
- document taxonomy v1 through v4;
- entity, people, organization, process, role, position, and semantic layers;
- translation glossary generations through G3, G4, and G4.1;
- Google Translate glossary preparation;
- translation cost and operational planning;
- structural discovery and sample review;
- special report package analysis;
- attachment taxonomy normalization and refinement;
- chunking blueprint v1.1.

Search and export are therefore not future concepts. They are already part of the local discovery workspace.

## Corpus Baseline

The current documented baseline includes:

- 2179 corpus documents;
- 27379787 characters, about 27.4M;
- about 10023 estimated chunks by profile target;
- about USD 547.60 estimated NMT translation cost;
- 35 document types represented in blueprint v1.1;
- 101 Python scripts;
- 162 TSV artifacts;
- 101 TXT reports;
- 4780 files in the current repository inventory.

## Architectural Premises

The project is guided by these premises:

- Use structured JSON/WordPress data when possible instead of fragile HTML scraping.
- Preserve local text/Markdown exports for human inspection.
- Treat search as a corpus exploration tool and a bridge to future retrieval, not as late-stage RAG.
- Use `document_type` as a core property for search, sizing, translation planning, and chunking.
- Interpret entity frequency and centrality cautiously; they are not automatic historical or causal centrality.
- Advance glossary canonicalization before paid translation.
- Treat translation as a resumable, validated, cost-controlled workflow.
- Chunk by document-native semantic units, not by size alone.
- Treat `special_report` as `document_package`.

## Structural Policy Baseline

Blueprint v1.1 currently defines:

| Document type | Primary unit |
|---|---|
| `interrogation_protocol` | `question_answer_block` |
| `confrontation_protocol` | `confrontation_exchange` |
| `session_transcript` | `speaker_turn` |
| `conversation_recording` | `conversation_segment` |
| `special_report` | `document_package` |

For `special_report`, attachment detection occurs before chunking.

## Current Non-Goals

The repository should not yet implement:

- chunk builder execution;
- production translation;
- embeddings;
- RAG;
- SQLite migration;
- manual physical reorganization.

The next technical step is C1 Chunk Builder Design. Governance work should first stabilize documentation, GitHub setup, and storage policy.
