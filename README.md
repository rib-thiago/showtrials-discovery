ShowTrials Discovery

ShowTrials Discovery is a documentary engineering and corpus-discovery repository for the ShowTrials corpus. Its purpose is to transform a large exported collection of historical documents into a measured, classified, searchable, and semantically understood corpus ready for later chunking, translation, database migration, and retrieval work.

This is not a production application yet. It is a research and engineering workspace containing scripts, derived TSVs, reports, diagnostics, inventories, validation outputs, and policy documents.

Why This Repository Exists

The long-term goal is to prepare the ShowTrials corpus for controlled Russian-to-English translation while preserving documentary meaning. The broader goal is to support future retrieval and RAG over coherent historical evidence units, not arbitrary text fragments.

The central problem is that this corpus cannot be processed safely by size alone. Many documents have internal legal, procedural, conversational, or archival structure. If that structure is ignored, future translation and retrieval would split questions from answers, speakers from statements, cover notes from attachments, and documentary packages from the records they contain.

This repository exists to answer, with evidence:

* what documents exist in the corpus;
* how large the corpus is;
* what document types dominate it;
* which people, organizations, processes, roles, and taxonomy terms appear;
* which terms require glossary control;
* how search can be improved beyond plain text lookup;
* how translation cost should be estimated;
* which structural units should be preserved during chunking;
* how special reports should be treated as documentary packages;
* which policy should guide future chunk builders, translation pilots, and retrieval layers.

Strategic Goal

The repository exists to progressively transform a large historical corpus into a structured knowledge base.

Rather than jumping directly to translation, embeddings, databases, or RAG, the project follows an evidence-first methodology:

1. discover and export the corpus;
2. catalog documents and metadata;
3. classify document types;
4. build entity, organization, process, and role layers;
5. implement and validate search capabilities;
6. normalize translation terminology through glossary work;
7. estimate translation scale and cost;
8. discover document-native structure;
9. define semantic chunking policy;
10. prepare future translation, persistence, and retrieval workflows.

Each phase produces scripts, TSV artifacts, reports, validation outputs, and policies that become inputs for later phases.

Current State

Current repository inventory snapshot:

* Files listed in inventory: 4,780.
* Python scripts: 101.
* TSV artifacts: 162.
* TXT reports: 101.
* Documented corpus baseline: 2,179 documents.
* Corpus size measured in D1: 27,379,787 characters, approximately 27.4M.
* Initial estimated NMT RU to EN cost: approximately USD 547.60.
* Estimated chunks by profile target: 10,023.
* Document types in chunking blueprint v1.1: 35.

The raw and exported corpus should not be versioned for now. Scripts, derived TSVs, review outputs, reports, inventories, and Markdown documentation can be versioned.

Methodological Sequence

The project developed through an evidence-producing sequence.

0. Collection and export

The first layer collected URLs, inspected pages and posts, exported document text, and produced local corpus material for discovery work. This includes local export directories and crawl artifacts that should remain outside Git for now.

1. Inventory and catalog

The project then created inventories, document indexes, metadata reports, collection summaries, date audits, taxonomy inspections, and a master catalog. This established the working document universe used by all later phases.

2. Document types

Document type classification evolved through multiple versions. The current document type layer supports later cost analysis, chunking policy, special report analysis, and translation planning.

3. Entities, people, organizations, and processes

The semantic layer includes canonical people, literal people, person aliases, organizations, organization families, hierarchy artifacts, roles, positions, process layers, process profiles, and person-organization-process matrices.

This layer matters because future search, retrieval, and RAG should not rely only on raw text matches. They should also understand who appears, which institutions are involved, and which political or judicial process a document belongs to.

4. Search

The repository already contains a search mechanism and a second-generation search implementation. The search work evolved from basic text lookup toward a richer documentary search layer backed by corpus metadata and semantic artifacts.

Relevant files include search scripts, search corpus diagnostics, and search validation outputs. The current search layer is not the final RAG system, but it is an important intermediate capability. It allows the corpus to be queried locally while the project develops better document types, entity layers, glossary normalization, and future chunking policy.

The strategic direction is evidence-oriented retrieval: search should eventually return meaningful documentary units, not just arbitrary text hits. The D1 to D4 work directly supports that goal by clarifying document types, structural units, and package boundaries.

5. Translation glossary

Glossary work produced seed terms, canonicalized glossary artifacts, review files, freeze-readiness diagnostics, and Google Translate glossary preparation. This phase exists to reduce ambiguity and improve consistency before any paid translation pilot.

The glossary is not a decorative artifact. It is part of the cost-control and quality-control strategy for future Russian-to-English translation.

6. Sizing and cost analysis

D1 established the corpus sizing baseline: 2,179 documents, 27,379,787 characters, approximately USD 547.60 in initial estimated NMT cost, and 10,023 estimated chunks by profile target.

This changed the project from speculation to measurement. It also showed that translation must be staged, budgeted, resumable, and guided by document structure.

7. Structural chunking discovery

D2 showed that chunking cannot be size-only. The corpus contains different documentary structures, and those structures must guide how text is divided.

A key correction was the rejection of lexical false positives. A document that merely contains words equivalent to question or answer is not necessarily a question-and-answer document. Structural evidence must come from the actual form of the document.

8. Special report package analysis

D3 established that special reports are usually documentary packages rather than simple documents. This was one of the most important methodological discoveries in the project.

A special report often contains a cover communication plus one or more attached documentary units. Treating the entire package as a single flat document would mix different evidentiary units and damage translation, retrieval, and citation quality.

9. Chunking blueprint v1.1

D4 consolidated the structural discoveries into chunking blueprint v1.1. The blueprint defines document-native semantic units and records which types are ready for future translation-oriented chunking.

The blueprint does not implement chunking yet. It defines the policy that a future chunk builder should follow.

Core Discoveries

The corpus is structurally concentrated

Although the repository tracks 35 document types in the current blueprint, the practical translation and chunking problem is dominated by a smaller set of high-impact structures:

* special reports;
* interrogation protocols;
* session transcripts;
* letters;
* statements;
* conversation recordings;
* confrontation protocols.

This means the project does not need 35 equally complex chunkers before meaningful progress. It needs strong policies for the dominant types and conservative fallback handling for residual types.

Special reports are documentary packages

The most important structural discovery is that special reports are not simple documents. They usually act as documentary packages made of a cover document plus one or more attached documentary units.

D3.1B showed that special reports contain interrogation protocol attachments in 448 cases, or 85.17%.

The refined attachment taxonomy includes:

Attachment type	Documents	Percentage
interrogation_protocol	448	85.17%
memo_note	51	9.70%
theses	42	7.98%
list	40	7.60%
reference_note	37	7.03%
statement	30	5.70%
confrontation_protocol	17	3.23%
letter	10	1.90%
diary	8	1.52%
memo	4	0.76%
draft_project	1	0.19%
unknown_attachment	1	0.19%

This discovery changes the future pipeline. Special reports require attachment detection before chunking.

Chunking must preserve semantic units

The current blueprint v1.1 defines document-native units:

Document type	Primary unit
interrogation_protocol	question_answer_block
confrontation_protocol	confrontation_exchange
session_transcript	speaker_turn
conversation_recording	conversation_segment
special_report	document_package
letter	letter_section
statement	statement_section
memo_note	memo_section
reference_note	reference_section
list	list_item_group

Size limits still matter, but only after structural boundaries are identified.

Validation Status

The current D4 blueprint consolidation produced:

* showtrials_chunking_blueprint_v1_1.tsv
* showtrials_chunking_policy_v1_1.txt
* showtrials_chunking_blueprint_v1_1_report.txt
* showtrials_chunking_blueprint_v1_1_validation.tsv
* showtrials_chunking_blueprint_v1_1_validation_report.txt

Validation result:

* 35 document types checked.
* FAIL=0.
* WARN=24.

The 24 warnings are expected. They mark residual document types with translation_ready=review_required. They are not structural failures.

Repository Contents

The current repository contains several artifact families.

Scripts

Python and shell scripts cover:

* crawling and export inspection;
* metadata inventory;
* corpus statistics;
* document type classification;
* entity extraction and cleanup;
* people and person alias handling;
* organization and process profiling;
* local search and search validation;
* translation glossary preparation;
* translation cost analysis;
* structural chunking discovery;
* special report package analysis;
* attachment taxonomy normalization and refinement;
* chunking blueprint planning and validation.

TSV artifacts

Derived TSVs include:

* master catalog and document indexes;
* document type versions and validation files;
* people, organization, process, role, and position matrices;
* search validation outputs;
* translation glossary versions and validation files;
* cost and sizing tables;
* structural chunking diagnostics;
* special report package and attachment matrices;
* chunking blueprint v1 and v1.1.

TXT reports

Reports document each diagnostic, planning, validation, and policy stage.

Important reports and policies include:

* showtrials_corpus_sizing_chunking_d1_report.txt
* showtrials_translation_cost_report.txt
* showtrials_translation_glossary_freeze_readiness_report.txt
* showtrials_search_corpus_report.txt
* showtrials_search_v2_validation_report.txt
* showtrials_structural_chunking_d2_report.txt
* showtrials_special_report_packages_d3_1_report.txt
* showtrials_attachment_taxonomy_refinement_d3_1b_report.txt
* showtrials_chunking_policy_v1_1.txt
* showtrials_chunking_blueprint_v1_1_report.txt

Documentation

* Project overview⁠￼
* Project history⁠￼
* Discoveries by phase⁠￼
* Artifact inventory⁠￼
* Repository policy⁠￼
* Roadmap⁠￼

Repository Policy

Versionable:

* scripts;
* derived TSVs;
* TXT reports;
* validation outputs;
* inventories;
* Markdown documentation.

Not versioned for now:

* raw and exported corpus directories;
* full text corpus TSV;
* structural sample dumps;
* crawler, cache, and runtime folders;
* compressed backup and checkpoint packages.

Ignored examples:

* export-md/
* export-txt/
* pages-json/
* posts-json/
* posts-json-embed/
* showtrials.ru/
* structural_samples_d2_1/
* showtrials_search_corpus.tsv
* crawl-spider.log

The repository should not be physically reorganized by manual file moves. Any restructuring should be planned, scripted, reviewed, validated, and committed separately.

Operating Rules

Current discipline:

* Do not alter input TSVs while generating derived outputs.
* Do not delete generated artifacts without a cleanup plan.
* Do not run translation as part of discovery documentation.
* Do not create embeddings yet.
* Do not implement RAG yet.
* Do not migrate to SQLite yet.
* Do not implement the chunk builder before its design is documented.

Next Steps

Immediate:

1. finish documentation review;
2. commit improved documentation;
3. install and configure GitHub CLI if needed;
4. create a private GitHub repository;
5. push the current documented state.

Near-term:

1. plan repository restructuring via script;
2. design C1, the chunk builder design phase;
3. define raw and exported corpus storage policy;
4. plan translation pilot using translation_ready=yes types first;
5. define future SQLite schema;
6. define future retrieval and RAG evidence model.

Current Non-Goals

This repository currently does not implement:

* production chunking;
* paid translation;
* embedding generation;
* RAG;
* SQLite persistence;
* public corpus distribution.

The present milestone is a documented discovery baseline for future engineering.
