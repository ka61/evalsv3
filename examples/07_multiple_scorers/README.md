# 07 · Multiple scorers on one task

The same model output can be judged several ways at once. Here a cheap
deterministic check runs *alongside* a model-graded check, and Inspect reports a
separate metric block for each — so you can see where they agree and disagree.

## What it teaches

- passing a **list** of scorers to a `Task`
- combining a deterministic scorer (`includes`) with a `model_graded_qa` scorer
- reading multiple metric blocks in one log
- when "the exact word appeared" and "the answer is actually right" diverge

## The code, line by line

```python
@task
def multi_scored():
    return Task(
        dataset=[
            Sample(input="Name the largest planet in the Solar System.", target="Jupiter"),
            Sample(input="What is the chemical symbol for gold?", target="Au"),
        ],
        solver=[system_message("Answer concisely."), generate()],
        scorer=[includes(), model_graded_qa()],
    )
```

- **`scorer=[includes(), model_graded_qa()]`** — the key line. Each scorer runs
  on every sample independently:
  - `includes()` — correct iff the `target` string appears in the answer
    (case-insensitive substring). Fast, free, but literal.
  - `model_graded_qa()` — a grader model decides correctness semantically (so
    "the symbol is Au" and "gold is Au" both count, and a wrong-but-contains-Au
    answer can be caught).

## Run it

```bash
inspect eval examples/07_multiple_scorers/task.py --model openai/gpt-4o-mini
```

## What happens, step by step

1. Each sample is solved once.
2. **Both** scorers grade that single output.
3. Inspect aggregates each scorer separately → two metric blocks
   (`includes/accuracy`, `model_graded_qa/accuracy`), each with a stderr.

## What to look for

- two metric blocks in the summary
- a sample where `includes` says wrong but the grader says right (the model
  phrased the right answer without the exact target string), or vice-versa

## Try this next

- add a third scorer, e.g. `match()` (stricter than `includes`)
- give the grader custom `instructions=` (see example 18) to change what "correct"
  means
- this pattern is how you separate **format** correctness from **semantic**
  correctness in real evals
