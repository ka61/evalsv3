# 03 · Custom tools (no sandbox)

Turn a chat model into a (tiny) tool user. A **tool** is a Python function the
model can call by emitting a structured request; Inspect runs it and feeds the
result back. This example's tool is pure in-process Python, so **no sandbox is
needed** — that comes in example 04, when tools start running arbitrary code.

## What it teaches

- the `@tool` decorator and the inner `async def execute(...)`
- why **type annotations + a docstring** are mandatory (they become the schema
  the model sees)
- `use_tools(...)` to expose tools to the model
- `match(numeric=True)` scoring for numeric answers
- the difference between an *inline* tool and one that needs a sandbox

## The code, line by line

```python
@tool
def add():
    async def execute(x: int, y: int):
        """Add two integers and return the sum.

        Args:
            x: The first number to add.
            y: The second number to add.
        """
        return x + y
    return execute
```

- **`@tool`** registers the factory. The outer function returns the actual
  `execute` coroutine — this two-layer pattern lets tools take configuration.
- **`async def execute`** is what runs when the model calls the tool. It's async
  so tools play nicely with Inspect's concurrency.
- **`x: int, y: int`** — the type hints tell the model what argument types to
  send. They are required.
- **the docstring** — the summary and the `Args:` lines become the tool's
  description and per-parameter docs the model reads. Required.

```python
Task(
    dataset=[Sample(input="Use the add tool to compute 21 + 21, ...", target="42")],
    solver=[use_tools(add()), generate()],
    scorer=match(numeric=True),
)
```

- **`use_tools(add())`** makes the `add` tool available for the next generation.
- **`generate()`** lets the model decide to call `add`, then produce a final
  answer using the result.
- **`match(numeric=True)`** scans the answer for the target *number* (so "42",
  "42.0", or "the answer is 42" all match).

## Run it

```bash
inspect eval examples/03_tools/task.py --model openrouter/openai/gpt-5.4-mini
```

## What happens, step by step

1. The model receives the prompt plus the `add` tool schema.
2. It emits a tool call: `add(x=21, y=21)`.
3. Inspect runs `execute(21, 21)` → `42` and returns it to the model.
4. The model writes a final answer; `match(numeric=True)` checks for `42`.

## What to look for

- the **tool call** in the transcript, with structured arguments
- the **tool result** returned to the model
- whether the model actually used the tool vs just doing the math itself (try
  forcing it via the prompt)

## Try this next

- add a second tool (e.g. `multiply`) and a question that needs both
- give a tool bad input handling and watch how errors are surfaced to the model
- note: the moment a tool runs *shell* or *file* commands, you must add a
  sandbox — that's example 04
