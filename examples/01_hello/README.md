# 01 · Hello, eval

The minimal Inspect eval. **Concepts:** `Task`, `Sample`, a chain solver
(`system_message` + `generate`), and a model-graded scorer.

```bash
inspect eval examples/01_hello/task.py --model openai/gpt-4o-mini
inspect view
```

What to notice in the log viewer:

- each **sample** has an input, the model's completion, and a score
- the `model_graded_qa` scorer used a model to judge correctness (look at the
  grader's explanation)
- the headline metric is **accuracy** with a **standard error**

Try next: swap the model (`--model anthropic/claude-sonnet-4-0`) and compare.
