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
inspect eval examples/01_hello/task.py --model openai/gpt-4o-mini --limit 5
inspect view                # browse the .eval log in your browser
```

Requires **Python ≥ 3.10**. Examples 04–05 also need **Docker** running.

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
scripts/run_example.sh 01            # run one (by number or name fragment)
scripts/run_example.sh 21 --epochs 3 # extra flags pass to `inspect eval`
scripts/run_all.sh                   # run all (skips Docker examples)
scripts/run_all.sh --with-docker     # include 04, 05, 10, 19, 22
scripts/view_results.sh              # open the log viewer over all runs
scripts/view_results.sh summary      # quick text table of every run's score
```

See [`scripts/README.md`](scripts/README.md) for details.

## Repository layout

```
evalsv3/
  examples/            # the learning path (01 → 05), each with its own README
  docs/                # deep-dive guides
    inspect-cli.md                # detailed Inspect CLI reference (flags + examples)
    inspect-evals-guide.html      # detailed how-to for Inspect
    inspect-platform-design.html  # a platform design spec
    implementation-plan.html      # build plan for that platform
  .vscode/             # recommended extensions + settings
  .devcontainer/       # one-click reproducible environment
  .github/             # CI, manual eval workflow, CODEOWNERS, templates
  scripts/setup_github.sh   # configure repo secrets + branch protection
  .env.example         # copy to .env and add your keys
  requirements.txt
```

## Models

Set a default in `.env` (`INSPECT_EVAL_MODEL`) or pass `--model provider/name`:

- `openai/gpt-4o-mini` · `openai/gpt-4o`
- `anthropic/claude-sonnet-4-0`
- `deepseek/deepseek-chat`
- self-hosted: `vllm/<hf-model>` (needs a GPU)

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
