# ShowTrials Discovery

ShowTrials Discovery is a repository for corpus discovery and documentary engineering around the ShowTrials text corpus. Its purpose is to document, measure, classify, and prepare the corpus for later chunking, translation, database migration, and retrieval work.

This repository is not yet the production corpus application. It contains scripts, derived TSVs, reports, diagnostics, and policy documents that explain how the corpus should be handled.

## Current State

- Inventory snapshot: 4780 files.
- Python scripts: 101.
- TSV artifacts: 162.
- TXT reports: 101.
- Corpus measured in D1: 2179 documents.
- Corpus size: 27379787 characters, about 27.4M characters.
- Initial estimated NMT cost: about USD 547.
- Estimated chunks by profile target: 10023.
- Document types in chunking blueprint v1.1: 35.

The raw/exported corpus should not be versioned for now. Scripts, derived TSVs, review outputs, reports, and Markdown documentation can be versioned.

## Key Discoveries

- `special_report` is a `document_package`, not a simple document.
- `interrogation_protocol` uses `question_answer_block`.
- `confrontation_protocol` uses `confrontation_exchange`.
- `session_transcript` uses `speaker_turn`.
- `conversation_recording` uses `conversation_segment`.
- `special_report` contains `interrogation_protocol` attachments in 448 cases, 85.17%.
- D4 validated chunking blueprint v1.1 across 35 document types with `FAIL=0`; the 24 warnings are expected future-review flags.

## Documentation

- [Project overview](docs/project-overview.md)
- [Project history](docs/project-history.md)
- [Discoveries by phase](docs/discoveries-by-phase.md)
- [Artifact inventory](docs/artifact-inventory.md)
- [Repository policy](docs/repository-policy.md)
- [Roadmap](docs/roadmap.md)

## Operating Rules

Do not move files manually during discovery work. Do not reorganize directories without a scripted migration plan. Do not alter input TSVs or raw corpus exports while producing derived diagnostics.

Future physical restructuring should be planned and executed by script, after documentation and version control are in place.

