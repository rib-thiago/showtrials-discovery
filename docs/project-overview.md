# Project Overview

## Executive Summary

ShowTrials Discovery is a documentary engineering project focused on understanding, organizing, and preparing the ShowTrials corpus for future translation, retrieval, and knowledge-system applications.

The project does not begin with translation.

It does not begin with embeddings.

It does not begin with databases.

Instead, it begins with understanding.

The central premise of the repository is that large historical corpora must be understood before they can be transformed.

This repository therefore serves as the discovery, analysis, and policy layer for future engineering work.

---

## The Corpus Problem

The ShowTrials corpus contains thousands of historical documents originating from a politically and historically complex documentary environment.

The corpus includes multiple documentary forms, including:

* interrogation protocols;
* confrontation protocols;
* session transcripts;
* conversation recordings;
* statements;
* letters;
* memoranda;
* reference notes;
* lists;
* special reports;
* and other supporting documentary materials.

At first glance, these documents appear to be simply large quantities of text.

Investigation demonstrated that this assumption is incorrect.

The corpus possesses:

* documentary structure;
* semantic structure;
* procedural structure;
* institutional structure;
* evidentiary structure.

Understanding these structures became the primary objective of the repository.

---

## Repository Mission

The mission of ShowTrials Discovery is to transform a large historical corpus into a documented and measurable knowledge asset.

This transformation occurs through evidence-producing phases rather than direct implementation.

The repository seeks to answer questions such as:

* What documents exist?
* How many documents exist?
* Which document types dominate the corpus?
* Which people and organizations appear?
* Which historical processes are represented?
* How should documents be translated?
* How should documents be chunked?
* How should documentary packages be represented?
* How should future retrieval systems interact with documentary evidence?

---

## Architectural Philosophy

The repository follows a philosophy of:

**Evidence Before Implementation**

Rather than immediately building production systems, the project prioritizes:

1. discovery;
2. measurement;
3. validation;
4. policy;
5. implementation.

This philosophy has influenced every major decision made so far.

Examples include:

* glossary development before translation;
* sizing before budgeting;
* structural discovery before chunking;
* package analysis before attachment handling;
* blueprint creation before chunk-builder implementation.

---

## Major Project Domains

### Corpus Discovery

Corpus discovery establishes the existence, scope, and composition of the document collection.

Outputs include:

* inventories;
* catalogs;
* metadata reports;
* corpus statistics.

---

### Documentary Taxonomy

Documentary taxonomy identifies and validates document families.

The taxonomy layer allows later processing to become document-aware rather than text-only.

This classification work directly supports:

* search;
* chunking;
* translation;
* retrieval.

---

### Semantic Layer

The semantic layer models relationships across the corpus.

Artifacts include:

* people;
* aliases;
* organizations;
* organization families;
* processes;
* roles;
* positions;
* documentary relationships.

This layer enables future evidence-oriented retrieval.

---

### Search

Search has evolved into a strategic component of the repository.

The project already includes a second-generation search implementation and associated validation artifacts.

The objective is not merely keyword lookup.

The objective is retrieval informed by:

* metadata;
* document types;
* semantic entities;
* documentary structure.

Search acts as a bridge between corpus discovery and future retrieval systems.

---

### Translation Preparation

Translation preparation includes:

* glossary generation;
* glossary validation;
* glossary freeze-readiness;
* cost estimation;
* translation profiles.

The repository currently prepares for translation rather than executing translation at scale.

---

### Structural Discovery

Structural discovery investigates how documents are organized internally.

A major finding of this work is that chunking cannot be performed safely using size limits alone.

Document-native structure must be preserved.

Examples include:

* question-and-answer exchanges;
* speaker turns;
* documentary sections;
* package boundaries.

---

### Documentary Package Analysis

One of the most important discoveries in the repository is that special reports behave as documentary packages rather than simple documents.

This finding significantly changed the future architecture of:

* chunking;
* translation;
* retrieval;
* citation.

---

### Chunking Policy

Structural discoveries were consolidated into chunking blueprint v1.1.

This blueprint defines canonical semantic units that future chunk builders should preserve.

The blueprint represents policy rather than implementation.

---

## Current Quantitative Baseline

The current documented baseline includes:

* 2,179 corpus documents;
* approximately 27.4 million characters;
* approximately 10,023 estimated chunks;
* approximately USD 547.60 estimated NMT translation cost;
* 35 document types represented in blueprint v1.1;
* 101 Python scripts;
* 162 TSV artifacts;
* 101 TXT reports.

These measurements provide the foundation for future engineering decisions.

---

## Most Important Discoveries

Several discoveries fundamentally altered project direction.

### Special Reports Are Documentary Packages

Special reports typically contain attached documentary evidence and therefore cannot be treated as simple documents.

### Chunking Must Preserve Semantic Units

Document structure must determine chunk boundaries.

### Translation Requires Terminology Control

Glossary work must precede large-scale translation.

### Search Depends On Structure

Search quality improves when retrieval incorporates documentary structure and semantic context.

### Complexity Is Concentrated

Although many document types exist, a smaller set of dominant structures accounts for most future engineering effort.

---

## Current Status

The repository has completed its initial discovery cycle.

It now contains:

* corpus inventories;
* documentary taxonomy;
* semantic layers;
* search infrastructure;
* glossary artifacts;
* sizing and cost analysis;
* structural discovery;
* package analysis;
* attachment taxonomy;
* chunking blueprint policy.

The repository possesses enough evidence to begin formal engineering design.

---

## Relationship To Future Systems

ShowTrials Discovery is not the final system.

It is the foundation upon which future systems will be built.

Expected future systems include:

* chunk builders;
* translation pipelines;
* SQLite persistence layers;
* retrieval systems;
* evidence-oriented RAG systems.

Those systems should consume discoveries produced by this repository rather than bypass them.

The purpose of ShowTrials Discovery is to ensure that future implementations are informed by evidence rather than assumptions.
