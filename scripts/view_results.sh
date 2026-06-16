#!/usr/bin/env bash
# View eval results the easy way.
#
# Usage:
#   scripts/view_results.sh                 # open the Inspect log viewer over ALL logs
#   scripts/view_results.sh summary         # print a text table of every log's score
#   scripts/view_results.sh 21              # open the viewer for one example
#   scripts/view_results.sh fingerprint     # ...by name fragment too
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

arg="${1:-view}"
case "$arg" in
  view|"")
    exec inspect view --log-dir logs
    ;;
  summary|table)
    exec python3 scripts/summarize_logs.py "${2:-logs}"
    ;;
  *)
    # treat as an example number/name → view just that example's logs
    dir=""
    for d in logs/[0-9]*/ examples/[0-9]*/; do
      base="$(basename "$d")"; num="${base%%_*}"
      if [ "$num" = "$arg" ] || [ "$num" = "0$arg" ] || \
         { [ "$num" -eq "$arg" ] 2>/dev/null; } || \
         printf '%s' "$base" | grep -qi "$arg"; then
        dir="logs/$base"; break
      fi
    done
    [ -n "$dir" ] && [ -d "$dir" ] || { echo "no logs for '$arg' (run it first)"; exit 1; }
    exec inspect view --log-dir "$dir"
    ;;
esac
