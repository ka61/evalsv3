# Examples

Worked Inspect examples in increasing order of complexity. Do them in order —
each introduces one new idea on top of the last.

| # | Example | New concept | Sandbox? |
|---|---------|-------------|----------|
| 01 | [`01_hello`](01_hello/) | dataset → solver → model-graded scorer | no |
| 02 | [`02_multiple_choice`](02_multiple_choice/) | choices + deterministic `choice` scorer | no |
| 03 | [`03_tools`](03_tools/) | a custom `@tool` the model can call | no |
| 04 | [`04_sandbox_agent`](04_sandbox_agent/) | `react` agent + `bash` in a Docker sandbox | **yes** |
| 05 | [`05_custom_scorer`](05_custom_scorer/) | custom scorer running `pytest`; image from a Dockerfile | **yes** |

## Running any example

```bash
# set up once (see the repo README)
source .venv/bin/activate

# run an example (override the model as you like)
inspect eval examples/01_hello/task.py --model openai/gpt-4o-mini --limit 5
inspect view
```

Examples 01–03 need only a model API key. Examples 04–05 also need **Docker**
running locally. All keys come from the repo-root `.env` (Inspect searches
parent directories), so you don't need a separate `.env` per example.
