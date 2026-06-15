# 09 · Model roles

**Concepts:** `model_roles` on a `Task`, the `--model-role` CLI flag, and the
fact that model-graded scorers use the `grader` role by default.

```bash
inspect eval examples/09_model_roles/task.py \
  --model openai/gpt-4o-mini --model-role grader=openai/gpt-4o
```

Roles let the *subject* model and the *grader* model vary independently — useful
for red-team/blue-team setups and for keeping a strong, fixed grader while you
sweep the model under test.
