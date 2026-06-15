# 12 · Chain-of-thought: reasoning models & self-critique

Two complementary ways to spend more "thinking" for a better answer: explicit
**chain-of-thought** prompting + **`self_critique`**, and dedicated **reasoning
models** that emit a separate reasoning trace.

## What it teaches

- CoT via a `system_message` instruction
- the `self_critique` solver (model critiques and revises its own answer)
- reasoning models and `--reasoning-effort`
- where to find the reasoning trace in the log

## The code, line by line

```python
@task
def reasoning_demo():
    return Task(
        dataset=[
            Sample(input="A bat and a ball cost $1.10 ... How many cents does the ball cost?",
                   target="5"),
            Sample(input="If 5 machines take 5 minutes to make 5 widgets, how many minutes ...",
                   target="5"),
        ],
        solver=[
            system_message("Think step by step, then state the final answer clearly."),
            generate(),
            self_critique(),
        ],
        scorer=match(numeric=True),
    )
```

- both questions are classic **intuition traps** (the tempting answers 10¢ and
  100 minutes are wrong; both correct answers are 5).
- **`system_message("Think step by step…")`** is the CoT instruction — it pushes
  the model to reason before answering.
- **`generate()`** produces the first answer (with reasoning).
- **`self_critique()`** adds a second pass: the model is asked to critique its own
  answer and revise if needed — often catching the trap.
- **`match(numeric=True)`** scores the final number.

## Run it

```bash
# ordinary model with CoT + self-critique
inspect eval examples/12_reasoning_cot/task.py --model openai/gpt-4o-mini

# a reasoning model (emits a separate reasoning trace)
inspect eval examples/12_reasoning_cot/task.py --model openai/o4-mini --reasoning-effort high
```

`--reasoning-effort` (values like `low|medium|high`) trades tokens/cost for more
deliberation on reasoning models.

## What happens, step by step

1. The CoT system message + question go to the model.
2. `generate()` returns reasoning + a first answer.
3. `self_critique()` asks the model to review and possibly revise.
4. `match(numeric=True)` checks the final answer.

## What to look for

- the **reasoning** in the transcript; with a reasoning model you'll see a
  distinct **reasoning trace** separate from the answer
- whether `self_critique` *changed* a wrong first answer to a right one

## Try this next

- remove the CoT system message and/or `self_critique` and watch accuracy fall —
  that delta is the value of "more thinking", measured
- compare `--reasoning-effort low` vs `high` on a reasoning model
