#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict

BASE = Path("/tmp/showtrials-discovery")

DOCTYPE_COST = BASE / "showtrials_translation_cost_by_document_type.tsv"

OUT_PROFILES = BASE / "showtrials_translation_profiles_v1.tsv"
OUT_GLOSSARY_SEEDS = BASE / "showtrials_translation_glossary_seed_plan_v1.tsv"
OUT_REPORT = BASE / "showtrials_translation_profiles_v1_report.txt"

PROFILE_RULES = {
    "interrogation_protocol": {
        "segmentation_strategy": "protocol_header_then_question_answer_blocks",
        "segment_kinds": "header | question_answer | answer_continuation | signature",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_question_answer_order",
        "translation_notes": "Preserve speaker/question-answer structure. Do not merge separate interrogatory turns.",
    },
    "confrontation_protocol": {
        "segmentation_strategy": "protocol_header_then_alternating_speaker_blocks",
        "segment_kinds": "header | speaker_turn | confrontation_exchange | signature",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_speaker_turn_order",
        "translation_notes": "Preserve confrontation exchanges and speaker attribution.",
    },
    "session_transcript": {
        "segmentation_strategy": "session_header_then_speaker_turns",
        "segment_kinds": "session_header | speaker_turn | procedural_note | resolution",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4200,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_session_sequence",
        "translation_notes": "Prioritize speaker turns. Avoid cutting inside long speeches unless necessary.",
    },
    "special_report": {
        "segmentation_strategy": "classification_recipient_body_attachments",
        "segment_kinds": "classification | sender_recipient | summary | body_paragraph | attachment",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_header_body_attachment_order",
        "translation_notes": "Preserve secrecy marks, sender/recipient lines, and attachment boundaries.",
    },
    "administrative_report": {
        "segmentation_strategy": "header_then_body_paragraphs",
        "segment_kinds": "header | body_paragraph | signature",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_paragraph_order",
        "translation_notes": "Preserve administrative formulae and dates.",
    },
    "telegram": {
        "segmentation_strategy": "whole_document_or_header_body",
        "segment_kinds": "telegram_header | telegram_body | signature",
        "target_chunk_chars": 2500,
        "soft_max_chars": 4000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_telegram_integrity",
        "translation_notes": "Prefer whole-document translation unless over hard limit.",
    },
    "letter": {
        "segmentation_strategy": "salutation_body_signature",
        "segment_kinds": "header | salutation | body_paragraph | signature | postscript",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_letter_structure",
        "translation_notes": "Preserve addressee, salutation, signature, and emotional tone.",
    },
    "correspondence": {
        "segmentation_strategy": "split_individual_letters_then_letter_profile",
        "segment_kinds": "letter_boundary | header | salutation | body_paragraph | signature",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_each_letter_boundary",
        "translation_notes": "Do not merge distinct letters inside correspondence.",
    },
    "memo_note": {
        "segmentation_strategy": "header_body_attachments",
        "segment_kinds": "header | body_paragraph | attachment | signature",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_note_structure",
        "translation_notes": "Preserve memo headers and any attached materials.",
    },
    "statement": {
        "segmentation_strategy": "header_then_numbered_or_paragraph_blocks",
        "segment_kinds": "header | statement_paragraph | numbered_point | signature",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_argument_sequence",
        "translation_notes": "Preserve numbered claims and rhetorical structure.",
    },
    "testimony": {
        "segmentation_strategy": "header_then_narrative_blocks",
        "segment_kinds": "header | testimony_paragraph | continuation | signature",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_testimony_sequence",
        "translation_notes": "Preserve chronology and first-person narrative structure.",
    },
    "indictment": {
        "segmentation_strategy": "sections_charges_numbered_points",
        "segment_kinds": "header | charge_section | numbered_point | conclusion",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_charge_hierarchy",
        "translation_notes": "Preserve legal structure and charge numbering.",
    },
    "verdict_or_sentence": {
        "segmentation_strategy": "sections_findings_sentence",
        "segment_kinds": "header | finding | legal_basis | sentence | conclusion",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_verdict_sequence",
        "translation_notes": "Preserve operative legal language and sentence terms.",
    },
    "list": {
        "segmentation_strategy": "list_items_grouped",
        "segment_kinds": "list_header | list_item_group | list_footer",
        "target_chunk_chars": 1800,
        "soft_max_chars": 3000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_item_order",
        "translation_notes": "Do not break inside individual list items where possible.",
    },
    "questionnaire_response": {
        "segmentation_strategy": "question_answer_pairs",
        "segment_kinds": "question | answer | question_answer_pair",
        "target_chunk_chars": 2500,
        "soft_max_chars": 4000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_question_answer_pairs",
        "translation_notes": "Keep questions attached to corresponding answers.",
    },
    "data_extract": {
        "segmentation_strategy": "rows_or_records",
        "segment_kinds": "record_header | data_record | row_group",
        "target_chunk_chars": 1800,
        "soft_max_chars": 3000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_record_order",
        "translation_notes": "Preserve structured records; avoid prose normalization.",
    },
    "press_summary": {
        "segmentation_strategy": "press_sections_and_paragraphs",
        "segment_kinds": "header | press_item | body_paragraph",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_press_item_order",
        "translation_notes": "Preserve attribution to newspapers/agencies.",
    },
    "article": {
        "segmentation_strategy": "paragraph_blocks",
        "segment_kinds": "headline | paragraph | section",
        "target_chunk_chars": 3500,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_article_order",
        "translation_notes": "Text-flow oriented; preserve headings.",
    },
    "biographical_article": {
        "segmentation_strategy": "paragraph_blocks_with_headings",
        "segment_kinds": "headline | section_heading | paragraph",
        "target_chunk_chars": 3500,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_article_order",
        "translation_notes": "Preserve biographical chronology and headings.",
    },
    "brochure": {
        "segmentation_strategy": "section_headings_and_paragraphs",
        "segment_kinds": "section_heading | paragraph | note",
        "target_chunk_chars": 3500,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_brochure_sections",
        "translation_notes": "Preserve section headings.",
    },
    "speech": {
        "segmentation_strategy": "speech_sections_or_paragraphs",
        "segment_kinds": "speech_header | paragraph | applause_note | conclusion",
        "target_chunk_chars": 3300,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_speech_flow",
        "translation_notes": "Preserve oratorical flow and interruptions.",
    },
    "draft_project": {
        "segmentation_strategy": "draft_sections_numbered_points",
        "segment_kinds": "header | draft_section | numbered_point | note",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_draft_structure",
        "translation_notes": "Preserve draft/project status and numbering.",
    },
    "plan_instruction": {
        "segmentation_strategy": "instruction_points",
        "segment_kinds": "header | instruction_point | numbered_point",
        "target_chunk_chars": 2800,
        "soft_max_chars": 4200,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_instruction_order",
        "translation_notes": "Preserve imperative/instructional wording.",
    },
    "reference_note": {
        "segmentation_strategy": "header_factual_paragraphs",
        "segment_kinds": "header | factual_paragraph | source_note",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_reference_structure",
        "translation_notes": "Preserve factual register.",
    },
    "explanation": {
        "segmentation_strategy": "paragraph_blocks",
        "segment_kinds": "header | explanation_paragraph | signature",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_paragraph_order",
        "translation_notes": "Preserve explanatory sequence.",
    },
    "summary": {
        "segmentation_strategy": "summary_sections_or_paragraphs",
        "segment_kinds": "header | summary_paragraph | conclusion",
        "target_chunk_chars": 3200,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_summary_order",
        "translation_notes": "Preserve concise summary style.",
    },
    "interrogation_extract": {
        "segmentation_strategy": "extract_header_then_question_answer_blocks",
        "segment_kinds": "extract_header | question_answer | excerpt_note",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_excerpt_boundaries",
        "translation_notes": "Preserve extract status and omitted-text markers.",
    },
    "autobiography": {
        "segmentation_strategy": "chronological_paragraph_blocks",
        "segment_kinds": "header | autobiographical_paragraph | date_section",
        "target_chunk_chars": 3300,
        "soft_max_chars": 4500,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_chronology",
        "translation_notes": "Preserve first-person chronology.",
    },
    "plea_pardon": {
        "segmentation_strategy": "petition_structure",
        "segment_kinds": "header | addressee | petition_body | signature",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_petition_structure",
        "translation_notes": "Preserve deferential/legal petition tone.",
    },
    "decree_resolution": {
        "segmentation_strategy": "resolution_points",
        "segment_kinds": "header | resolution_point | signature",
        "target_chunk_chars": 2800,
        "soft_max_chars": 4200,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_resolution_points",
        "translation_notes": "Preserve formal resolution language.",
    },
    "program": {
        "segmentation_strategy": "program_sections",
        "segment_kinds": "header | section | program_point",
        "target_chunk_chars": 3000,
        "soft_max_chars": 4300,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_program_sections",
        "translation_notes": "Preserve programmatic structure.",
    },
    "poem": {
        "segmentation_strategy": "stanzas",
        "segment_kinds": "title | stanza | line_group",
        "target_chunk_chars": 1800,
        "soft_max_chars": 3000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_line_breaks",
        "translation_notes": "Preserve line/stanza structure; translation quality may require manual review.",
    },
    "medical_act": {
        "segmentation_strategy": "medical_form_sections",
        "segment_kinds": "header | observation | conclusion | signature",
        "target_chunk_chars": 2500,
        "soft_max_chars": 4000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_form_structure",
        "translation_notes": "Preserve clinical/formal wording.",
    },
    "search_protocol": {
        "segmentation_strategy": "protocol_header_inventory_signature",
        "segment_kinds": "header | inventory_item | procedural_note | signature",
        "target_chunk_chars": 2500,
        "soft_max_chars": 4000,
        "hard_max_chars": 5000,
        "reassembly_strategy": "preserve_inventory_order",
        "translation_notes": "Preserve inventory/procedural structure.",
    },
}

GLOSSARY_SEED_LAYERS = [
    {
        "layer": "people",
        "source_file": "showtrials_literal_people.tsv",
        "source_field": "person",
        "glossary_kind": "person_name",
        "priority": "high",
        "translation_policy": "curated_english_name_or_transliteration",
        "notes": "Top frequent people first; avoid automatic translation of names.",
    },
    {
        "layer": "organizations",
        "source_file": "showtrials_organizations.tsv",
        "source_field": "organization",
        "glossary_kind": "organization",
        "priority": "high",
        "translation_policy": "canonical_acronym_or_historical_english_name",
        "notes": "NKVD/GUGB/VKP(b)/Central Committee/Politburo need stable forms.",
    },
    {
        "layer": "processes",
        "source_file": "showtrials_processes.tsv",
        "source_field": "process",
        "glossary_kind": "process_name",
        "priority": "high",
        "translation_policy": "short_canonical_english_label",
        "notes": "Use stable labels such as August 1936 Trial, January 1937 Trial, March 1938 Trial.",
    },
    {
        "layer": "roles",
        "source_file": "showtrials_roles_v2.tsv",
        "source_field": "role",
        "glossary_kind": "role_or_label",
        "priority": "medium",
        "translation_policy": "curated_term_translation",
        "notes": "Separate office positions from political/accusatory labels.",
    },
    {
        "layer": "document_types",
        "source_file": "showtrials_document_types_v4.tsv",
        "source_field": "document_type",
        "glossary_kind": "internal_document_type",
        "priority": "low",
        "translation_policy": "internal_label_only",
        "notes": "Mostly for UI/reporting, not necessarily for Google glossary.",
    },
]

def load_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

doctype_rows = load_tsv(DOCTYPE_COST)
profiles = []
missing = []

for r in doctype_rows:
    dt = r["document_type"]
    rule = PROFILE_RULES.get(dt)
    if not rule:
        missing.append(dt)
        rule = {
            "segmentation_strategy": "generic_paragraph_blocks",
            "segment_kinds": "header | paragraph | note",
            "target_chunk_chars": 3000,
            "soft_max_chars": 4300,
            "hard_max_chars": 5000,
            "reassembly_strategy": "preserve_order",
            "translation_notes": "Fallback profile; requires manual review.",
        }

    profiles.append({
        "document_type": dt,
        "documents": r["documents"],
        "chars": r["chars"],
        "estimated_nmt_ru_en_usd": r["estimated_nmt_ru_en_usd"],
        "segmentation_strategy": rule["segmentation_strategy"],
        "segment_kinds": rule["segment_kinds"],
        "target_chunk_chars": rule["target_chunk_chars"],
        "soft_max_chars": rule["soft_max_chars"],
        "hard_max_chars": rule["hard_max_chars"],
        "reassembly_strategy": rule["reassembly_strategy"],
        "translation_notes": rule["translation_notes"],
        "status": "draft_profile",
        "manual_review_required": "yes" if dt in {"poem", "biographical_article", "indictment", "verdict_or_sentence"} else "no",
    })

with OUT_PROFILES.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "document_type", "documents", "chars", "estimated_nmt_ru_en_usd",
        "segmentation_strategy", "segment_kinds",
        "target_chunk_chars", "soft_max_chars", "hard_max_chars",
        "reassembly_strategy", "translation_notes",
        "status", "manual_review_required",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(sorted(profiles, key=lambda x: (-int(x["chars"]), x["document_type"])))

with OUT_GLOSSARY_SEEDS.open("w", encoding="utf-8", newline="") as f:
    fields = [
        "layer", "source_file", "source_field", "glossary_kind",
        "priority", "translation_policy", "notes",
    ]
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    w.writeheader()
    w.writerows(GLOSSARY_SEED_LAYERS)

chars_total = sum(int(r["chars"]) for r in profiles)
high_coverage = sum(
    int(r["chars"]) for r in profiles
    if r["document_type"] in {"special_report", "interrogation_protocol", "session_transcript", "letter", "statement"}
)

by_strategy = defaultdict(lambda: {"types": 0, "chars": 0, "docs": 0})
for r in profiles:
    s = r["segmentation_strategy"]
    by_strategy[s]["types"] += 1
    by_strategy[s]["chars"] += int(r["chars"])
    by_strategy[s]["docs"] += int(r["documents"])

report = []
report.append("ShowTrials translation profiles v1 plan")
report.append("")
report.append(f"Document types covered: {len(profiles)}")
report.append(f"Missing profiles using fallback: {len(missing)}")
report.append(f"Total chars covered: {chars_total}")
report.append(f"Top-5 high-volume types coverage chars: {high_coverage}")
report.append(f"Top-5 high-volume types coverage share: {round(high_coverage / chars_total, 4) if chars_total else 0}")
report.append("")
report.append("Profiles by strategy:")
for s, v in sorted(by_strategy.items(), key=lambda x: (-x[1]["chars"], x[0])):
    report.append(f"{v['chars']}\tdocs={v['docs']}\ttypes={v['types']}\t{s}")

if missing:
    report.append("")
    report.append("Missing profiles:")
    for dt in missing:
        report.append(dt)

report.append("")
report.append("Glossary seed layers:")
for g in GLOSSARY_SEED_LAYERS:
    report.append(f"{g['priority']}\t{g['layer']}\t{g['glossary_kind']}\t{g['translation_policy']}")

report.append("")
report.append("Next steps:")
report.append("1. Review translation profiles v1 manually.")
report.append("2. Generate structural segmentation diagnostics using these profiles.")
report.append("3. Generate glossary seed TSVs from people, organizations, processes, and roles.")
report.append("4. Only after that, plan a small RU->EN pilot batch.")

report.append("")
report.append("Outputs:")
report.append(str(OUT_PROFILES))
report.append(str(OUT_GLOSSARY_SEEDS))
report.append(str(OUT_REPORT))

OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

print(OUT_PROFILES)
print(OUT_GLOSSARY_SEEDS)
print(OUT_REPORT)
