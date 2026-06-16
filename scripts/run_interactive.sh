#!/usr/bin/env bash
# Interactive runner — pick an EXAMPLE and a MODEL from menus, then run it.
# The model menu is shown UNLESS you pass --model (or accept the default in-menu).
#
# Usage:
#   scripts/run_interactive.sh                                   # menus for both
#   scripts/run_interactive.sh 17                                # example given, pick model
#   scripts/run_interactive.sh 17 --model openrouter/openai/gpt-5.4   # both given, no prompts
#   scripts/run_interactive.sh 17 --epochs 3                     # epochs given, no N prompt
#   scripts/run_interactive.sh --dry-run                         # show the command, don't run
# It asks for the example, the model, and N (epochs = repeats per sample) unless
# each is supplied on the command line.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"

# default model: env, else .env, else the repo default
DEFAULT_MODEL="${INSPECT_EVAL_MODEL:-}"
if [ -z "$DEFAULT_MODEL" ] && [ -f .env ]; then
  DEFAULT_MODEL="$(grep -E '^INSPECT_EVAL_MODEL=' .env | head -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"' | tr -d "'" | xargs)"
fi
[ -z "$DEFAULT_MODEL" ] && DEFAULT_MODEL="openrouter/openai/gpt-5.4-mini"

# Ensure an OpenRouter prefix: bare slugs like "anthropic/claude-opus-4.8" become
# "openrouter/anthropic/claude-opus-4.8" (this repo routes everything via OpenRouter).
norm_model() { case "$1" in openrouter/*|"") printf '%s' "$1";; *) printf 'openrouter/%s' "$1";; esac; }
DEFAULT_MODEL="$(norm_model "$DEFAULT_MODEL")"

# curated model menu — verified against the live OpenRouter catalog
# (https://openrouter.ai/api/v1/models). Keep in sync with README "Example models to try".
MODELS=(
  "openrouter/openai/gpt-5.4-mini|text+image · cheap default (runs everything)"
  "openrouter/openai/gpt-5.4|text+image · strong general + vision"
  "openrouter/openai/gpt-5.5|text+image+reasoning · frontier"
  "openrouter/anthropic/claude-opus-4.8|text+image · coding & agentic"
  "openrouter/google/gemini-3.5-flash|text+image+video · fast & cheap"
  "openrouter/x-ai/grok-4.3|text+image · reasoning"
  "openrouter/qwen/qwen3.6-flash|text+image+video · open-weight vision (Qwen — good for images)"
  "openrouter/qwen/qwen3.6-27b|text+image+video · open-weight vision (Qwen)"
  "openrouter/google/gemma-4-31b-it|text+image · open-weight vision (Gemma)"
  "openrouter/mistralai/mistral-small-2603|text+image · open vision (Mistral Small 4)"
  "openrouter/deepseek/deepseek-v4-flash|text only · low cost"
  "openrouter/qwen/qwen3.7-max|text only · flagship reasoning"
)

# ---- parse args ----
EXAMPLE=""; MODEL=""; EPOCHS=""; DRY=0; EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="${2:-}"; shift 2;;
    --model=*) MODEL="${1#--model=}"; shift;;
    --epochs) EPOCHS="${2:-}"; shift 2;;
    --epochs=*) EPOCHS="${1#--epochs=}"; shift;;
    --dry-run) DRY=1; shift;;
    -h|--help) sed -n '2,11p' "$0"; exit 0;;
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
      "enter a custom model id") read -rp "  model id (e.g. anthropic/claude-opus-4.8): " MODEL
                                 [ -n "$MODEL" ] && break || echo "  empty, try again";;
      *) MODEL="${pick%%   —*}"; break;;
    esac
  done
fi

# normalise whatever we ended up with (menu / default / custom / --model) to openrouter/*
MODEL="$(norm_model "$MODEL")"

# ---- choose N (epochs) unless specified ----
if [ -z "$EPOCHS" ]; then
  echo
  read -rp "How many epochs N? (repeat each sample N times to average out noise) [1]: " EPOCHS
  EPOCHS="${EPOCHS:-1}"
fi
case "$EPOCHS" in ''|*[!0-9]*) echo "✗ epochs N must be a positive integer"; exit 2;; esac
[ "$EPOCHS" -ge 1 ] || { echo "✗ epochs N must be >= 1"; exit 2; }
# only pass the flag when N > 1 (N=1 is Inspect's default)
EPOCH_ARGS=()
[ "$EPOCHS" -gt 1 ] && EPOCH_ARGS=(--epochs "$EPOCHS")

echo
echo "▶ example=$EXAMPLE   model=$MODEL   epochs=$EPOCHS   extra=${EXTRA[*]:-(none)}"
if [ "$DRY" -eq 1 ]; then
  echo "(dry-run) would run: bash scripts/run_example.sh $EXAMPLE --model $MODEL ${EPOCH_ARGS[*]:-} ${EXTRA[*]:-}"
  exit 0
fi
exec bash "$ROOT/scripts/run_example.sh" "$EXAMPLE" --model "$MODEL" \
  ${EPOCH_ARGS[@]+"${EPOCH_ARGS[@]}"} ${EXTRA[@]+"${EXTRA[@]}"}
