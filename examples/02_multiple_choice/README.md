# 02 · Multiple choice

Deterministic scoring (no grader model needed). **Concepts:** `choices` on a
`Sample`, the `multiple_choice` solver, the `choice` scorer, letter targets.

```bash
inspect eval examples/02_multiple_choice/task.py --model openai/gpt-4o-mini
```

The `target` is the **letter** of the correct option (`"A"`, `"B"`, ...).

Try next — load a real benchmark from the Hugging Face Hub instead of inline
samples:

```python
from inspect_ai.dataset import hf_dataset, Sample

dataset = hf_dataset(
    "cais/mmlu", "all", split="test",
    sample_fields=lambda r: Sample(
        input=r["question"], choices=r["choices"], target="ABCD"[r["answer"]],
    ),
)
```
