# 02 · Multiple choice

Deterministic scoring — no grader model required. When answers are a fixed set of
options, you can score by exact selection, which is cheaper and perfectly
reproducible.

## What it teaches

- the `choices` field on a `Sample`
- the `multiple_choice` **solver** (formats options, asks for a letter)
- the `choice` **scorer** (checks the selected letter)
- why "letter targets" make grading unambiguous

## The code, line by line

```python
Sample(
    input="Which planet is known as the Red Planet?",
    choices=["Venus", "Mars", "Jupiter", "Saturn"],
    target="B",
)
...
solver=multiple_choice(),
scorer=choice(),
```

- **`choices`** lists the options. Inspect labels them A, B, C, D in order.
- **`target="B"`** is the *letter* of the correct option (here "Mars"). Targets
  are letters, not the option text, so grading is a simple equality check.
- **`multiple_choice()`** is a solver that renders the question + lettered options
  into a prompt, instructs the model to choose, and parses the chosen letter out
  of the reply.
- **`choice()`** compares the parsed letter to `target` and scores it.

## Run it

```bash
inspect eval examples/02_multiple_choice/task.py --model openai/gpt-4o-mini
```

## What happens, step by step

1. `multiple_choice()` builds a prompt like "… A) Venus B) Mars … Answer:".
2. The model replies; the solver extracts the letter it picked.
3. `choice()` marks it correct iff the letter equals `target`.
4. Accuracy + stderr are computed across all samples.

## What to look for

- the **rendered prompt** (note how choices were laid out and shuffled, if
  shuffling is enabled)
- the **parsed answer** (the single letter Inspect extracted)

## Try this next — load a real benchmark

Instead of inline samples, pull MMLU from the Hugging Face Hub:

```python
from inspect_ai.dataset import hf_dataset, Sample

dataset = hf_dataset(
    "cais/mmlu", "all", split="test",
    sample_fields=lambda r: Sample(
        input=r["question"], choices=r["choices"], target="ABCD"[r["answer"]],
    ),
)
```

This is exactly what example 06 does (with GSM8K). Most public MC benchmarks fit
this pattern.
