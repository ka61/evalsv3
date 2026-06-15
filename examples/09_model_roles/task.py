"""Example 09 — Model roles.

Give the grader its own named role so you can swap which model grades without
touching code. Built-in model-graded scorers look for the `grader` role.

Run:
    inspect eval examples/09_model_roles/task.py \
        --model openai/gpt-4o-mini --model-role grader=openai/gpt-4o
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import generate


@task
def roles_demo():
    return Task(
        dataset=[
            Sample(
                input="Explain in one sentence why the sky is blue.",
                target="Rayleigh scattering of sunlight by the atmosphere.",
            )
        ],
        solver=generate(),
        scorer=model_graded_qa(),
        # default grader; override on the CLI with --model-role grader=...
        model_roles={"grader": "openai/gpt-4o-mini"},
    )
