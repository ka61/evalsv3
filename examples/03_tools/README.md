# 03 · Custom tools (no sandbox)

Turn a chat model into a (tiny) tool user. **Concepts:** `@tool`, the typed
`execute` signature + docstring becoming the schema the model sees, `use_tools`,
and `match(numeric=True)`.

```bash
inspect eval examples/03_tools/task.py --model openai/gpt-4o-mini
```

In the transcript you'll see the model emit a **tool call** with structured
arguments, Inspect run the function, and the result returned to the model.

Why no sandbox? This tool is pure in-process Python. The moment a tool runs
**arbitrary** code (shell, file edits), it must run in an isolated sandbox —
that's example 04.
