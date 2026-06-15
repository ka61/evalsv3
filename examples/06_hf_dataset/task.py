"""Example 06 — A real benchmark from the Hub, with chain-of-thought.

Load GSM8K (grade-school math) from the Hugging Face Hub, prompt the model to
reason step by step (chain-of-thought) and end with a clear final answer, then
score the number.

Run:
    inspect eval examples/06_hf_dataset/task.py --model openai/gpt-4o-mini --limit 20
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, hf_dataset
from inspect_ai.scorer import match
from inspect_ai.solver import generate, prompt_template

COT_TEMPLATE = """Solve the problem. Think step by step, then on the final line write:
ANSWER: <number>

{prompt}"""


def record_to_sample(record):
    # GSM8K gold answers look like: "...\n#### 42"
    answer = record["answer"].split("####")[-1].strip().replace(",", "")
    return Sample(input=record["question"], target=answer)


@task
def gsm8k_cot():
    return Task(
        dataset=hf_dataset(
            "gsm8k", "main", split="test", sample_fields=record_to_sample
        ),
        solver=[prompt_template(COT_TEMPLATE), generate()],
        scorer=match(numeric=True),
    )
