#!/usr/bin/env bash
#
# Paved-path setup for the GitHub repo: secrets, repo settings, light branch
# safety, and security features. Run this ONCE locally.
#
# NOTE: direct pushes to `main` are ALLOWED (solo-learning mode). Branch
# protection here only blocks destructive actions (force-push, deletion); it
# does NOT require pull requests. Tighten it later via the commented block.
#
# Prerequisites:
#   1. Install the GitHub CLI:  https://cli.github.com/
#   2. Authenticate:            gh auth login
#   3. You must have admin on the repo.
#
# Usage:
#   ./scripts/setup_github.sh

set -euo pipefail
REPO="${REPO:-ka61/evalsv3}"

command -v gh >/dev/null || { echo "Install the GitHub CLI first: https://cli.github.com/"; exit 1; }

echo "==> Target repo: $REPO"

echo "==> Setting model-provider secrets (input hidden; leave blank to skip)"
for key in OPENAI_API_KEY ANTHROPIC_API_KEY DEEPSEEK_API_KEY; do
  read -rsp "  $key: " val; echo
  if [ -n "$val" ]; then
    gh secret set "$key" --repo "$REPO" --body "$val"
    echo "  set $key"
  else
    echo "  skipped $key"
  fi
done

echo "==> Repo settings (squash-only, auto-delete merged branches)"
gh repo edit "$REPO" \
  --enable-squash-merge \
  --enable-merge-commit=false \
  --enable-rebase-merge=false \
  --delete-branch-on-merge

echo "==> Enabling secret scanning + push protection"
gh api -X PATCH "repos/$REPO" \
  -f "security_and_analysis[secret_scanning][status]=enabled" \
  -f "security_and_analysis[secret_scanning_push_protection][status]=enabled" || \
  echo "  (skip: may require a public repo or GitHub Advanced Security)"

echo "==> Light protection on 'main' (direct pushes ALLOWED; block force-push & deletion)"
gh api -X PUT "repos/$REPO/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<'JSON'
{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "restrictions": null
}
JSON

# --- Want a stricter paved path later? Replace the block above with this to
# --- require CI + 1 review and forbid direct pushes to main:
#
# gh api -X PUT "repos/$REPO/branches/main/protection" \
#   -H "Accept: application/vnd.github+json" --input - <<'JSON'
# {
#   "required_status_checks": { "strict": true, "contexts": ["lint"] },
#   "enforce_admins": true,
#   "required_pull_request_reviews": {
#     "required_approving_review_count": 1,
#     "dismiss_stale_reviews": true
#   },
#   "required_linear_history": true,
#   "allow_force_pushes": false,
#   "allow_deletions": false,
#   "restrictions": null
# }
# JSON

echo "==> Done. CI still runs on every push to main; pushing directly is allowed."
