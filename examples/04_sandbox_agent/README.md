# 04 · A sandboxed agent

The jump from "trusted text" to "untrusted execution." **Concepts:** the
`react` agent, the `bash` tool, the **Docker sandbox**, `Sample.files`, and the
`includes` scorer.

**Requires Docker running.** Check with `docker run --rm hello-world`.

```bash
inspect eval examples/04_sandbox_agent/task.py --model openai/gpt-4o-mini
docker ps          # see the disposable sandbox while it runs
inspect view
```

How it works:

- `sandbox="docker"` + the `compose.yaml` here create a fresh, network-isolated
  container per sample (using the official `aisiuk/inspect-tool-support` image)
- `Sample.files` mounts `flag.txt` into the container
- the `react` agent loops, calling `bash` until it calls the built-in `submit()`
  tool with the flag
- the container is destroyed when the sample finishes

Debugging tip: run with `--no-sandbox-cleanup`, then
`docker exec -it <name> bash -l` to poke around, and
`inspect sandbox cleanup docker` when done.
