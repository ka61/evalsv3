"""Example 10 — Limits and guardrails.

Agents can loop forever or burn tokens. Inspect caps messages, tokens, time, and
working time per sample (and CPU/memory via the sandbox). This is a tiny agent;
the README shows how to bound it.

Run (with limits):
    inspect eval examples/10_limits_guardrails/task.py --model openrouter/openai/gpt-5.4-mini \
        --message-limit 8 --token-limit 50000 --time-limit 120
"""

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.tool import bash


@task
def bounded_agent():
    return Task(
        dataset=[
            Sample(
                input="Run `date -u` with bash and submit the full output line.",
                target="UTC",
            )
        ],
        solver=react(tools=[bash(timeout=30)]),
        scorer=includes(),
        sandbox="docker",
    )
