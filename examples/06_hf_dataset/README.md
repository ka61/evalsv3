# 06 · A real benchmark from the Hub + chain-of-thought

Up to now datasets were hand-written. Real evals load hundreds or thousands of
samples from the **Hugging Face Hub**. This example runs **GSM8K** (grade-school
math word problems) and uses **chain-of-thought (CoT)** prompting to boost
accuracy.

## What it teaches

- `hf_dataset(...)` to stream a dataset from the Hub
- a `record_to_sample` mapping function (raw record → `Sample`)
- **chain-of-thought** prompting via `prompt_template`
- numeric scoring with `match(numeric=True)`
- why a final-answer convention matters for scoring

## The code, line by line

```python
COT_TEMPLATE = """Solve the problem. Think step by step, then on the final line write:
ANSWER: <number>

{prompt}"""

def record_to_sample(record):
    answer = record["answer"].split("####")[-1].strip().replace(",", "")
    return Sample(input=record["question"], target=answer)

@task
def gsm8k_cot():
    return Task(
        dataset=hf_dataset("gsm8k", "main", split="test", sample_fields=record_to_sample),
        solver=[prompt_template(COT_TEMPLATE), generate()],
        scorer=match(numeric=True),
    )
```

- **`hf_dataset("gsm8k", "main", split="test", ...)`** downloads the GSM8K test
  split. `sample_fields=record_to_sample` converts each raw record into a
  `Sample`.
- **`record_to_sample`** — GSM8K's gold `answer` field ends with `#### 42`. We
  split on `####`, take the final number, strip commas, and use it as the target.
  The model never sees this; it's only for grading.
- **`prompt_template(COT_TEMPLATE)`** wraps each question. `{prompt}` is replaced
  by the sample's input. The template tells the model to **reason step by step**
  and end with `ANSWER: <number>` — the CoT instruction.
- **`generate()`** produces the worked solution + final line.
- **`match(numeric=True)`** scans the output for the target *number* (tolerant of
  formatting), so the final `ANSWER: 42` line scores correct.

## Run it

```bash
inspect eval examples/06_hf_dataset/task.py --model openrouter/openai/gpt-5.4-mini --limit 20
inspect view
```

`--limit 20` runs the first 20 problems — start small, GSM8K's test split is
~1,300 items.

## What happens, step by step

1. Inspect streams GSM8K from the Hub and maps records to samples.
2. Each question is wrapped in the CoT template and sent to the model.
3. The model writes step-by-step reasoning ending in `ANSWER: N`.
4. `match(numeric=True)` checks `N` against the gold number.

## What to look for

- the model's **reasoning** in the transcript (the chain of thought)
- cases where the reasoning is right but the final number is mis-stated — a
  scoring/format issue, not a math one

## Try this next — measure the CoT effect

Remove the "Think step by step" line from the template and re-run. Accuracy
should drop noticeably — that gap *is* the value of chain-of-thought, quantified.
For a stronger version, run with a reasoning model (see example 12).
