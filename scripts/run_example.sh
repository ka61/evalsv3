#!/usr/bin/env bash
# Run ONE example by number or name. Eval logs go to logs/<example>/.
#
# Usage:
#   scripts/run_example.sh 01                      # by number
#   scripts/run_example.sh hello                   # by name fragment
#   scripts/run_example.sh 21 --epochs 3           # extra inspect args pass through
#   scripts/run_example.sh 23 --model openrouter/openai/gpt-4o
#
# The model defaults to $INSPECT_EVAL_MODEL, else openrouter/openai/gpt-4o-mini
# (vision-capable, so the image examples work). Override with --model.
# API keys are read automatically from the repo-root .env by Inspect.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[ $# -ge 1 ] || { echo "usage: scripts/run_example.sh <number|name> [inspect args...]"; exit 2; }
QUERY="$1"; shift || true

# resolve the example directory from a number (01, 1) or a name fragment
dir=""
for d in examples/[0-9]*/; do
  base="$(basename "$d")"; num="${base%%_*}"
  if [ "$num" = "$QUERY" ] || [ "$num" = "0$QUERY" ] || \
     { [ "$num" -eq "$QUERY" ] 2>/dev/null; } || \
     printf '%s' "$base" | grep -qi "$QUERY"; then
    dir="$d"; break
  fi
done
[ -n "$dir" ] || { echo "No example matches '$QUERY'. Options:"; ls -1 examples | grep '^[0-9]'; exit 1; }

name="$(basename "$dir")"
logdir="logs/$name"
mkdir -p "$logdir"

# default model only if the caller didn't pass one and none is set in the env
if ! printf ' %s ' "$*" | grep -q ' --model ' && [ -z "${INSPECT_EVAL_MODEL:-}" ]; then
  export INSPECT_EVAL_MODEL="openrouter/openai/gpt-4o-mini"
fi

echo "▶ running $name  →  logs in $logdir/"
inspect eval "$dir/task.py" --log-dir "$logdir" "$@"
echo "✓ $name done. View it:  inspect view --log-dir $logdir"
