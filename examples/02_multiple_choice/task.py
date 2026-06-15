"""Example 02 — Multiple choice.

Move from open-ended grading to deterministic scoring. The `multiple_choice`
solver formats the options and parses the model's selection; the `choice`
scorer checks it against the target letter.

Run:
    inspect eval examples/02_multiple_choice/task.py --model openai/gpt-4o-mini
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice


@task
def trivia_mc():
    return Task(
        dataset=[
            Sample(
                input="Which planet is known as the Red Planet?",
                choices=["Venus", "Mars", "Jupiter", "Saturn"],
                target="B",
            ),
            Sample(
                input="Which gas do plants primarily absorb for photosynthesis?",
                choices=["Oxygen", "Nitrogen", "Carbon dioxide", "Helium"],
                target="C",
            ),
            Sample(
                input="How many continents are there on Earth?",
                choices=["Five", "Six", "Seven", "Eight"],
                target="C",
            ),
        ],
        solver=multiple_choice(),
        scorer=choice(),
    )
