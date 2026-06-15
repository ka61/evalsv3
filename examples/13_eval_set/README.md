# 13 · Running a suite (eval_set)

**Concepts:** `eval_set` for running many tasks with automatic retry of failures;
the `inspect eval-set` CLI.

```bash
# programmatic
python examples/13_eval_set/task.py

# CLI across multiple files
inspect eval-set examples/01_hello/task.py examples/02_multiple_choice/task.py \
  --model openai/gpt-4o-mini --log-dir ./logs/suite
```

`eval_set` is how you run a whole benchmark battery reproducibly — it groups the
logs under one directory and retries transient failures so a flaky run doesn't
sink the suite.
