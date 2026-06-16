"""Example 16 — Vision: comparing two images.

Put TWO images in one message and ask a relational question. This is the shape of
many real multimodal evals (spot-the-difference, before/after, consistency).

Run:
    inspect eval examples/16_image_compare/task.py --model openrouter/openai/gpt-5.4
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

ASSETS = Path(__file__).parent / "assets"
LEFT = str(ASSETS / "left.png")
RIGHT = str(ASSETS / "right.png")


@task
def image_compare():
    return Task(
        dataset=[
            Sample(
                input=[
                    ChatMessageUser(
                        content=[
                            ContentText(
                                text="Here are two images. Are the squares the same colour? Answer yes or no."
                            ),
                            ContentImage(image=LEFT),
                            ContentImage(image=RIGHT),
                        ]
                    )
                ],
                target="no",
            )
        ],
        solver=generate(),
        scorer=includes(),
    )
