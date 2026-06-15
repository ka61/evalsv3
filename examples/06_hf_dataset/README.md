# 06 · A real benchmark + chain-of-thought

**Concepts:** `hf_dataset` (load GSM8K from the Hub), `record_to_sample` field
mapping, **chain-of-thought** prompting via `prompt_template`, numeric `match`.

```bash
inspect eval examples/06_hf_dataset/task.py --model openai/gpt-4o-mini --limit 20
```

The CoT template asks the model to reason step by step and end with
`ANSWER: <number>`; the `match(numeric=True)` scorer compares the number.
Try removing the "think step by step" line and watch accuracy drop — that's the
CoT effect, measured.
