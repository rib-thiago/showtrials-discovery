# Roadmap

## Purpose

This roadmap describes the expected sequence after the current discovery baseline. It does not replace [methodological-timeline.md](methodological-timeline.md); it builds on it.

The repository has completed broad discovery across A/B/C/E/G/T/D and is now in R — Repository Governance, Git, Documentation, And GitHub Preparation.

## Immediate Governance Steps

1. Commit the documentation updates.
2. Install and configure `gh` or an equivalent approved GitHub workflow.
3. Create a private GitHub repository.
4. Push the current baseline.
5. Define raw/exported corpus storage policy.
6. Plan physical repository restructuring by script, not manually.

Do not reorganize the repository by hand.

## Next Technical Step: C1 Chunk Builder Design

C1 is the next technical design phase.

Objective:

- design a chunk builder that implements blueprint v1.1;
- define inputs, outputs, processing stages, validation rules, and metadata;
- preserve semantic units and package boundaries;
- support resumable processing;
- support future translation workflows.

C1 is design first. It should not begin by writing a size-only chunker.

## After C1

After chunk builder design and storage policy are clear, later phases can be planned.

Recommended order:

1. C1 Chunk Builder Design.
2. Raw/exported corpus storage policy.
3. Chunk builder implementation plan.
4. Translation pilot design.
5. Persistence strategy.
6. SQLite design.
7. Search/retrieval evolution.
8. Future RAG layer design.

Translation, SQLite, and RAG should not jump ahead of C1 and storage policy.

## Translation Pilot Planning

The future translation pilot should use:

- blueprint v1.1;
- glossary artifacts;
- Google Translate glossary preparation;
- batching;
- cache by hash;
- deduplication;
- pending/running/done/failed queues;
- resumability;
- cost limits per batch;
- validation before and after translation.

The pilot should validate assumptions rather than maximize throughput.

## Persistence And SQLite

SQLite remains a future design topic. It should not be implemented before the document/chunk/package model is stable.

Likely future entities include:

- documents;
- document types;
- packages;
- attachments;
- chunks;
- people;
- organizations;
- processes;
- glossary terms;
- translations.

TODO: Define persistence requirements after C1.

## Search And Future RAG

Search already exists as a local exploration layer and search v2 exists as an evolution of that layer.

Future retrieval should return meaningful documentary units such as:

- Q/A blocks;
- confrontation exchanges;
- speaker turns;
- conversation segments;
- package attachments;
- list items.

RAG should remain a future layer until chunking, storage, and retrieval design are stable.

## Explicit Non-Goals For Now

- No chunk builder implementation yet.
- No large-scale translation execution yet.
- No embeddings yet.
- No RAG layer yet.
- No SQLite migration yet.
- No manual physical reorganization.
