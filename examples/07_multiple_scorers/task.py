"""Example 07 — Multiple scorers on one task.

You can grade the same output several ways. Here a deterministic substring check
runs alongside a model-graded check; Inspect reports both, each with accuracy and
a standard error.

Run:
    inspect eval examples/07_multiple_scorers/task.py --model openai/gpt-4o-mini
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, model_graded_qa
from inspect_ai.solver import generate, system_message


@task
def multi_scored():
    return Task(
        dataset=[
            Sample(input="Name the largest planet in the Solar System.", target="Jupiter"),
            Sample(input="What is the chemical symbol for gold?", target="Au"),
        ],
        solver=[system_message("Answer concisely."), generate()],
        scorer=[includes(), model_graded_qa()],
    )
