#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_B="$ROOT/data/b-json-export-search"
DATA_C="$ROOT/data/c-catalog-taxonomy"
DATA_E="$ROOT/data/e-semantic-layer"
LOCAL="$ROOT/local"
REPORT_E="$ROOT/reports/e-semantic-layer"
SCRIPT_B="$ROOT/scripts/b-json-export-search"

REPORT="$REPORT_E/showtrials_semantic_baseline_report.txt"
TSV="$DATA_E/showtrials_semantic_baseline_inventory.tsv"
DEPS="$DATA_E/showtrials_semantic_baseline_dependencies.tsv"

mkdir -p "$(dirname "$TSV")" "$(dirname "$REPORT")"

count_rows() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo 0
    return
  fi
  awk 'NR>1 {c++} END {print c+0}' "$file"
}

count_cols() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo 0
    return
  fi
  awk -F '\t' 'NR==1 {print NF; exit}' "$file"
}

write_layer() {
  local layer="$1"
  local file="$2"
  local status="missing"
  [ -f "$file" ] && status="present"
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$layer" "$file" "$status" "$(count_rows "$file")" "$(count_cols "$file")" >> "$TSV"
}

cat > "$TSV" <<'EOF'
layer	path	status	row_count	column_count
EOF

write_layer "catalog" "$DATA_C/showtrials_master_catalog.tsv"
write_layer "search_corpus" "$LOCAL/showtrials_search_corpus.tsv"
write_layer "people" "$DATA_E/showtrials_literal_people.tsv"
write_layer "person_documents" "$DATA_E/showtrials_literal_person_documents.tsv"
write_layer "person_aliases" "$DATA_E/showtrials_person_aliases.tsv"
write_layer "document_types_v4" "$DATA_C/showtrials_document_types_v4.tsv"
write_layer "organizations" "$DATA_E/showtrials_organizations.tsv"
write_layer "organization_documents" "$DATA_E/showtrials_organization_documents.tsv"
write_layer "organization_hierarchy" "$DATA_E/showtrials_organization_hierarchy.tsv"
write_layer "organization_families" "$DATA_E/showtrials_organization_families.tsv"
write_layer "organization_family_document_matrix" "$DATA_E/showtrials_organization_family_document_matrix.tsv"
write_layer "roles_v2" "$DATA_E/showtrials_roles_v2.tsv"
write_layer "role_documents_v2" "$DATA_E/showtrials_role_documents_v2.tsv"
write_layer "person_organization_matrix" "$DATA_E/showtrials_person_organization_matrix.tsv"
write_layer "person_organization_summary" "$DATA_E/showtrials_person_organization_summary.tsv"
write_layer "organization_person_summary" "$DATA_E/showtrials_organization_person_summary.tsv"
write_layer "person_context_profiles_v2" "$DATA_E/showtrials_person_institution_profiles_v2.tsv"
write_layer "processes" "$DATA_E/showtrials_processes.tsv"
write_layer "process_document_matrix" "$DATA_E/showtrials_process_document_matrix.tsv"
write_layer "person_process_matrix" "$DATA_E/showtrials_person_process_matrix.tsv"
write_layer "organization_process_matrix" "$DATA_E/showtrials_organization_process_matrix.tsv"
write_layer "family_process_matrix" "$DATA_E/showtrials_family_process_matrix.tsv"
write_layer "person_process_profiles" "$DATA_E/showtrials_person_process_profiles.tsv"
write_layer "organization_process_profiles" "$DATA_E/showtrials_organization_process_profiles.tsv"
write_layer "family_process_profiles" "$DATA_E/showtrials_family_process_profiles.tsv"
write_layer "search_v2_script" "$SCRIPT_B/showtrials-search-v2.py"
write_layer "search_v2_validation" "$DATA_B/showtrials_search_v2_validation.tsv"
write_layer "semantic_layer_inventory" "$DATA_E/showtrials_semantic_layer_inventory.tsv"
write_layer "semantic_layer_validation" "$DATA_E/showtrials_semantic_layer_validation.tsv"

cat > "$DEPS" <<'EOF'
artifact	depends_on	purpose
showtrials_literal_people.tsv	showtrials_master_catalog.tsv	person entity inventory
showtrials_literal_person_documents.tsv	showtrials_literal_people.tsv	person-document links
showtrials_person_aliases.tsv	showtrials_literal_people.tsv	manual/automatic alias normalization
showtrials_document_types_v4.tsv	showtrials_master_catalog.tsv	document type classification
showtrials_organizations.tsv	showtrials_master_catalog.tsv	organization entity inventory
showtrials_organization_documents.tsv	showtrials_organizations.tsv	organization-document links
showtrials_organization_hierarchy.tsv	showtrials_organizations.tsv	organization hierarchy
showtrials_organization_families.tsv	showtrials_organizations.tsv	institutional family mapping
showtrials_organization_family_document_matrix.tsv	showtrials_organization_documents.tsv	document-family matrix
showtrials_roles_v2.tsv	showtrials_positions.tsv	role taxonomy
showtrials_role_documents_v2.tsv	showtrials_roles_v2.tsv	role-document links
showtrials_person_organization_matrix.tsv	person_documents + organization_documents	person-organization cooccurrence matrix
showtrials_processes.tsv	showtrials_master_catalog.tsv	process entity layer
showtrials_process_document_matrix.tsv	showtrials_processes.tsv	process-document matrix
showtrials_person_process_matrix.tsv	person_documents + processes	person-process matrix
showtrials_organization_process_matrix.tsv	organization_documents + processes	organization-process matrix
showtrials_family_process_matrix.tsv	organization_family_document_matrix + processes	family-process matrix
showtrials_process_profiles.tsv	process matrices	entity process profiles
showtrials-search-v2.py	semantic TSV baseline	semantic search consumer
EOF

{
  echo "ShowTrials semantic baseline"
  echo
  echo "Generated: $(date -Is)"
  echo "Root: $ROOT"
  echo
  echo "Layer inventory:"
  column -t -s $'\t' "$TSV"
  echo
  echo "Dependencies:"
  column -t -s $'\t' "$DEPS"
  echo
  echo "Interpretation policy:"
  echo "- Frequency and cooccurrence are contextual evidence."
  echo "- They are not biographical, causal, or historiographical claims."
  echo "- Centrality metrics require manual curatorial interpretation before use."
  echo "- Search v2 is approved as a consumer of the validated semantic baseline."
  echo
  echo "Recommended next state:"
  echo "ShowTrials Discovery v1 semantic baseline can be treated as frozen for exploratory search."
} > "$REPORT"

echo "$TSV"
echo "$DEPS"
echo "$REPORT"
