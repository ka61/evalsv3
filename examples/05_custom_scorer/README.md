# 05 · Agentic coding with a custom scorer

The capstone: an agent fixes real code and is graded by **running tests**.
**Concepts:** a custom `@scorer`, `sandbox().exec()` inside the scorer, building
a sandbox image from a `Dockerfile`, `react` with `bash` + `text_editor`, and
multiple `attempts`.

**Requires Docker.** The first run builds the image (cached afterwards).

```bash
inspect eval examples/05_custom_scorer/task.py --model anthropic/claude-sonnet-4-0
inspect view
```

Flow:

1. `buggy.py` (a wrong `add`) and `test_buggy.py` are mounted into the sandbox
2. the agent reads the failing tests, edits `buggy.py`, and submits
3. the `tests_pass` scorer runs `pytest` in the sandbox — green means correct
4. with `attempts=3`, a failed submission lets the agent try again

This is the same shape as benchmarks like SWE-bench: repo + failing tests in,
a fix attempt, tests as the score.

Files:

- `task.py` — the eval
- `Dockerfile` / `compose.yaml` — the sandbox image (tool-support base + pytest)
- `assets/` — the buggy module and its tests
