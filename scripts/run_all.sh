#!/usr/bin/env bash
# Run EVERY example. Each example's logs go to logs/<example>/.
#
# Docker-based examples (04, 05, 10, 19, 22) are SKIPPED unless --with-docker.
# All other args (e.g. --model, --limit, --epochs) pass through to every run.
#
# Usage:
#   scripts/run_all.sh                          # all non-Docker examples
#   scripts/run_all.sh --with-docker            # include Docker ones too
#   scripts/run_all.sh --limit 3 --model openrouter/openai/gpt-4o
set -uo pipefail   # NOT -e: keep going if one example fails
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOCKER_EXAMPLES=" 04 05 10 19 22 "
with_docker=0
extra=()
while [ $# -gt 0 ]; do
  case "$1" in
    --with-docker) with_docker=1; shift;;
    *) extra+=("$1"); shift;;
  esac
done

pass=0; fail=0; skip=0; failed_names=()
for d in examples/[0-9]*/; do
  name="$(basename "$d")"; num="${name%%_*}"
  if [ "$with_docker" -eq 0 ] && printf '%s' "$DOCKER_EXAMPLES" | grep -q " $num "; then
    echo "⏭  skip $name (needs Docker — rerun with --with-docker)"; skip=$((skip+1)); continue
  fi
  echo; echo "──────── $name ────────"
  if bash "$ROOT/scripts/run_example.sh" "$num" ${extra[@]+"${extra[@]}"}; then
    pass=$((pass+1))
  else
    echo "✗ FAILED: $name"; fail=$((fail+1)); failed_names+=("$name")
  fi
done

echo; echo "════════ summary ════════"
echo "  ok: $pass   failed: $fail   skipped: $skip"
[ "$fail" -gt 0 ] && printf '  failures: %s\n' "${failed_names[*]}"
echo "  view everything:  scripts/view_results.sh        (or: inspect view --log-dir logs)"
echo "  text summary:     scripts/view_results.sh summary"
exit 0
