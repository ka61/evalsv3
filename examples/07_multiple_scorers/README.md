# 07 · Multiple scorers

**Concepts:** passing a *list* of scorers; comparing a cheap deterministic
scorer (`includes`) against a `model_graded_qa` scorer on the same outputs.

```bash
inspect eval examples/07_multiple_scorers/task.py --model openai/gpt-4o-mini
```

The log shows a metric block per scorer. Watch where they disagree — that gap is
where "did the exact string appear" and "is the answer actually right" diverge.
