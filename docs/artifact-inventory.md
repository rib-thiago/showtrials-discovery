# Artifact Inventory

## Purpose

This document maps the major artifact families in the ShowTrials Discovery repository. It is based on current inventory files and the methodological sequence in [methodological-timeline.md](methodological-timeline.md).

## Snapshot Counts

- `repo-current-filelist.txt`: 4780 files.
- `repo-current-scripts.txt`: 101 Python scripts.
- `repo-current-tsvs.txt`: 162 TSV files.
- `repo-current-reports-txt.txt`: 101 TXT reports.

## A — HTML, Curl, And Source Inspection

Visible artifact families include:

- URL and sitemap/crawl files such as `crawl-urls.txt`, `sitemap-urls.txt`, and `wp-sitemap.xml`;
- local source samples such as `doc-8863.txt` and `doc-8863.md`;
- source inspection scripts and early audit scripts.

The methodological timeline records multiple HTML samples, curl tests, and analysis of documentary content versus page noise.

TODO: Identify the exact retained curl command logs or HTML sample filenames if they exist outside the current visible names.

## B — JSON, Pages, Posts, Text Export, And Search

Visible artifact families include:

- JSON/page/post artifacts such as `pages-json`, `posts-json`, `posts-json-embed`, `pages-page-1.json`, and `posts-page-1.json`;
- taxonomy JSON such as `showtrials_categories.json`, `showtrials_tags.json`, and `showtrials_users.json`;
- text and Markdown export directories such as `export-txt`, `export-md`, and `export-test`;
- export scripts such as `showtrials-export-texts.py`;
- search scripts such as `showtrials-search.py`, `showtrials-search-v2.py`, and `search-showtrials.py`;
- search artifacts such as `showtrials_search_corpus.tsv`, search reports, and search v2 validation outputs.

Search belongs to early corpus exploration. It is not a late RAG artifact.

## C — Catalog, Metadata, And Documentary Taxonomy

Visible artifact families include:

- `showtrials_master_catalog.tsv`;
- master catalog reports;
- document indexes;
- page hierarchy and page link artifacts;
- document collection artifacts;
- date audit artifacts;
- post metadata artifacts;
- document type v1, v2, v3, and v4 TSVs;
- document type comparison artifacts;
- document type validation artifacts.

`document_type` is a core downstream field for search, sizing, translation planning, package analysis, and chunking policy.

## E — Semantic Layer

Visible artifact families include:

- canonical people;
- literal people;
- aliases;
- truncated person candidates;
- person normalization and merge candidates;
- organizations;
- organization families;
- organization hierarchy;
- roles;
- positions;
- processes;
- process layers;
- process profiles;
- person, organization, and process matrices;
- semantic baseline and semantic layer inventories.

These artifacts support future evidence-oriented retrieval, but their metrics require historical interpretation.

## G — Glossary And Translation Terminology

Visible artifact families include:

- glossary seeds;
- glossary v1;
- G3 enrichment artifacts;
- G4 expansion artifacts;
- G4.1 refinement artifacts;
- review TSVs;
- validation reports;
- freeze-readiness reports;
- `showtrials_google_translate_glossary_ru_en_v1.tsv`.

This family exists to control terminology before paid translation.

## T — Translation Cost And Operational Planning

Visible artifact families include:

- translation cost by document, document type, and process;
- translation cost reports;
- translation profile artifacts;
- D1 sizing and chunking diagnostics.

The timeline also records operational requirements that future scripts should support: batching, hash cache, deduplication, pending/running/done/failed status queues, resumability, cost limits per batch, validation before and after translation, and future relation to Toolbox-style `run-jobs` and pipelines.

## D — Structural Discovery And Chunking Policy

Visible artifact families include:

- D1 corpus sizing TSVs and reports;
- D2 structural chunking by document and by type;
- D2 examples and validation;
- D2.1 structural sample indexes and reports;
- D2.2 structural review indexes and reports;
- chunking blueprint v1 and v1.1;
- chunking policy v1.1;
- blueprint validation artifacts.

## D — Packages And Attachments

Visible artifact families include:

- special report package diagnostics;
- package summary and examples;
- attachment matrix;
- attachment taxonomy D3.1A;
- attachment taxonomy refinement D3.1B;
- validation reports.

These artifacts support the policy that `special_report` is a `document_package` and requires attachment-first handling.

## R — Repository Governance

Visible artifact families include:

- `repo-current-filelist.txt`;
- `repo-current-scripts.txt`;
- `repo-current-tsvs.txt`;
- `repo-current-reports-txt.txt`;
- Markdown documentation;
- `.gitignore` policy;
- existing local Git commits.

## Versioning Policy Summary

Versionable:

- scripts;
- derived TSVs;
- TXT reports;
- validation outputs;
- inventory snapshots;
- Markdown documentation.

Not versioned for now:

- raw/exported corpus directories and large source exports.

TODO: Define the final raw corpus storage policy before any repository restructuring.
