"""Example 12 — Chain-of-thought: reasoning + self-critique.

Two ways to spend more "thinking" for a better answer:
  1. Reasoning models — pass --reasoning-effort and inspect the reasoning trace.
  2. self_critique — the model critiques and revises its own first answer.

Run:
    inspect eval examples/12_reasoning_cot/task.py --model openrouter/openai/gpt-5.4-mini
    # with a reasoning model:
    # inspect eval examples/12_reasoning_cot/task.py --model openrouter/openai/gpt-5.5 --reasoning-effort high
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate, self_critique, system_message


@task
def reasoning_demo():
    return Task(
        dataset=[
            Sample(
                input=(
                    "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than "
                    "the ball. How many cents does the ball cost?"
                ),
                target="5",
            ),
            Sample(
                input=(
                    "If it takes 5 machines 5 minutes to make 5 widgets, how many minutes "
                    "do 100 machines take to make 100 widgets?"
                ),
                target="5",
            ),
        ],
        solver=[
            system_message("Think step by step, then state the final answer clearly."),
            generate(),
            self_critique(),
        ],
        scorer=match(numeric=True),
    )
