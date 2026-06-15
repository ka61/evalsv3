# 10 · Limits & guardrails

**Concepts:** per-sample budgets that stop runaway agents, plus sandbox resource
caps. Requires Docker.

```bash
inspect eval examples/10_limits_guardrails/task.py --model openai/gpt-4o-mini \
  --message-limit 8 --token-limit 50000 --time-limit 120 --working-limit 90
```

| Limit | Flag |
|-------|------|
| messages per sample | `--message-limit` |
| tokens per sample | `--token-limit` |
| wall-clock per sample | `--time-limit` |
| active working time | `--working-limit` |
| dollar cost per sample | `--cost-limit` |
| concurrent containers | `--max-sandboxes` |

CPU/memory are bounded in `compose.yaml` (`cpus`, `mem_limit`). Limits are the
difference between a safe agentic eval and a surprise bill.
