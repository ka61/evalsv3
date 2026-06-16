# evalsv3 — learning Inspect

A hands-on repo for learning the [UK AISI **Inspect**](https://inspect.aisi.org.uk/)
framework for evaluating language models. It pairs a set of runnable examples
(increasing in complexity) with deep-dive HTML guides.

> New to evals? Start with the guide in [`docs/`](docs/), then run the examples
> below in order.

## Quickstart

```bash
# 1. clone
git clone git@github.com:ka61/evalsv3.git
cd evalsv3

# 2. create an environment (uv recommended; venv shown here)
python -m venv .venv && source .venv/bin/activate

# 3. install
pip install -r requirements.txt

# 4. add your keys
cp .env.example .env        # then edit .env

# 5. run your first eval
inspect eval examples/01_hello/task.py --model openrouter/openai/gpt-5.4-mini --limit 5
inspect view                # browse the .eval log in your browser
```

Requires **Python ≥ 3.10**. Examples **04, 05, 10, 19, 22** also need **Docker**;
the vision examples (**14–16, 20–22**) need a vision-capable model (e.g. `gpt-5.4`).

## Open it in VS Code

1. Install the recommended extensions when prompted (or from the Extensions
   view) — the official **Inspect AI** extension (`ukaisi.inspect-ai`), Python,
   and Ruff. They're listed in [`.vscode/extensions.json`](.vscode/extensions.json).
2. Select your `.venv` as the interpreter (**Python: Select Interpreter**).
3. Set keys via the extension's **Configuration (.env)** panel, or edit `.env`.
4. Open any `task.py` and use **Run Task** / **Debug Task** from the Inspect
   activity bar; logs open inline.

Prefer containers? Reopen in the provided **dev container**
([`.devcontainer/`](.devcontainer/)) for a ready-made Python + Docker setup.

## Examples

Work through these in order — each adds one concept. Full annotated index in
[`examples/README.md`](examples/README.md). Tags: 🧠 chain-of-thought ·
🖼️ vision · 🛡️ AI-safety.

**Foundations**

| # | Example | Teaches | Docker |
|---|---------|---------|--------|
| 01 | [`01_hello`](examples/01_hello/) | the core loop: dataset → solver → model-graded scorer | – |
| 02 | [`02_multiple_choice`](examples/02_multiple_choice/) | deterministic `choice` scoring | – |
| 03 | [`03_tools`](examples/03_tools/) | a custom `@tool` the model calls | – |
| 04 | [`04_sandbox_agent`](examples/04_sandbox_agent/) | a `react` agent + `bash` in a Docker sandbox | ✓ |
| 05 | [`05_custom_scorer`](examples/05_custom_scorer/) | custom scorer running `pytest`; image from a Dockerfile | ✓ |

**Going deeper**

| # | Example | Teaches | Docker |
|---|---------|---------|--------|
| 06 | [`06_hf_dataset`](examples/06_hf_dataset/) | 🧠 GSM8K from the Hub + chain-of-thought | – |
| 07 | [`07_multiple_scorers`](examples/07_multiple_scorers/) | several scorers on one task | – |
| 08 | [`08_epochs_reliability`](examples/08_epochs_reliability/) | epochs & pass@k | – |
| 09 | [`09_model_roles`](examples/09_model_roles/) | model roles (grader / red-team) | – |
| 10 | [`10_limits_guardrails`](examples/10_limits_guardrails/) | message/token/time limits + caps | ✓ |
| 11 | [`11_web_search_agent`](examples/11_web_search_agent/) | a research agent with `web_search` | – |
| 12 | [`12_reasoning_cot`](examples/12_reasoning_cot/) | 🧠 reasoning models + `self_critique` | – |
| 13 | [`13_eval_set`](examples/13_eval_set/) | running a suite with `eval_set` | – |

**Vision**

| # | Example | Teaches | Docker |
|---|---------|---------|--------|
| 14 | [`14_image_vqa`](examples/14_image_vqa/) | 🖼️ single-image Q&A | – |
| 15 | [`15_image_chart`](examples/15_image_chart/) | 🖼️ chart reading | – |
| 16 | [`16_image_compare`](examples/16_image_compare/) | 🖼️ comparing two images | – |

**AI-safety concepts (Apollo Research)** — harmless toy evals that *measure* the behaviour

| # | Example | Teaches | Docker |
|---|---------|---------|--------|
| 17 | [`17_apollo_sandbagging`](examples/17_apollo_sandbagging/) | 🛡️ sandbagging (strategic underperformance) | – |
| 18 | [`18_apollo_deception`](examples/18_apollo_deception/) | 🛡️ strategic deception (lying to reach a goal) | – |
| 19 | [`19_apollo_scheming_oversight`](examples/19_apollo_scheming_oversight/) | 🛡️🧠 scheming (covertly disabling oversight) | ✓ |

**Scheming with images** — Apollo concepts where the cue or task is visual

| # | Example | Teaches | Docker |
|---|---------|---------|--------|
| 20 | [`20_scheming_eval_awareness`](examples/20_scheming_eval_awareness/) | 🛡️🖼️ situational awareness (spot an eval from a screenshot) | – |
| 21 | [`21_scheming_visual_sandbagging`](examples/21_scheming_visual_sandbagging/) | 🛡️🖼️ visual sandbagging (underperform on a vision task) | – |
| 22 | [`22_scheming_visual_oversight`](examples/22_scheming_visual_oversight/) | 🛡️🖼️🧠 scheming with a visual oversight cue | ✓ |

**Manipulation & CoT robustness** — does authoritative context steer the answer?

| # | Example | Teaches | Docker |
|---|---------|---------|--------|
| 23 | [`23_fingerprint_manipulation`](examples/23_fingerprint_manipulation/) | 🧠🖼️🛡️ CoT failure: authority pressure manufactures a false fingerprint match (Shirley McKie case) | – |

Data details for every example, plus a table of popular benchmarks, are in
[`DATASETS.md`](DATASETS.md).

### Run them with the helper scripts

Logs are written to `logs/<example>/` (gitignored); keys come from `.env`.

```bash
scripts/run_interactive.sh          # menu: pick example + model + N (epochs); asks for each unless --model/--epochs
scripts/run_example.sh 01            # run one (by number or name fragment)
scripts/run_example.sh 21 --epochs 3 # extra flags pass to `inspect eval`
scripts/run_all.sh                   # run all (skips Docker examples)
scripts/run_all.sh --with-docker     # include 04, 05, 10, 19, 22
```

### View & analyse the results

```bash
scripts/view_results.sh              # open the interactive Inspect log viewer
scripts/view_results.sh summary      # quick text table of every run's score
python scripts/analyze_logs.py       # write a layman-friendly report -> logs/ANALYSIS.md + .html
python scripts/analyze_logs.py logs --no-llm   # stats + plain-English verdicts, no model call
```

`analyze_logs.py` explains, in plain English, what each example tests and gives a
**verdict** (did sandbagging / deception / scheming happen?), then — when a model
is reachable — adds a GPT‑5.5 narrative. It writes both Markdown and a styled HTML
report (with a table of contents). See [`scripts/README.md`](scripts/README.md).

For the full Inspect command line, see [`docs/inspect-cli.md`](docs/inspect-cli.md).

## Repository layout

```
evalsv3/
  examples/            # the learning path (01 → 23), each with its own README
    assets/diagrams/   # concept diagrams used in the example READMEs
  docs/                # deep-dive guides
    inspect-cli.md                # detailed Inspect CLI reference (flags + examples)
    inspect-evals-guide.html      # detailed how-to for Inspect
    inspect-platform-design.html  # a platform design spec
    implementation-plan.html      # build plan for that platform
  scripts/             # helpers (see scripts/README.md)
    run_interactive.sh            # menu: pick example + model + N (epochs), then run
    run_example.sh · run_all.sh   # run one / all examples -> logs/
    view_results.sh               # open the viewer / print a summary table
    summarize_logs.py             # the summary table backend
    analyze_logs.py               # write an interpreted report (md + html)
    setup_github.sh               # one-time repo secrets + branch safety
  .vscode/             # recommended extensions + settings
  .devcontainer/       # one-click reproducible environment
  .github/             # CI, manual eval workflow, CODEOWNERS, templates
  logs/                # eval logs land here (gitignored)
  DATASETS.md · CONTRIBUTING.md · .env.example · requirements.txt
```

## Models — switch easily via OpenRouter (recommended)

The simplest setup is **one OpenRouter key** for every model. Put
`OPENROUTER_API_KEY` in `.env` and set a default model — then switch models by
editing a single line (or `--model`):

```bash
# .env
OPENROUTER_API_KEY=sk-or-...
INSPECT_EVAL_MODEL=openrouter/openai/gpt-5.4-mini   # change this to switch everywhere
```

Use any [OpenRouter model](https://openrouter.ai/models) as `openrouter/<id>`:

- `openrouter/openai/gpt-5.4` · `openrouter/openai/gpt-5.5` (vision-capable — needed for examples 14–16, 20–22)
- `openrouter/anthropic/claude-opus-4.8`
- `openrouter/google/gemini-3.5-flash` · `openrouter/qwen/qwen3.6-flash`

Per-run override: `inspect eval task.py --model openrouter/anthropic/claude-opus-4.8`
or `scripts/run_example.sh 17 --model openrouter/google/gemini-3.5-flash`.

**Prefer native provider keys instead?** Set `OPENAI_API_KEY` /
`ANTHROPIC_API_KEY` / `DEEPSEEK_API_KEY` in `.env` and use plain ids
(`openai/gpt-5.4`, `anthropic/claude-opus-4.8`, …); self-host with
`vllm/<hf-model>`. The report writer `scripts/analyze_logs.py` defaults to
`openrouter/openai/gpt-5.5` (override with `--model`).

## Example models to try

A starting menu of OpenRouter model ids — set one as `INSPECT_EVAL_MODEL` in
`.env` or pass `--model`. Exact ids and prices change, so browse
[openrouter.ai/models](https://openrouter.ai/models) for the current list.

The ids below were checked against the live OpenRouter catalog, but slugs and
prices move quickly — always confirm an id at
[openrouter.ai/models](https://openrouter.ai/models) before relying on it.

| Model (`--model`) | Input | Good for |
|---|---|---|
| `openrouter/openai/gpt-5.4-mini` | text + image (multimodal) | cheap default — runs every example, incl. vision |
| `openrouter/openai/gpt-5.4` | text + image (multimodal) | strong general + vision |
| `openrouter/openai/gpt-5.5` | text + image, reasoning | frontier; the analysis-report default analyst |
| `openrouter/anthropic/claude-opus-4.8` | text + image (multimodal) | strong coding & agentic (examples 04, 05) |
| `openrouter/google/gemini-3.5-flash` | text + image + video | fast, cheap multimodal, huge context |
| `openrouter/x-ai/grok-4.3` | text + image (multimodal) | reasoning + vision |
| `openrouter/qwen/qwen3.6-flash` | text + image + video | open-weight vision (Qwen) — **good for image inputs** |
| `openrouter/qwen/qwen3.6-27b` | text + image + video | open-weight vision (Qwen), dense 27B |
| `openrouter/qwen/qwen3.5-9b` | text + image + video | small open-weight vision (cheapest image option) |
| `openrouter/google/gemma-4-31b-it` | text + image (multimodal) | open-weight vision (Gemma) |
| `openrouter/mistralai/mistral-small-2603` | text + image (multimodal) | open-weight vision (Mistral Small 4) |
| `openrouter/deepseek/deepseek-v4-flash` | text only | low-cost general (text-only examples) |
| `openrouter/qwen/qwen3.7-max` | text only | flagship reasoning (text only) |

> **Pick by capability:** the vision examples (14–16, 20–22) need a **text + image**
> model — text-only ones (`…/deepseek-v4-flash`, `…/qwen3.7-max`) will error there.
> For image inputs the Qwen 3.6 / 3.5 vision models are a strong open-weight pick.
> Agentic/sandbox examples (04, 05, 10, 19, 22) run on any model but benefit from
> strong tool-use models (`…/gpt-5.5`, `…/claude-opus-4.8`).

Prefer not to use OpenRouter? Drop the `openrouter/` prefix and set the matching
native key (e.g. `--model openai/gpt-5.4` with `OPENAI_API_KEY`).

## Contributing & the paved path

This is set up for **solo learning**, so you can push directly to `main` — CI
(`ruff` + import checks) still runs on every push, and force-pushes/branch
deletion are blocked for safety. PRs are optional but recommended once you're
collaborating; see [CONTRIBUTING.md](CONTRIBUTING.md). One-time repo setup
(secrets, settings, light branch safety):

```bash
./scripts/setup_github.sh      # needs the GitHub CLI + admin on the repo
```

The script contains a commented stricter block (require CI + 1 review, no direct
pushes) to switch on later.

## Secrets

Keys live only in your local `.env` (gitignored) and in GitHub Actions Secrets
(`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`). Never commit a key —
`gitleaks` (pre-commit) and GitHub push protection are there to catch slips.
