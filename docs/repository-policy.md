# Repository Policy

## Repository Purpose

This repository is for discovery and documentary engineering of the ShowTrials corpus. It records how the corpus was inspected, measured, classified, and prepared for future processing.

## What Can Be Versioned

The following are appropriate to version:

- Scripts used for diagnostics, planning, validation, and reporting.
- Derived TSVs produced by those scripts.
- TXT reports.
- Markdown documentation.
- Inventory snapshots.

## What Should Not Be Versioned Yet

The raw/exported corpus should not be versioned for now.

Reasons:

- It may be large.
- It may be regenerated.
- It may need separate provenance and storage rules.
- The current repository is focused on derived discovery artifacts and policy.

TODO: Define the final raw corpus storage policy.

## Change Discipline

- Do not alter input TSVs while generating derived outputs.
- Do not delete generated artifacts unless a specific cleanup plan exists.
- Do not manually reorganize files.
- Do not alter `.gitignore` as part of documentation-only work.
- Do not implement chunking, translation, embeddings, RAG, or SQLite migration inside documentation tasks.

## Future Restructuring

Physical restructuring should happen only after:

- Documentation is committed.
- GitHub CLI or equivalent remote workflow is installed/configured.
- A private repository exists.
- The current state has been pushed.
- A migration script has been planned and reviewed.

