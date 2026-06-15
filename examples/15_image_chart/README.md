# 15 · Vision — chart understanding

**Concepts:** document/chart reading with a vision model; deterministic scoring.

```bash
inspect eval examples/15_image_chart/task.py --model openai/gpt-4o
```

`assets/sales.png` is a bar chart where product **C** is tallest. Chart reading
is a common real eval (finance, science) and a good test of whether a model
actually *looks* versus guessing.
