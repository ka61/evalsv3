# 10 · Limits & guardrails

Agents can loop forever, blow the context window, or run up a bill. Inspect
provides **per-sample budgets** (messages, tokens, time, working time, cost) and
**sandbox resource caps** (CPU, memory). Treat these as required, not optional.

## What it teaches

- the per-sample limit flags and what each bounds
- sandbox CPU/memory caps via `compose.yaml`
- how a limit terminates a sample (and how that shows in the log)
- the safety/cost discipline that makes agentic evals runnable

## The code

```python
@task
def bounded_agent():
    return Task(
        dataset=[Sample(input="Run `date -u` with bash and submit the full output line.",
                        target="UTC")],
        solver=react(tools=[bash(timeout=30)]),
        scorer=includes(),
        sandbox="docker",
    )
```

The task itself is deliberately tiny — a `react` agent that runs one command.
The point is **how you run it**, with limits attached.

## Run it with limits

```bash
inspect eval examples/10_limits_guardrails/task.py --model openrouter/openai/gpt-5.4-mini \
  --message-limit 8 --token-limit 50000 --time-limit 120 --working-limit 90
```

| Limit | Flag | Bounds |
|-------|------|--------|
| messages | `--message-limit` | total messages per sample (caps agent loops) |
| tokens | `--token-limit` | total tokens per sample |
| time | `--time-limit` | wall-clock seconds per sample |
| working time | `--working-limit` | active model/tool time (excludes waiting) |
| cost | `--cost-limit` | dollars per sample (needs model cost data) |
| sandboxes | `--max-sandboxes` | concurrent containers |

### Sandbox caps — `compose.yaml`

```yaml
services:
  default:
    image: aisiuk/inspect-tool-support
    init: true
    command: tail -f /dev/null
    cpus: 1.0          # CPU cap
    mem_limit: 0.5gb   # memory cap
    network_mode: none # no egress
```

## What happens when a limit trips

The sample is **terminated** at the limit and the log records the reason (e.g.
"message limit exceeded"). The eval keeps running other samples. This is how you
stop one runaway agent from hanging or bankrupting a whole run.

## What to look for

- run once with a generous limit, once with `--message-limit 2`, and compare —
  the second should terminate early with a limit reason in the transcript

## Try this next

- add `--cost-limit 0.05` (with model cost config) to cap spend per sample
- lower `mem_limit` and run a memory-hungry command to see the sandbox enforce it
- combine with example 19 (scheming) — limits keep long agent runs bounded
