# 12 · Chain-of-thought: reasoning & self-critique

**Concepts:** explicit CoT via a system prompt, the `self_critique` solver, and
reasoning models (`--reasoning-effort`).

```bash
inspect eval examples/12_reasoning_cot/task.py --model openai/gpt-4o-mini
# reasoning model (emits a separate reasoning trace you can inspect):
inspect eval examples/12_reasoning_cot/task.py --model openai/o4-mini --reasoning-effort high
```

Both questions are classic "intuitive but wrong" traps (answers are 5 and 5).
`self_critique` adds a revise step; with a reasoning model you'll also see the
model's **reasoning tokens** in the transcript. Compare accuracy with and without
the CoT system message.
