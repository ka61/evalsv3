"""Example 01 — Hello, eval.

The smallest possible Inspect eval: ask a few questions and let a grader model
judge the answers. No tools, no sandbox — just dataset -> solver -> scorer.

Run:
    inspect eval examples/01_hello/task.py --model openai/gpt-4o-mini
    inspect view
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import generate, system_message


@task
def hello():
    return Task(
        dataset=[
            Sample(input="What is the capital of France?", target="Paris"),
            Sample(input="Who wrote Pride and Prejudice?", target="Jane Austen"),
            Sample(input="What is 7 multiplied by 6?", target="42"),
        ],
        solver=[
            system_message("Answer as concisely as possible."),
            generate(),
        ],
        scorer=model_graded_qa(),
    )
