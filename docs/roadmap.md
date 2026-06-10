# Roadmap

## Immediate Next Steps

1. Commit the initial documentation.
2. Install and configure `gh` or another approved GitHub workflow.
3. Create a private repository.
4. Push the initial repository state.
5. Plan physical repository restructuring by script, not manually.

## Near-Term Engineering

After documentation and version control are stable:

- Design the Chunk Builder using blueprint v1.1.
- Plan a translation pilot.
- Decide raw/exported corpus storage policy.
- Prepare future SQLite migration design.
- Prepare future RAG layer design.

## Chunk Builder Design

The future chunk builder should use semantic units from `showtrials_chunking_blueprint_v1_1.tsv`.

Do not start with size-only chunking. Size limits should be applied after structural units are identified.

## Translation Pilot

The translation pilot should use:

- `translation_ready=yes` types first.
- `special_report` only with attachment-first handling.
- Cost controls based on D1 sizing and v1.1 chunking policy.

## SQLite Migration

SQLite migration should be planned after the document model is stable. It should preserve:

- Document metadata.
- Document type.
- Structural chunk unit.
- Package/attachment relations.
- Validation status.

## Future RAG Layer

Future retrieval should cite documentary units, not arbitrary text spans. The v1.1 policy is intended to support cleaner retrieval over Q/A blocks, confrontation exchanges, speaker turns, conversation segments, and special report attachments.

## Explicit Non-Goals For Now

- No chunk builder implementation yet.
- No translation execution yet.
- No embeddings yet.
- No RAG layer yet.
- No SQLite migration yet.
- No manual physical reorganization.

