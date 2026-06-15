"""Example 08 — Reliability with epochs and pass@k.

Run each sample multiple times and reduce the repeats into one score. Essential
for stochastic tasks where a single run is noisy.

Run:
    inspect eval examples/08_epochs_reliability/task.py --model openai/gpt-4o-mini --epochs 5
"""

from inspect_ai import Epochs, Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate


@task
def reliability():
    return Task(
        dataset=[
            Sample(input="Reply with ONLY the number 7.", target="7"),
            Sample(input="Reply with ONLY the word 'banana'.", target="banana"),
        ],
        solver=generate(),
        # repeat each sample 5x; 'pass_at_1' = correct if any single attempt is right
        epochs=Epochs(5, "pass_at_1"),
        scorer=match(),
    )
