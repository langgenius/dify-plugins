#!/usr/bin/env bash
# ============================================================================
# classify-issues.sh
#
# Run this script to apply the issue classification plan:
#   1. Create labels (if they don't exist)
#   2. Close duplicate issues with a comment linking to the kept issue
#   3. Label all categorized issues
#
# Prerequisites:
#   - gh CLI authenticated (gh auth login)
#   - Write access to langgenius/dify-plugins
#
# Usage:
#   chmod +x .github/scripts/classify-issues.sh
#   .github/scripts/classify-issues.sh
#
# To preview without making changes, set DRY_RUN=1:
#   DRY_RUN=1 .github/scripts/classify-issues.sh
# ============================================================================

set -euo pipefail

REPO="langgenius/dify-plugins"
DRY_RUN="${DRY_RUN:-0}"

run_cmd() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "[DRY RUN] $*"
  else
    echo "[RUN] $*"
    "$@"
  fi
}

# ─── Step 1: Create labels ──────────────────────────────────────────────────

echo "=== Step 1: Ensure labels exist ==="

create_label() {
  local name="$1"
  local color="$2"
  local description="$3"

  if gh label list --repo "$REPO" --search "$name" --json name -q '.[].name' 2>/dev/null | grep -qx "$name"; then
    echo "  Label '$name' already exists."
  else
    run_cmd gh label create "$name" --repo "$REPO" --color "$color" --description "$description"
  fi
}

create_label "plugin-request" "0075ca" "Request for a new plugin"
create_label "bug" "d73a4a" "Something isn't working"
create_label "feature-request" "a2eeef" "Improvement to an existing plugin"
create_label "duplicate" "cfd3d7" "This issue already exists"
create_label "security" "e4e669" "Security-related issue"
create_label "question" "d876e3" "Further information is requested"

# ─── Step 2: Close duplicate issues ─────────────────────────────────────────

echo ""
echo "=== Step 2: Close duplicate issues ==="

close_as_duplicate() {
  local dup_issue="$1"
  local kept_issue="$2"
  local group_name="$3"

  echo "  Closing #$dup_issue as duplicate of #$kept_issue ($group_name)"
  run_cmd gh issue comment "$dup_issue" --repo "$REPO" \
    --body "Closing as duplicate of #$kept_issue ($group_name). Please follow #$kept_issue for updates."
  run_cmd gh issue close "$dup_issue" --repo "$REPO" --reason "not planned"
  run_cmd gh issue edit "$dup_issue" --repo "$REPO" --add-label "duplicate"
}

close_as_duplicate 2035 2102 "Parse Document OCR"
close_as_duplicate 2160 2163 "Security Scanning for Plugins"
close_as_duplicate 693  1322 "BookStack Integration"
close_as_duplicate 766  893  "vLLM Plugin Improvements"

# ─── Step 3: Label issues ───────────────────────────────────────────────────

echo ""
echo "=== Step 3: Apply labels ==="

apply_label() {
  local label="$1"
  shift
  for issue in "$@"; do
    echo "  Adding '$label' to #$issue"
    run_cmd gh issue edit "$issue" --repo "$REPO" --add-label "$label"
  done
}

# Plugin Requests — New Model Providers
apply_label "plugin-request" \
  2265 1966 914 860 834 656 632

# Plugin Requests — New Tools / Integrations
apply_label "plugin-request" \
  2225 2185 2182 2159 2158 2042 1995 1820 1781 1747 \
  1691 1619 1468 1460 1322 1320 1209 1206 1201 994 \
  947 890 883 690 684 645 628 599 560 547 546

# Plugin Requests — Document / OCR
apply_label "plugin-request" 2102

# Bug Reports
apply_label "bug" \
  1980 1969 1960 1931 1391 1252 1216 757 730 679 \
  660 631 624 623 502 501 471 355 312 293 96

# Feature Requests / Improvements on Existing Plugins
apply_label "feature-request" \
  2063 1857 1010 893 315 265

# Security
apply_label "security" 2163

# Questions
apply_label "question" 959 425

echo ""
echo "=== Done! ==="
if [ "$DRY_RUN" = "1" ]; then
  echo "(This was a dry run. Set DRY_RUN=0 to apply changes.)"
fi
