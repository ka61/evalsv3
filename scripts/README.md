# scripts/

Helpers for running the examples and viewing results. Run them from anywhere —
each resolves the repo root itself. API keys are read automatically from the
repo-root `.env` (Inspect loads it), so just have your keys there.

All eval logs are written under **`logs/<example_name>/`** at the repo root
(`logs/` is gitignored).

**Switching models is one line.** Put `OPENROUTER_API_KEY` in `.env` and set
`INSPECT_EVAL_MODEL=openrouter/openai/gpt-4o-mini` (or any `openrouter/<id>`); every
script and `inspect eval` then uses it. Override per run with `--model openrouter/...`.

## Typical workflow

```bash
scripts/run_interactive.sh       # 0. menu-driven: pick example + model
scripts/run_example.sh 17        # 1. run an example (or scripts/run_all.sh)
scripts/view_results.sh summary  # 2. glance at the scores
python scripts/analyze_logs.py   # 3. get an interpreted report (logs/ANALYSIS.md + .html)
```

For the raw `inspect` command line behind these scripts, see
[`../docs/inspect-cli.md`](../docs/inspect-cli.md).

## Interactive — `run_interactive.sh`

Menu-driven wrapper around `run_example.sh`: pick the example, then pick the model
(it shows the curated OpenRouter list). It only asks for the model **unless you
pass `--model`**.

```bash
scripts/run_interactive.sh                 # menus for example + model
scripts/run_interactive.sh 17              # example given, just pick the model
scripts/run_interactive.sh 17 --model openrouter/openai/gpt-4o   # both given, no prompts
scripts/run_interactive.sh --dry-run       # show the resolved command without running
```

## Run one example — `run_example.sh`

```bash
scripts/run_example.sh 01                 # by number
scripts/run_example.sh hello              # by name fragment
scripts/run_example.sh 21 --epochs 3      # extra flags pass straight to `inspect eval`
scripts/run_example.sh 23 --model openrouter/openai/gpt-4o
```

Default model is `$INSPECT_EVAL_MODEL` if set, else `openrouter/openai/gpt-4o-mini`
(vision-capable, so the image examples work). Override with `--model`.

## Run everything — `run_all.sh`

```bash
scripts/run_all.sh                        # all non-Docker examples
scripts/run_all.sh --with-docker          # include 04, 05, 10, 19, 22 (need Docker)
scripts/run_all.sh --limit 3 --model openrouter/openai/gpt-4o
```

It keeps going if one example fails and prints an ok/failed/skipped summary at the
end. Docker-based examples are skipped by default.

## View results — `view_results.sh`

```bash
scripts/view_results.sh                   # open the Inspect log viewer over ALL logs
scripts/view_results.sh summary           # quick text table (task, model, accuracy, …)
scripts/view_results.sh 21                # open the viewer for just one example
```

`summary` calls `summarize_logs.py`, which reads every log header under `logs/`
and prints one row per run.

## Analyse results — `analyze_logs.py`

Turn the logs into a written, interpreted report — **Markdown + HTML**.

```bash
# reads logs/, asks the model to interpret, writes logs/ANALYSIS.md + logs/ANALYSIS.html
python scripts/analyze_logs.py

# choose the analyst model, or skip the LLM and emit stats only
python scripts/analyze_logs.py logs --model openrouter/anthropic/claude-3.5-sonnet  # any model
python scripts/analyze_logs.py logs --no-llm
python scripts/analyze_logs.py logs --out reports/run1   # -> reports/run1.md + .html
```

For every eval it writes a **plain-English explanation** (what it's testing, the
terms it uses) and a **computed verdict** (e.g. "No sandbagging — 67% vs 67%",
"Scheming observed in 0% of runs"), plus per-condition tables and collapsible
transcripts. The analyst model (default `openrouter/openai/gpt-5.5`, override with
`--model`) adds a
narrative summary written for a non-expert. The HTML has a table of contents and
a floating Contents/Top button. With `--no-llm` (or no key/network) the
explanations, verdicts and stats are all still produced locally.

## Other

- `setup_github.sh` — one-time repo setup (secrets, settings, light branch
  safety). See the root README.

## Requirements

- `pip install -r requirements.txt` (Inspect + provider SDKs) and a key in `.env`.
- Examples 04, 05, 10, 19, 22 need **Docker** running.
- The vision examples (14–16, 20–22) need a **vision-capable** model
  (`openrouter/openai/gpt-4o-mini` works; `.../gpt-4o` is stronger).
