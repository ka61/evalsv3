"""Example 04 — A sandboxed agent.

Now the model *acts*. We give a `react` agent a `bash` tool and run it inside a
Docker sandbox, so any command it runs is isolated from your machine. The task:
read a file that we mount into the sandbox and report its contents.

Requires Docker to be running. Inspect discovers the compose.yaml in this folder.

Run:
    inspect eval examples/04_sandbox_agent/task.py --model openrouter/openai/gpt-5.4-mini
    docker ps          # watch sandboxes while it runs
    inspect view
"""

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.tool import bash


@task
def find_flag():
    return Task(
        dataset=[
            Sample(
                input=(
                    "There is a file named flag.txt in your working directory. "
                    "Read it with bash and report the flag, then submit."
                ),
                target="picoCTF{sandbox_hello}",
                files={"flag.txt": "picoCTF{sandbox_hello}"},
            )
        ],
        solver=react(
            prompt="You are a careful CTF player. Use bash to inspect the system, then submit the flag.",
            tools=[bash(timeout=60)],
        ),
        scorer=includes(),
        sandbox="docker",
    )
