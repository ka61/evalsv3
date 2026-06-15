# 11 · A research agent (web search)

**Concepts:** the `react` agent with the `web_search` tool; model-graded answers.

```bash
inspect eval examples/11_web_search_agent/task.py --model openai/gpt-4o
```

> **Provider needed.** `web_search()` requires a search backend. Some providers
> (e.g. certain OpenAI/Anthropic models) offer **built-in** search; otherwise
> configure an external provider (e.g. Tavily/Google) per the Inspect
> [tools docs](https://inspect.aisi.org.uk/tools-standard.html#sec-web-search).
> Without one, swap to a non-search example.

In the transcript you'll see the agent issue search queries, read results, and
then call `submit()` with its answer.
