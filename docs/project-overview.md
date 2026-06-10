# Project Overview

ShowTrials Discovery is a documentary engineering workspace for the ShowTrials corpus. It exists to turn a large set of exported historical documents into a well-understood corpus with explicit metadata, document types, structural policies, and future-ready translation/retrieval assumptions.

The repository currently emphasizes discovery rather than production serving. It contains scripts, TSV outputs, TXT reports, and policy documents produced through iterative analysis.

## Scope

In scope:

- Corpus inventory and cataloging.
- Document type classification.
- Entity and process discovery.
- Translation glossary preparation.
- Sizing, chunking, and cost diagnostics.
- Structural discovery for document-specific chunking.
- Analysis of `special_report` as documentary package.
- Chunking blueprint policy consolidation.

Out of scope for the current state:

- Production chunk builder.
- Translation execution.
- Embedding generation.
- RAG implementation.
- SQLite migration.
- Repository reorganization by manual moves.

## Current Corpus Baseline

D1 measured:

- 2179 documents.
- 27379787 characters, about 27.4M.
- Estimated NMT RU to EN cost of about USD 547.60.
- 10023 estimated chunks by profile target.

## Structural Baseline

The current chunking policy is v1.1. It treats document-native semantic units as the basis for future chunking:

- Q/A pairs for interrogation protocols.
- Confrontation exchanges for confrontation protocols.
- Speaker turns for session transcripts.
- Timestamp/event segments for conversation recordings.
- Attachments inside a document package for special reports.

