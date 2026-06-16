# scripts/

Helpers for running the examples and viewing results. Run them from anywhere —
each resolves the repo root itself. API keys are read automatically from the
repo-root `.env` (Inspect loads it), so just have your keys there.

All eval logs are written under **`logs/<example_name>/`** at the repo root
(`logs/` is gitignored).

## Run one example — `run_example.sh`

```bash
scripts/run_example.sh 01                 # by number
scripts/run_example.sh hello              # by name fragment
scripts/run_example.sh 21 --epochs 3      # extra flags pass straight to `inspect eval`
scripts/run_example.sh 23 --model openai/gpt-4o
```

Default model is `$INSPECT_EVAL_MODEL` if set, else `openai/gpt-4o-mini` (which is
vision-capable, so the image examples work). Override with `--model`.

## Run everything — `run_all.sh`

```bash
scripts/run_all.sh                        # all non-Docker examples
scripts/run_all.sh --with-docker          # include 04, 05, 10, 19, 22 (need Docker)
scripts/run_all.sh --limit 3 --model openai/gpt-4o
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
python scripts/analyze_logs.py logs --model openai/gpt-5.5-pro   # stronger analyst
python scripts/analyze_logs.py logs --no-llm
python scripts/analyze_logs.py logs --out reports/run1   # -> reports/run1.md + .html
```

It computes headline metrics, **per-condition breakdowns** (control vs.
incentivized, etc.), and includes a few transcripts, then GPT-5.5 (the default analyst, override with --model) writes an
executive summary, per-eval interpretation (incl. sandbagging / deception /
scheming signals), caveats, and next steps. The interpretation uses Inspect's
model layer, so it reads your `.env` key and works with any provider. With
`--no-llm` (or no key/network) it still writes the full statistics report.

## Other

- `setup_github.sh` — one-time repo setup (secrets, settings, light branch
  safety). See the root README.

## Requirements

- `pip install -r requirements.txt` (Inspect + provider SDKs) and a key in `.env`.
- Examples 04, 05, 10, 19, 22 need **Docker** running.
- The vision examples (14–16, 20–22) need a **vision-capable** model
  (`gpt-4o-mini` works; `gpt-4o` is stronger).
