# ShowTrials Discovery

ShowTrials Discovery is a documentary engineering and corpus-discovery repository for the ShowTrials corpus. It records how the corpus was inspected, exported, searched, cataloged, classified, measured, and prepared for future chunking and translation work.

This is not a production application yet. It is a research and engineering workspace containing scripts, derived TSVs, reports, inventories, validation outputs, and policy documents.

For the full project narrative, see [docs/methodological-timeline.md](docs/methodological-timeline.md). That timeline is the canonical account of the project sequence.

## Current Baseline

- Inventory snapshot: 4780 files.
- Python scripts: 101.
- TSV artifacts: 162.
- TXT reports: 101.
- Corpus baseline: 2179 documents.
- Corpus size measured in D1: 27379787 characters, about 27.4M.
- Initial estimated NMT RU to EN cost: about USD 547.60.
- Estimated chunks by profile target: 10023.
- Chunking blueprint v1.1 covers 35 document types.

The raw/exported corpus should not be versioned for now. Scripts, derived TSVs, reports, inventories, validation outputs, and Markdown documentation can be versioned.

## Methodological Sequence

The project did not begin with D1 to D4. D1 to D4 are subphases of the D-series structural discovery and chunking policy work.

The global sequence is:

- A — Site Reconnaissance And Extraction Strategy.
- B — JSON Corpus, Text Export, And Local Search.
- C — Catalog, Metadata, And Documentary Taxonomy.
- E — Entity, People, Organization, Process, And Semantic Layers.
- G — Glossary And Translation Terminology.
- T — Translation Cost And Operational Planning.
- D — Structural Discovery And Chunking Policy.
- R — Repository Governance, Git, Documentation, And GitHub Preparation.

Early work included inspection of multiple HTML samples, curl tests, identification of documentary content versus page noise, and a decision to prefer WordPress/JSON structured data over fragile HTML scraping. The project then built local JSON/page/post artifacts, text and Markdown exports, and local search tooling. Search and search v2 are exploration tools for the local corpus, not a late RAG feature.

## Key Discoveries

- Document type is a core property used by search, sizing, translation planning, package analysis, and chunking policy.
- Frequency and centrality metrics in entity layers require historical interpretation; they do not automatically prove causal or historical centrality.
- Glossary work was advanced before paid translation to reduce terminology ambiguity and downstream waste.
- Translation planning requires batching, hash-based caching, deduplication, resumable status queues, cost limits, and validation before and after translation.
- `special_report` is a `document_package`, not a simple document.
- `interrogation_protocol` uses `question_answer_block`.
- `confrontation_protocol` uses `confrontation_exchange`.
- `session_transcript` uses `speaker_turn`.
- `conversation_recording` uses `conversation_segment`.
- `special_report` contains `interrogation_protocol` attachments in 448 cases, 85.17%.
- D4 validated chunking blueprint v1.1 across 35 document types with `FAIL=0`; the 24 warnings are expected future-review flags.

## Documentation

- [Methodological timeline](docs/methodological-timeline.md)
- [Project overview](docs/project-overview.md)
- [Project history](docs/project-history.md)
- [Discoveries by phase](docs/discoveries-by-phase.md)
- [Artifact inventory](docs/artifact-inventory.md)
- [Repository policy](docs/repository-policy.md)
- [Roadmap](docs/roadmap.md)

## Operating Rules

Do not move files manually during discovery work. Do not reorganize directories without a scripted migration plan. Do not alter input TSVs, scripts, reports, or raw corpus exports while producing derived diagnostics or documentation.

The next technical design step is C1 Chunk Builder Design. Governance next steps include committing documentation, configuring `gh`, creating a private GitHub repository, pushing the current baseline, and only then planning any physical restructuring by script.
