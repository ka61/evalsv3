"""Example 05 — Agentic coding with a custom scorer.

The full shape of a real agentic eval: an agent edits code inside a Docker
sandbox, and a CUSTOM scorer grades it by running the project's test suite in
that same sandbox.

Concepts: a custom `@scorer`, `sandbox().exec(...)` from within the scorer,
mounting local files into the sandbox, a `react` agent with `bash` + `text_editor`,
and building a sandbox image from a Dockerfile.

Requires Docker. Inspect builds the image from the Dockerfile / compose.yaml here.

Run:
    inspect eval examples/05_custom_scorer/task.py --model anthropic/claude-sonnet-4-0
    inspect view
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState
from inspect_ai.tool import bash, text_editor
from inspect_ai.util import sandbox

ASSETS = Path(__file__).parent / "assets"


@scorer(metrics=[accuracy(), stderr()])
def tests_pass():
    async def score(state: TaskState, target: Target):
        # run the project's tests inside the sandbox; success == fix worked
        result = await sandbox().exec(["python", "-m", "pytest", "-q"], timeout=120)
        return Score(
            value="C" if result.success else "I",
            explanation=(result.stdout + result.stderr)[-2000:],
        )

    return score


@task
def fix_bug():
    return Task(
        dataset=[
            Sample(
                input=(
                    "The tests in this project are failing. Fix the code in buggy.py "
                    "so that `pytest` passes, then submit."
                ),
                files={
                    "buggy.py": str(ASSETS / "buggy.py"),
                    "test_buggy.py": str(ASSETS / "test_buggy.py"),
                },
            )
        ],
        solver=react(
            prompt="You are a precise software engineer. Fix the failing tests, then submit.",
            tools=[bash(timeout=120), text_editor()],
            attempts=3,
        ),
        scorer=tests_pass(),
        sandbox="docker",
    )
