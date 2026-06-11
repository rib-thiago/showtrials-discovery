#!/usr/bin/env bash
set -u

BASE="/tmp/showtrials-discovery"
INVENTORY="$BASE/showtrials_semantic_baseline_inventory.tsv"
REPORT="$BASE/showtrials_semantic_baseline_validation_report.txt"
TSV="$BASE/showtrials_semantic_baseline_validation.tsv"

failures=0
warnings=0

{
  echo -e "level\tcheck\tlayer\tdetail"

  if [ ! -f "$INVENTORY" ]; then
    echo -e "FAIL\tmissing_inventory\tsemantic_baseline\t$INVENTORY"
    failures=$((failures + 1))
  else
    awk -F '\t' 'NR>1 && $3!="present" {print "FAIL\tmissing_artifact\t"$1"\t"$2}' "$INVENTORY" |
    while IFS= read -r line; do
      echo "$line"
    done
  fi

  if [ -f "$INVENTORY" ]; then
    missing_count="$(awk -F '\t' 'NR>1 && $3!="present" {c++} END {print c+0}' "$INVENTORY")"
    zero_count="$(awk -F '\t' 'NR>1 && $4==0 && $1 !~ /script$/ {c++} END {print c+0}' "$INVENTORY")"

    if [ "$missing_count" -gt 0 ]; then
      failures=$((failures + missing_count))
    fi

    if [ "$zero_count" -gt 0 ]; then
      echo -e "WARN\tzero_row_artifacts\tsemantic_baseline\t$zero_count"
      warnings=$((warnings + 1))
    fi
  fi

  if [ -f "$BASE/showtrials_semantic_layer_validation.tsv" ]; then
    bad_semantic="$(awk -F '\t' 'NR>1 && $1!="OK" {c++} END {print c+0}' "$BASE/showtrials_semantic_layer_validation.tsv")"
    if [ "$bad_semantic" -gt 0 ]; then
      echo -e "FAIL\tsemantic_layer_validation_not_clean\tsemantic_layer\t$bad_semantic"
      failures=$((failures + 1))
    fi
  else
    echo -e "FAIL\tmissing_semantic_layer_validation\tsemantic_layer\tshowtrials_semantic_layer_validation.tsv"
    failures=$((failures + 1))
  fi

  if [ -f "$BASE/showtrials_search_v2_validation.tsv" ]; then
    failed_search="$(awk -F '\t' 'NR>1 && $2!="PASS" {c++} END {print c+0}' "$BASE/showtrials_search_v2_validation.tsv")"
    if [ "$failed_search" -gt 0 ]; then
      echo -e "FAIL\tsearch_v2_validation_not_clean\tsearch_v2\t$failed_search"
      failures=$((failures + 1))
    fi
  else
    echo -e "FAIL\tmissing_search_v2_validation\tsearch_v2\tshowtrials_search_v2_validation.tsv"
    failures=$((failures + 1))
  fi

  if [ "$failures" -eq 0 ] && [ "$warnings" -eq 0 ]; then
    echo -e "OK\tall_checks\tsemantic_baseline\tpassed"
  fi
} > "$TSV"

failures="$(awk -F '\t' 'NR>1 && $1=="FAIL" {c++} END {print c+0}' "$TSV")"
warnings="$(awk -F '\t' 'NR>1 && $1=="WARN" {c++} END {print c+0}' "$TSV")"

{
  echo "ShowTrials semantic baseline validation"
  echo
  echo "Failures: $failures"
  echo "Warnings: $warnings"
  echo
  cat "$TSV"
} > "$REPORT"

echo "$REPORT"
echo "$TSV"

[ "$failures" -eq 0 ]
