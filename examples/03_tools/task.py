"""Example 03 — Custom tools (no sandbox yet).

Give the model a tool it can call. This `add` tool is pure Python and makes no
network or filesystem calls, so it runs inline — no sandbox required. (Tools
that execute arbitrary code, like bash/python, DO need a sandbox: see 04.)

Concepts: the `@tool` decorator, typed args + docstring as the tool schema,
`use_tools`, and numeric `match` scoring.

Run:
    inspect eval examples/03_tools/task.py --model openrouter/openai/gpt-5.4-mini
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import tool


@tool
def add():
    async def execute(x: int, y: int):
        """Add two integers and return the sum.

        Args:
            x: The first number to add.
            y: The second number to add.
        """
        return x + y

    return execute


@task
def calculator():
    return Task(
        dataset=[
            Sample(
                input="Use the add tool to compute 21 + 21, then reply with just the number.",
                target="42",
            ),
            Sample(
                input="Use the add tool to compute 128 + 256, then reply with just the number.",
                target="384",
            ),
        ],
        solver=[use_tools(add()), generate()],
        scorer=match(numeric=True),
    )
