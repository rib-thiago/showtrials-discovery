# Discoveries By Phase

## 0. Collection And Export

The repository contains URL lists, exported text references, and scripts for corpus collection/export inspection.

Known status:

- Raw/exported corpus material exists locally.
- Raw/exported corpus should not be versioned for now.

TODO: Document the exact export command sequence once the workflow is frozen.

## 1. Inventory And Catalog

Inventory and catalog work established the corpus as a set of documents with post IDs, titles, URLs, dates, processes, collections, categories, tags, and text-derived sizing.

Current inventory snapshot:

- 4780 files in `repo-current-filelist.txt`.
- 101 Python scripts.
- 162 TSV artifacts.
- 101 TXT reports.

## 2. Entities, People, Organizations, Processes

The repository includes artifacts for:

- Canonical people.
- Literal people.
- Person aliases.
- Organizations.
- Organization families.
- Organization hierarchy.
- Process layers and profiles.
- Roles and positions.

TODO: Summarize final entity counts from the relevant reports.

## 3. Translation Glossary

Glossary scripts and TSVs exist for translation preparation. This repository does not currently execute translation as part of the documented discovery baseline.

TODO: Summarize glossary size and freeze-readiness from glossary reports.

## 4. Sizing And Cost

D1 measured:

- 2179 documents.
- 27379787 characters.
- Estimated NMT RU to EN cost: USD 547.60.
- Estimated chunks by profile target: 10023.

Top document types by character volume include:

- `special_report`: 526 documents, 9604474 characters.
- `interrogation_protocol`: 982 documents, 7301792 characters.
- `session_transcript`: 51 documents, 4934530 characters.
- `letter`: 256 documents, 1481811 characters.
- `statement`: 78 documents, 977750 characters.

## 5. Structural Discovery And Chunking

The structural discovery phase established that chunking cannot be size-only. It must respect semantic units.

Confirmed policies:

- `interrogation_protocol`: `question_answer_block`.
- `confrontation_protocol`: `confrontation_exchange`.
- `session_transcript`: `speaker_turn`.
- `conversation_recording`: `conversation_segment`.

## 6. Special Report As Documentary Package

D3 established that `special_report` acts as a documentary package.

D3.1B refined attachment taxonomy:

- `interrogation_protocol`: 448 documents, 85.17%.
- `memo_note`: 51 documents, 9.70%.
- `theses`: 42 documents, 7.98%.
- `list`: 40 documents, 7.60%.
- `reference_note`: 37 documents, 7.03%.
- `statement`: 30 documents, 5.70%.
- `confrontation_protocol`: 17 documents, 3.23%.
- `letter`: 10 documents, 1.90%.
- `diary`: 8 documents, 1.52%.
- `memo`: 4 documents, 0.76%.
- `draft_project`: 1 document, 0.19%.
- `unknown_attachment`: 1 document, 0.19%.

## 7. Chunking Blueprint v1.1

D4 consolidated policy into `showtrials_chunking_blueprint_v1_1.tsv` and `showtrials_chunking_policy_v1_1.txt`.

Validation result:

- 35 document types.
- `FAIL=0`.
- `WARN=24`, expected for document types still requiring future review.

