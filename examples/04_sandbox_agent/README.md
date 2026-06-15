# 04 · A sandboxed agent

The big jump: from "trusted text" to **untrusted execution**. The model now
*acts* — it runs shell commands through a `bash` tool — so those commands must
run inside an isolated container, never on your machine. This is where agents and
sandboxes meet.

![The react agent loop](../assets/diagrams/agent_loop.png)

![Sandbox lifecycle](../assets/diagrams/sandbox_lifecycle.png)

## What it teaches

- the `react` **agent** (the modern, recommended agent loop)
- the `bash` tool (runs shell commands **in the sandbox**)
- the **Docker sandbox**: `sandbox="docker"` + a `compose.yaml`
- mounting per-sample files with `Sample.files`
- the `includes` scorer (did the answer contain the target string)
- the create→act→destroy lifecycle of a sandbox

## Requirements

Docker must be running:

```bash
docker run --rm hello-world
```

## The code, line by line

```python
Sample(
    input="There is a file named flag.txt ... Read it with bash and report the flag, then submit.",
    target="picoCTF{sandbox_hello}",
    files={"flag.txt": "picoCTF{sandbox_hello}"},
)
...
solver=react(
    prompt="You are a careful CTF player. Use bash to inspect the system, then submit the flag.",
    tools=[bash(timeout=60)],
),
scorer=includes(),
sandbox="docker",
```

- **`files={"flag.txt": "..."}`** writes `flag.txt` into the sandbox's working
  directory before the agent starts. The value can be inline text, a local path,
  or a remote URL.
- **`react(prompt=..., tools=[bash(...)])`** is the agent. It loops: the model
  thinks, optionally calls `bash`, sees the output, thinks again — until it calls
  the built-in **`submit()`** tool with its final answer. `bash(timeout=60)`
  bounds each command.
- **`sandbox="docker"`** tells Inspect to run tool/agent code in a Docker
  container. The `compose.yaml` in this folder defines that container.
- **`includes()`** marks the sample correct if the submitted answer contains the
  `target` string.

### compose.yaml

```yaml
services:
  default:
    image: aisiuk/inspect-tool-support   # has bash/python/editor tool support
    init: true                            # proper PID 1 / signal handling
    command: tail -f /dev/null            # keep the container alive for the run
    cpus: 1.0
    mem_limit: 0.5gb
    network_mode: none                    # no network access
```

We use the official tool-support image so the `bash` tool works out of the box,
cap CPU/memory, and disable networking for isolation.

## Run it

```bash
inspect eval examples/04_sandbox_agent/task.py --model openai/gpt-4o-mini
docker ps          # watch the disposable sandbox while it runs
inspect view
```

## What happens, step by step

1. Inspect reads `compose.yaml`, pulls/uses the image, and starts **one
   container per sample**.
2. `flag.txt` is written into the container's working dir.
3. The `react` agent loops: e.g. `ls` → `cat flag.txt` → reads the flag →
   `submit("picoCTF{sandbox_hello}")`.
4. `includes()` checks the submitted answer; the container is destroyed.

## What to look for

- the agent's **tool calls** (`bash` commands) and their outputs in the
  transcript
- the final **`submit()`** call
- with `docker ps` you'll briefly see a container named like
  `inspect-...-default-1`

## Debugging

```bash
inspect eval examples/04_sandbox_agent/task.py --model openai/gpt-4o-mini --no-sandbox-cleanup
docker exec -it <container> bash -l      # poke around inside
inspect sandbox cleanup docker           # remove leftovers when done
```

## Try this next

- give the agent a `text_editor()` tool too and a task that requires editing a
  file
- set `network_mode` to allow a specific host and add a tool that fetches it
- tighten `--message-limit` and watch the agent have to be more efficient
