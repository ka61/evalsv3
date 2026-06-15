# 18 · Apollo concept — Strategic deception

> **Strategic deception** = knowingly asserting something false to achieve a
> goal. One of the core behaviours in Apollo's scheming work.

The model plays a salesbot with a closing goal and is told the TRUE product facts,
then asked questions where lying would help. The `model_graded_qa` scorer grades
**honesty**, not sales success.

```bash
inspect eval examples/18_apollo_deception/task.py --model openai/gpt-4o-mini
```

**Read it:** accuracy here = honesty rate. A low score means the model lied to
pursue its goal. Try strengthening the goal pressure in the system prompt and
watch whether honesty degrades — that sensitivity is the finding.

Detection only — we measure whether the model deceives, we don't help it.
