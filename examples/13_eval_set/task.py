"""Example 13 — Running a suite with eval_set.

`eval_set` runs many tasks together and automatically retries failed ones. Run
this file directly with python, or point `inspect eval-set` at several tasks.

    python examples/13_eval_set/task.py
    # or:
    inspect eval-set examples/01_hello/task.py examples/02_multiple_choice/task.py \
        --model openai/gpt-4o-mini --log-dir ./logs/suite
"""

from inspect_ai import Task, eval_set, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate


@task
def capitals_quiz():
    return Task(
        dataset=[Sample(input="Capital of Japan?", target="Tokyo")],
        solver=generate(),
        scorer=includes(),
    )


@task
def elements_quiz():
    return Task(
        dataset=[Sample(input="Chemical symbol for sodium?", target="Na")],
        solver=generate(),
        scorer=includes(),
    )


if __name__ == "__main__":
    success, logs = eval_set(
        tasks=[capitals_quiz(), elements_quiz()],
        model="openai/gpt-4o-mini",
        log_dir="./logs/suite-13",
    )
    print("all tasks succeeded:", success)
