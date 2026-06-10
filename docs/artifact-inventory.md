# Artifact Inventory

This document summarizes the current repository artifact inventory. It is based on the generated inventory files in the repository root.

## Snapshot Counts

- `repo-current-filelist.txt`: 4780 files.
- `repo-current-scripts.txt`: 101 Python scripts.
- `repo-current-tsvs.txt`: 162 TSV files.
- `repo-current-reports-txt.txt`: 101 TXT reports.

## Important Policy And Report Files

- `showtrials_chunking_policy_v1_1.txt`
- `showtrials_chunking_blueprint_v1_1.tsv`
- `showtrials_chunking_blueprint_v1_1_report.txt`
- `showtrials_chunking_blueprint_v1_1_validation_report.txt`
- `showtrials_attachment_taxonomy_d3_1b.tsv`
- `showtrials_attachment_taxonomy_refinement_d3_1b.tsv`
- `showtrials_attachment_taxonomy_refinement_d3_1b_report.txt`
- `showtrials_corpus_sizing_chunking_d1_report.txt`

## Versionable Artifacts

These can be versioned:

- Python scripts.
- Derived TSVs.
- TXT reports.
- Markdown documentation.
- Inventory snapshots.

## Not Yet Versioned

The raw/exported corpus should not be versioned for now. It may be large, may include generated exports, and may need a separate storage policy.

TODO: Decide whether future raw corpus storage belongs in Git LFS, object storage, release artifacts, or a separate private data repository.

## Directory Policy

Do not manually move or reorganize files during documentation or discovery phases. Any future physical restructuring should be scripted, reviewed, and validated.

