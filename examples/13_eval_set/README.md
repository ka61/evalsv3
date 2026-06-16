# 13 · Running a suite with `eval_set`

Real evaluation means running **many tasks** reproducibly, not one file at a time.
`eval_set` runs a batch together, groups their logs, and **automatically retries**
transient failures.

## What it teaches

- the `eval_set(...)` function (programmatic) and `inspect eval-set` (CLI)
- grouping a run under one `log_dir`
- automatic retry of failed tasks
- structuring a repo so suites are one command

## The code, line by line

```python
@task
def capitals_quiz():
    return Task(dataset=[Sample(input="Capital of Japan?", target="Tokyo")],
                solver=generate(), scorer=includes())

@task
def elements_quiz():
    return Task(dataset=[Sample(input="Chemical symbol for sodium?", target="Na")],
                solver=generate(), scorer=includes())

if __name__ == "__main__":
    success, logs = eval_set(
        tasks=[capitals_quiz(), elements_quiz()],
        model="openrouter/openai/gpt-5.4-mini",
        log_dir="./logs/suite-13",
    )
    print("all tasks succeeded:", success)
```

- **two `@task`s** in one file — a mini suite.
- **`if __name__ == "__main__":`** guards the runner so importing the file (as CI
  does) doesn't kick off an eval.
- **`eval_set(tasks=[...], model=..., log_dir=...)`** runs them all, writing logs
  under one directory and retrying failures. It returns `(success, logs)`.

## Run it

```bash
# programmatic
python examples/13_eval_set/task.py

# CLI across multiple files
inspect eval-set examples/01_hello/task.py examples/02_multiple_choice/task.py \
  --model openrouter/openai/gpt-5.4-mini --log-dir ./logs/suite
```

## What happens, step by step

1. `eval_set` schedules every task.
2. Each runs like a normal eval; logs land under `log_dir`.
3. If a task errors (e.g. a transient API hiccup), `eval_set` retries it.
4. `success` is `True` only if all tasks completed.

## What to look for

- all task logs grouped under `./logs/suite-13`
- on a forced failure, the **retry** behaviour
- `inspect view --log-dir ./logs/suite-13` to browse the whole suite

## Try this next

- add `examples/06_hf_dataset/task.py` to the CLI suite for a real benchmark
- run a suite that varies the model via `--model-role` (example 09)
- this is the building block for the "run the whole battery nightly" workflow
