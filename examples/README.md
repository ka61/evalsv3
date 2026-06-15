# Examples

Worked Inspect examples in increasing order of complexity. Do them in order —
each introduces one new idea on top of the last. Tags: 🧠 chain-of-thought ·
🖼️ vision · 🛡️ AI-safety (Apollo Research concepts).

## Foundations

| # | Example | New concept | Sandbox? |
|---|---------|-------------|----------|
| 01 | [`01_hello`](01_hello/) | dataset → solver → model-graded scorer | no |
| 02 | [`02_multiple_choice`](02_multiple_choice/) | choices + deterministic `choice` scorer | no |
| 03 | [`03_tools`](03_tools/) | a custom `@tool` the model can call | no |
| 04 | [`04_sandbox_agent`](04_sandbox_agent/) | `react` agent + `bash` in a Docker sandbox | **yes** |
| 05 | [`05_custom_scorer`](05_custom_scorer/) | custom scorer running `pytest`; image from a Dockerfile | **yes** |

## Going deeper

| # | Example | New concept | Sandbox? |
|---|---------|-------------|----------|
| 06 | [`06_hf_dataset`](06_hf_dataset/) | 🧠 load GSM8K from the Hub + chain-of-thought | no |
| 07 | [`07_multiple_scorers`](07_multiple_scorers/) | several scorers on one task | no |
| 08 | [`08_epochs_reliability`](08_epochs_reliability/) | epochs & pass@k reliability | no |
| 09 | [`09_model_roles`](09_model_roles/) | model roles (grader / red-team) | no |
| 10 | [`10_limits_guardrails`](10_limits_guardrails/) | message/token/time limits + resource caps | **yes** |
| 11 | [`11_web_search_agent`](11_web_search_agent/) | a `react` research agent with `web_search` | no |
| 12 | [`12_reasoning_cot`](12_reasoning_cot/) | 🧠 reasoning models + `self_critique` | no |
| 13 | [`13_eval_set`](13_eval_set/) | running a suite with `eval_set` | no |

## Vision (multimodal)

| # | Example | New concept | Sandbox? |
|---|---------|-------------|----------|
| 14 | [`14_image_vqa`](14_image_vqa/) | 🖼️ single-image question answering | no |
| 15 | [`15_image_chart`](15_image_chart/) | 🖼️ reading a chart image | no |
| 16 | [`16_image_compare`](16_image_compare/) | 🖼️ comparing two images in one prompt | no |

## AI-safety concepts (Apollo Research)

Faithful but harmless toy reproductions of behaviours Apollo studies. They
**detect/measure** the behaviour — they never ask the model to do anything
harmful.

| # | Example | Concept | Sandbox? |
|---|---------|---------|----------|
| 17 | [`17_apollo_sandbagging`](17_apollo_sandbagging/) | 🛡️ **sandbagging** — strategic underperformance | no |
| 18 | [`18_apollo_deception`](18_apollo_deception/) | 🛡️ **strategic deception** — lying to reach a goal | no |
| 19 | [`19_apollo_scheming_oversight`](19_apollo_scheming_oversight/) | 🛡️🧠 **scheming** — covertly disabling oversight | **yes** |

## Running any example

```bash
# set up once (see the repo README)
source .venv/bin/activate

# run an example (override the model as you like)
inspect eval examples/01_hello/task.py --model openai/gpt-4o-mini --limit 5
inspect view
```

Most examples need only a model API key. Examples **04, 05, 10, 19** also need
**Docker** running. The **vision** examples (14–16) need a vision-capable model
(`--model openai/gpt-4o`). All keys come from the repo-root `.env` (Inspect
searches parent directories), so you don't need a `.env` per example.

> **On the Apollo examples (17–19):** these are *propensity* evals — they ask the
> same thing under different framings, or watch what an agent does, to quantify
> whether a model sandbags, deceives, or schemes. Most current chat models score
> "safe" on these toys; the value is learning how such evals are *built*. See the
> [in-context scheming paper](https://www.apolloresearch.ai/research/frontier-models-are-capable-of-in-context-scheming/).
