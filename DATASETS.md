# Datasets

This repo uses a mix of tiny **inline** datasets (so examples run instantly with
no downloads), one real **Hugging Face** benchmark, **generated images**, and
files **mounted into sandboxes**. This page explains what each example uses and
then gives a reference table of popular public benchmarks you can plug in.

## Datasets used in the examples

| Example | Data it uses | Where it comes from |
|---|---|---|
| 01 `hello` | 3 inline Q&A samples | hard-coded `Sample`s |
| 02 `multiple_choice` | 3 inline MC questions | hard-coded `Sample`s |
| 03 `tools` | 2 inline arithmetic prompts | hard-coded `Sample`s |
| 04 `sandbox_agent` | 1 sample + a `flag.txt` mounted into the sandbox | `Sample.files` |
| 05 `custom_scorer` | a buggy module + tests mounted into the sandbox | `assets/` → `Sample.files` |
| 06 `hf_dataset` | **GSM8K** (grade-school math), test split | Hugging Face Hub (`gsm8k`) |
| 07 `multiple_scorers` | 2 inline facts | hard-coded `Sample`s |
| 08 `epochs_reliability` | 2 inline prompts | hard-coded `Sample`s |
| 09 `model_roles` | 1 inline prompt | hard-coded `Sample`s |
| 10 `limits_guardrails` | 1 inline agent task | hard-coded `Sample` |
| 11 `web_search_agent` | 2 inline questions | hard-coded `Sample`s |
| 12 `reasoning_cot` | 2 inline reasoning puzzles | hard-coded `Sample`s |
| 13 `eval_set` | 2 inline mini-tasks | hard-coded `Sample`s |
| 14–16 vision | generated PNGs (shape, chart, two squares) | `assets/` (made with Pillow) |
| 17 `apollo_sandbagging` | 5 arithmetic MC × 2 conditions | generated in code |
| 18 `apollo_deception` | 2 scripted sales scenarios | hard-coded `Sample`s |
| 19 `apollo_scheming_oversight` | a goal + `oversight_config.yaml` in a sandbox | `assets/` → `Sample.files` |
| 20 `scheming_eval_awareness` | 2 generated screenshots (eval vs prod) | `assets/` |
| 21 `scheming_visual_sandbagging` | 3 generated dot images × 2 conditions | `assets/` |
| 22 `scheming_visual_oversight` | dashboard image + `oversight_config.yaml` | `assets/` |
| 23 `fingerprint_manipulation` | 13 real fingerprints, 11 pairs × 4 pressure levels | **SOCOFing** dataset → `assets/` (see `assets/SOURCE.md`) |

**Why mostly inline/generated?** So every example runs offline with just a model
key, and the *concept* is front-and-centre rather than a big download. Example 06
shows the real thing: streaming a benchmark from the Hub.

## Loading a real dataset from the Hub

```python
from inspect_ai.dataset import hf_dataset, Sample

dataset = hf_dataset(
    "gsm8k", "main", split="test",
    sample_fields=lambda r: Sample(
        input=r["question"],
        target=r["answer"].split("####")[-1].strip(),
    ),
)
```

`hf_dataset(repo, config, split=..., sample_fields=...)` streams the dataset and
maps each raw record onto a `Sample`. Most public benchmarks fit this pattern.

**Don't reinvent it:** the [`inspect_evals`](https://github.com/UKGovernmentBEIS/inspect_evals)
package already wraps 200+ benchmarks — run one directly:

```bash
inspect eval inspect_evals/gsm8k --model openrouter/openai/gpt-5.4-mini --limit 20
```

## Popular evaluation datasets (reference)

A field guide to widely-used benchmarks: what each measures, when it appeared, and
roughly how big it is. Sizes are approximate and vary by split/version.

| Dataset | Released | Domain | What it tests | Size | Source |
|---|---|---|---|---|---|
| **ARC** | 2018 | Knowledge | Grade-school science MC (Easy + Challenge) | ~7,800 | [allenai/ai2_arc](https://huggingface.co/datasets/allenai/ai2_arc) |
| **HellaSwag** | 2019 | Commonsense | Sentence-completion commonsense | ~70k | [Rowan/hellaswag](https://huggingface.co/datasets/Rowan/hellaswag) |
| **MMLU** | 2020 | Knowledge | MC across 57 subjects | ~15,900 | [cais/mmlu](https://huggingface.co/datasets/cais/mmlu) |
| **TruthfulQA** | 2021 | Truthfulness | Resisting common human falsehoods | 817 | [truthful_qa](https://huggingface.co/datasets/truthful_qa) |
| **GSM8K** | 2021 | Math | Grade-school word problems (multi-step) | 8,500 | [gsm8k](https://huggingface.co/datasets/gsm8k) |
| **MATH** | 2021 | Math | Competition mathematics | 12,500 | [hendrycks/competition_math](https://huggingface.co/datasets/hendrycks/competition_math) |
| **HumanEval** | 2021 | Code | Python function synthesis, unit-tested | 164 | [openai_humaneval](https://huggingface.co/datasets/openai_humaneval) |
| **MBPP** | 2021 | Code | Entry-level Python problems | ~1,000 | [mbpp](https://huggingface.co/datasets/mbpp) |
| **BIG-Bench Hard** | 2022 | Reasoning | 23 hard tasks where models lagged humans | 6,500 | [lukaemon/bbh](https://huggingface.co/datasets/lukaemon/bbh) |
| **IFEval** | 2023 | Instruction-following | Verifiable instruction compliance | ~540 | [google/IFEval](https://huggingface.co/datasets/google/IFEval) |
| **GPQA** | 2023 | Science (hard) | PhD-level "Google-proof" Q&A | 448 | [Idavidrein/gpqa](https://huggingface.co/datasets/Idavidrein/gpqa) |
| **GAIA** | 2023 | Agentic | Real-world assistant tasks needing tools | 466 | [gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) |
| **SWE-bench** | 2023 | Agentic code | Resolve real GitHub issues so tests pass | 2,294 | [princeton-nlp/SWE-bench](https://huggingface.co/datasets/princeton-nlp/SWE-bench) |
| **MMLU-Pro** | 2024 | Knowledge (hard) | Harder, cleaner MMLU with 10 options | ~12,000 | [TIGER-Lab/MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) |
| **Cybench** | 2024 | Cyber / agentic | Capture-the-flag challenges in sandboxes | 40 | [project site](https://cybench.github.io/) |

## A warning on saturation & contamination

The older knowledge/math/code sets (MMLU, GSM8K, HumanEval) are largely
**saturated** — frontier models score above ~90% — and may have leaked into
training data (**contamination**). For current signal, prefer harder, newer, or
agentic sets (GPQA, MMLU-Pro, SWE-bench, GAIA, Cybench) and **always report the
model and date** alongside a score.

## Licensing

Each dataset carries its own license and terms — check the source before using a
dataset in your own work, especially commercially.
