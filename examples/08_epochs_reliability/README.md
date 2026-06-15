# 08 · Epochs & pass@k

**Concepts:** `Epochs(count, reducer)`, the `--epochs` flag, and reducers like
`mean`, `pass_at_1`, `pass_at_k`.

```bash
inspect eval examples/08_epochs_reliability/task.py --model openai/gpt-4o-mini --epochs 5
```

Repeating samples turns a single lucky/unlucky run into a reliability estimate.
Use `pass_at_k` for "can it ever get this right in k tries" and `mean` for the
average. Always report the **standard error** next to accuracy.
