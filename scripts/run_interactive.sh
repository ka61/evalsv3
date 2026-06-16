#!/usr/bin/env bash
# Interactive runner — pick an EXAMPLE and a MODEL from menus, then run it.
# The model menu is shown UNLESS you pass --model (or accept the default in-menu).
#
# Usage:
#   scripts/run_interactive.sh                                   # menus for both
#   scripts/run_interactive.sh 17                                # example given, pick model
#   scripts/run_interactive.sh 17 --model openrouter/openai/gpt-4o   # both given, no prompts
#   scripts/run_interactive.sh 17 --epochs 3                     # extra inspect flags pass through
#   scripts/run_interactive.sh --dry-run                         # show the command, don't run
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"

# default model: env, else .env, else the repo default
DEFAULT_MODEL="${INSPECT_EVAL_MODEL:-}"
if [ -z "$DEFAULT_MODEL" ] && [ -f .env ]; then
  DEFAULT_MODEL="$(grep -E '^INSPECT_EVAL_MODEL=' .env | head -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"' | tr -d "'" | xargs)"
fi
[ -z "$DEFAULT_MODEL" ] && DEFAULT_MODEL="openrouter/openai/gpt-4o-mini"

# curated model menu (keep in sync with README "Example models to try")
MODELS=(
  "openrouter/openai/gpt-4o-mini|text+image · cheap default (runs everything)"
  "openrouter/openai/gpt-4o|text+image · stronger general + vision"
  "openrouter/openai/gpt-5.5|text+image+reasoning · frontier"
  "openrouter/anthropic/claude-3.5-sonnet|text+image · coding & agentic"
  "openrouter/google/gemini-2.5-pro|text+image · long context, reasoning"
  "openrouter/google/gemini-2.5-flash|text+image · fast & cheap"
  "openrouter/qwen/qwen2.5-vl-72b-instruct|text+image · open-weight vision (Qwen-VL)"
  "openrouter/meta-llama/llama-3.2-90b-vision-instruct|text+image · open-weight vision (Llama)"
  "openrouter/mistralai/pixtral-large-2411|text+image · vision (Pixtral)"
  "openrouter/deepseek/deepseek-chat|text only · low cost"
  "openrouter/deepseek/deepseek-r1|text · reasoning"
)

# ---- parse args ----
EXAMPLE=""; MODEL=""; DRY=0; EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="${2:-}"; shift 2;;
    --model=*) MODEL="${1#--model=}"; shift;;
    --dry-run) DRY=1; shift;;
    -h|--help) sed -n '2,9p' "$0"; exit 0;;
    -*) EXTRA+=("$1"); shift;;
    *) if [ -z "$EXAMPLE" ]; then EXAMPLE="$1"; else EXTRA+=("$1"); fi; shift;;
  esac
done

# ---- choose example if not given ----
if [ -z "$EXAMPLE" ]; then
  DIRS=()
  for d in examples/[0-9]*/; do DIRS+=("$(basename "${d%/}")"); done
  echo "Select an example:"
  PS3=$'\n> example number (or Ctrl-C to quit): '
  select choice in "${DIRS[@]}"; do
    if [ -n "${choice:-}" ]; then EXAMPLE="${choice%%_*}"; break; fi
    echo "  invalid — type the number next to an example"
  done
fi

# ---- choose model unless specified ----
if [ -z "$MODEL" ]; then
  echo
  echo "Select a model (these go through OpenRouter — needs OPENROUTER_API_KEY):"
  OPTS=()
  for m in "${MODELS[@]}"; do OPTS+=("${m%%|*}   —   ${m#*|}"); done
  OPTS+=("use default ($DEFAULT_MODEL)")
  OPTS+=("enter a custom model id")
  PS3=$'\n> model number: '
  select pick in "${OPTS[@]}"; do
    [ -z "${pick:-}" ] && { echo "  invalid"; continue; }
    case "$pick" in
      "use default ("*) MODEL="$DEFAULT_MODEL"; break;;
      "enter a custom model id") read -rp "  model id (e.g. openrouter/anthropic/claude-3.5-sonnet): " MODEL
                                 [ -n "$MODEL" ] && break || echo "  empty, try again";;
      *) MODEL="${pick%%   —*}"; break;;
    esac
  done
fi

echo
echo "▶ example=$EXAMPLE   model=$MODEL   extra=${EXTRA[*]:-(none)}"
if [ "$DRY" -eq 1 ]; then
  echo "(dry-run) would run: bash scripts/run_example.sh $EXAMPLE --model $MODEL ${EXTRA[*]:-}"
  exit 0
fi
exec bash "$ROOT/scripts/run_example.sh" "$EXAMPLE" --model "$MODEL" ${EXTRA[@]+"${EXTRA[@]}"}
