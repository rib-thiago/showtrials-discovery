# Repository Reorganization Plan

## Purpose

This document proposes a physical reorganization of the ShowTrials Discovery repository. It is a plan only. No files have been moved.

The proposed structure follows the methodological sequence in `docs/methodological-timeline.md`: A, B, C, E, G, T, D, and R.

## Constraints

- Do not move files yet.
- Do not alter scripts.
- Do not alter TSVs.
- Do not alter reports.
- Do not alter `.gitignore` as part of this plan.
- Do not stage or commit this plan automatically.
- Exclude raw/exported corpus payloads ignored by `.gitignore`.

## Proposed Top-Level Layout

- `scripts/a-extraction/`
- `scripts/b-json-export-search/`
- `scripts/c-catalog-taxonomy/`
- `scripts/e-semantic-layer/`
- `scripts/g-glossary/`
- `scripts/t-translation-planning/`
- `scripts/d-structural-chunking/`
- `scripts/r-governance/`
- `data/a-extraction/`
- `data/b-json-export-search/`
- `data/c-catalog-taxonomy/`
- `data/e-semantic-layer/`
- `data/g-glossary/`
- `data/t-translation-planning/`
- `data/d-structural-chunking/`
- `data/r-governance/`
- `reports/a-extraction/`
- `reports/b-json-export-search/`
- `reports/c-catalog-taxonomy/`
- `reports/e-semantic-layer/`
- `reports/g-glossary/`
- `reports/t-translation-planning/`
- `reports/d-structural-chunking/`
- `reports/r-governance/`

Markdown documentation remains under `docs/` and may be grouped by phase when it is not a root file. `README.md` and `.gitignore` remain at the repository root.

## Classification Rules

- `.py` and `.sh` files are classified as `scripts`.
- `.tsv` and derived `.json` files are classified as `data`.
- report `.txt` files are classified as `reports`.
- `.md` files are classified as `docs`.
- `repo-current-*` and `repo-file-metadata.tsv` are classified as `governance/inventory`.
- Files and directories ignored as raw/exported corpus payloads by `.gitignore` are excluded from the move map.

## Phase Mapping

- A extraction: site reconnaissance, crawl/source inspection, sitemap and early extraction evidence.
- B json-export-search: JSON/page/post artifacts, text/Markdown export tooling, search and search v2.
- C catalog-taxonomy: master catalog, metadata, document indexes, collections, dates, document type versions, taxonomy.
- E semantic-layer: people, aliases, organizations, roles, positions, processes, profiles, semantic matrices.
- G glossary: glossary seeds, canonicalization, G3, G4, G4.1, review, validation, freeze-readiness, Google Translate glossary preparation.
- T translation-planning: translation cost, profiles, sizing, budgeting and operational planning artifacts.
- D structural-chunking: D1-D4 sizing/chunking, structural samples, special report packages, attachments, blueprint policy.
- R governance: documentation, inventory, `.gitignore`, repository policy, Git/GitHub preparation.

## Commit Strategy

Use `repo-reorganization-commit-groups.tsv` as the proposed commit grouping. The migration should be performed by a script that reads `repo-reorganization-map.tsv`, creates target directories, moves files, and verifies that every source path lands at the proposed path.

Recommended sequence:

1. Governance inventory and docs.
2. A extraction.
3. B JSON/export/search.
4. C catalog/taxonomy.
5. E semantic layer.
6. G glossary.
7. T translation planning.
8. D structural/chunking.
9. Unclassified review, if any remains.

## Counts By Phase

| Phase | Files |
|---|---:|
| A extraction | 6 |
| B json-export-search | 13 |
| C catalog-taxonomy | 99 |
| D structural-chunking | 56 |
| E semantic-layer | 148 |
| G glossary | 34 |
| R governance | 4 |
| T translation-planning | 11 |

## Counts By Artifact Type

| Artifact type | Files |
|---|---:|
| data | 166 |
| docs | 3 |
| governance/inventory | 2 |
| reports | 97 |
| scripts | 103 |

## Counts By Commit Group

| Commit group | Files |
|---|---:|
| a-extraction-docs | 1 |
| a-extraction-reports | 3 |
| a-extraction-scripts | 2 |
| b-json-export-search-data | 5 |
| b-json-export-search-reports | 2 |
| b-json-export-search-scripts | 6 |
| c-catalog-taxonomy-data | 48 |
| c-catalog-taxonomy-reports | 25 |
| c-catalog-taxonomy-scripts | 26 |
| d-structural-chunking-data | 23 |
| d-structural-chunking-reports | 17 |
| d-structural-chunking-scripts | 16 |
| e-semantic-layer-data | 69 |
| e-semantic-layer-reports | 38 |
| e-semantic-layer-scripts | 41 |
| g-glossary-data | 14 |
| g-glossary-reports | 10 |
| g-glossary-scripts | 10 |
| r-governance-docs | 2 |
| r-governance-inventory | 2 |
| t-translation-planning-data | 7 |
| t-translation-planning-reports | 2 |
| t-translation-planning-scripts | 2 |

## Unclassified Files

No versionable files were left unclassified by the current rules.

## Review Notes

- The map is intentionally conservative and does not perform moves.
- Some files may deserve manual review before migration, especially generic one-off outputs.
- The migration script should refuse to overwrite existing files.
- The migration script should produce a before/after manifest and a validation report.
