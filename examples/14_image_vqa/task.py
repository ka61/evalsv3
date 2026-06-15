"""Example 14 — Vision: single-image question answering.

Multimodal input. Build a chat message that mixes text and an image, then ask a
vision-capable model what it sees (gpt-4o, claude-sonnet-4-0, gemini-2.5-pro).

Run:
    inspect eval examples/14_image_vqa/task.py --model openai/gpt-4o
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

IMG = str(Path(__file__).parent / "assets" / "shape.png")


@task
def image_vqa():
    return Task(
        dataset=[
            Sample(
                input=[
                    ChatMessageUser(
                        content=[
                            ContentText(text="What colour is the shape? Answer with one word."),
                            ContentImage(image=IMG),
                        ]
                    )
                ],
                target="red",
            )
        ],
        solver=generate(),
        scorer=includes(),
    )
