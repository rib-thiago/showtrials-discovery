# Project History

This repository grew through a discovery sequence that prioritized evidence over premature implementation.

## Phase 0: Collection And Export

Initial work collected URLs, inspected WordPress/post metadata, and exported document text. The raw/exported corpus is useful for local discovery but should not be versioned for now.

## Phase 1: Inventory And Catalog

The project built corpus inventories, master catalog TSVs, document indexes, collection summaries, process summaries, and audit reports. These artifacts established the basic document universe used by later phases.

## Phase 2: Entities, People, Organizations, Processes

The repository includes scripts and TSVs for canonical people, literal people, organization indexes, organization families, process layers, process profiles, roles, positions, aliases, and entity cleanup.

## Phase 3: Translation Glossary

Translation glossary work produced seed and canonical glossary artifacts. This phase prepared terminology for future translation but did not execute translation in the current documentation pass.

## Phase 4: Sizing And Cost

D1 established the corpus sizing baseline:

- 2179 documents.
- 27379787 characters.
- Estimated NMT cost of USD 547.60.
- 10023 estimated chunks by profile target.

The D1 report also identified the highest-impact document types by character volume, including `special_report`, `interrogation_protocol`, `session_transcript`, `letter`, and `statement`.

## Phase 5: Structural Discovery And Chunking

D2 and D2.2 explored structural samples and corrected an important false-positive risk: lexical occurrences such as words for question/answer inside text must not be treated as proof of real Q/A structure.

D2.2 produced review-oriented outputs rather than automatic final decisions.

## Phase 6: Special Report As Documentary Package

D3.1 analyzed `special_report` as a package. D3.1A normalized attachment relations, and D3.1B refined the taxonomy.

Key result:

- `special_report` contains `interrogation_protocol` attachments in 448 cases, 85.17%.

## Phase 7: Chunking Blueprint v1.1

D4 consolidated the structural discoveries into chunking blueprint v1.1. The validation report shows:

- 35 document types.
- `FAIL=0`.
- 24 expected warnings for types that remain `translation_ready=review_required`.

