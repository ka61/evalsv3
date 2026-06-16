"""Example 15 — Vision: chart understanding.

Ask a vision model to read a simple bar chart and identify the tallest bar.

Run:
    inspect eval examples/15_image_chart/task.py --model openrouter/openai/gpt-5.4
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

IMG = str(Path(__file__).parent / "assets" / "sales.png")


@task
def chart_reading():
    return Task(
        dataset=[
            Sample(
                input=[
                    ChatMessageUser(
                        content=[
                            ContentText(
                                text=(
                                    "This bar chart shows units sold per product (A-D). "
                                    "Which product sold the most? Answer with the single letter."
                                )
                            ),
                            ContentImage(image=IMG),
                        ]
                    )
                ],
                target="C",
            )
        ],
        solver=generate(),
        scorer=includes(),
    )
