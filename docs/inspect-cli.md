# Inspect CLI — a detailed reference

A practical, example-driven guide to the `inspect` command line: every flag that
matters, what it means, and how to use it. Grouped into tables so you can scan.

> **Get help anytime:** `inspect --help` lists the commands; `inspect eval --help`
> lists every option with its exact, version-correct description. This file is a
> curated companion, not a replacement — flags evolve between releases.

- [Commands at a glance](#commands-at-a-glance)
- [`inspect eval` — options by group](#inspect-eval--options-by-group)
  - [Model provider](#model-provider) · [Generation](#model-generation) ·
    [Tasks & solvers](#tasks--solvers) · [Sample selection](#sample-selection) ·
    [Parallelism](#parallelism) · [Errors & limits](#errors--limits) ·
    [Eval logs](#eval-logs) · [Scoring](#scoring) · [Sandboxes](#sandboxes) ·
    [Display & misc](#display--misc)
- [Configuring with `.env` and environment variables](#configuring-with-env-and-environment-variables)
- [Other commands](#other-commands)
- [Worked recipes](#worked-recipes)

---

## Commands at a glance

| Command | What it does | Example |
|---|---|---|
| `inspect eval` | Run one or more tasks | `inspect eval task.py --model openai/gpt-4o` |
| `inspect eval-set` | Run a **set** of tasks together, retrying failures | `inspect eval-set tasks/ --model openai/gpt-4o --log-dir logs/suite` |
| `inspect eval-retry` | Re-run the failed samples of a previous log | `inspect eval-retry logs/2026-…​.eval` |
| `inspect view` | Open the interactive log viewer in a browser | `inspect view --log-dir logs` |
| `inspect score` | Score (or re-score) an existing log | `inspect score logs/…​.eval --scorer model_graded_qa` |
| `inspect log` | Inspect/convert log files (`list`, `dump`, `convert`, `schema`) | `inspect log dump logs/…​.eval` |
| `inspect trace` | Diagnose stuck/slow subprocess & sandbox calls | `inspect trace anomalies` |
| `inspect sandbox` | Manage sandboxes (e.g. cleanup) | `inspect sandbox cleanup docker` |
| `inspect list tasks` | List the tasks discovered in a directory | `inspect list tasks` |
| `inspect cache` | Manage the model-output cache | `inspect cache clear` |
| `inspect info` | Print version / environment info | `inspect info` |

Run `inspect <command> --help` for the authoritative, current options of any
command.

---

## `inspect eval` — options by group

`inspect eval [FILES…] [OPTIONS]`. `FILES` are task files/dirs (and you can target
a single task with `file.py@task_name`). Every option below is also accepted by
the Python `eval()` function and most are settable via environment variable
(see [the env section](#configuring-with-env-and-environment-variables)).

### Model provider

| Flag | Meaning | Example |
|---|---|---|
| `--model` | The model under test, as `provider/name`. `--model none` runs tasks that don't need a model. | `--model anthropic/claude-sonnet-4-0` |
| `--model-base-url` | Override the provider's API base URL (self-hosted / proxy). | `--model-base-url http://localhost:8000/v1` |
| `--model-config` | A JSON/YAML file of model-client args. | `--model-config model.yaml` |
| `-M` | A single model-client arg as `key=value` (repeatable). | `-M location=us-east5` |
| `--model-role` | Bind a **named role** to a model (repeatable). Graders use the `grader` role. | `--model-role grader=openai/gpt-4o` |

### Model generation

Controls how tokens are generated. Many are **provider-specific** — Inspect ignores
ones a provider doesn't support.

| Flag | Meaning | Example |
|---|---|---|
| `--generate-config` | JSON/YAML file with all generation options at once. | `--generate-config gen.yaml` |
| `--max-tokens` | Max tokens in the completion. | `--max-tokens 2048` |
| `--system-message` | Override the task's system message. | `--system-message "Answer briefly."` |
| `--temperature` | Sampling temperature (0–2); lower = more deterministic. | `--temperature 0.0` |
| `--top-p` | Nucleus sampling cutoff (alternative to temperature). | `--top-p 0.9` |
| `--top-k` | Sample from the top-k tokens (Anthropic, Google, HF, vLLM). | `--top-k 40` |
| `--frequency-penalty` | Penalise repeated tokens (-2…2). (OpenAI, Google, Grok, Groq, llama-cpp, vLLM) | `--frequency-penalty 0.5` |
| `--presence-penalty` | Encourage new topics (-2…2). (same providers as above) | `--presence-penalty 0.3` |
| `--logit-bias` | Bias specific token ids (-100…100). (OpenAI, Grok) | `--logit-bias "42=10,43=-10"` |
| `--seed` | Random seed for reproducibility. (OpenAI, Google, Groq, Mistral, HF, vLLM) | `--seed 123` |
| `--stop-seqs` | Stop generation at these sequences. | `--stop-seqs "###,END"` |
| `--num-choices` | Generate N choices per input. (OpenAI, Grok, Google, Together, vLLM) | `--num-choices 4` |
| `--best-of` | Server-side sample N, return the best. (OpenAI) | `--best-of 5` |
| `--log-probs` / `--top-logprobs` | Return token log-probabilities / the top-N per position. | `--log-probs --top-logprobs 5` |
| `--cache-prompt` | Cache the prompt prefix: `auto`/`true`/`false`. (Anthropic) | `--cache-prompt true` |
| `--reasoning-effort` | Reasoning budget on reasoning models: `low`/`medium`/`high` (and more). | `--reasoning-effort high` |
| `--reasoning-tokens` | Max tokens for reasoning. (Anthropic) | `--reasoning-tokens 4000` |
| `--reasoning-history` | How much prior reasoning to resend: `none`/`all`/`last`/`auto`. | `--reasoning-history auto` |
| `--response-format` | Constrain output to a JSON schema. (OpenAI, Google, Mistral) | `--response-format schema.json` |
| `--parallel-tool-calls` | Allow multiple tool calls per turn (default on). (OpenAI, Groq) | `--parallel-tool-calls false` |
| `--max-tool-output` | Max bytes of a tool result (default 16 KiB). | `--max-tool-output 65536` |
| `--internal-tools` | Map tools to a model's built-in versions (e.g. Anthropic `computer`). | `--internal-tools false` |
| `--max-retries` | Max retries per generate request (default: unlimited). | `--max-retries 5` |
| `--timeout` | Overall generate timeout (s). | `--timeout 120` |
| `--attempt-timeout` | Timeout per attempt before retrying. | `--attempt-timeout 60` |

### Tasks & solvers

| Flag | Meaning | Example |
|---|---|---|
| `-T` | Pass an argument to the `@task` function (repeatable). | `-T epochs=5 -T subset=hard` |
| `--task-config` | A JSON/YAML file of task args. | `--task-config task.yaml` |
| `--solver` | Override the task's default solver. | `--solver chain_of_thought.py` |
| `-S` | Pass an argument to the solver (repeatable). | `-S max_attempts=3` |
| `--solver-config` | A JSON/YAML file of solver args. | `--solver-config solver.yaml` |

### Sample selection

| Flag | Meaning | Example |
|---|---|---|
| `--limit` | Run a maximum number, or a **range**, of samples. | `--limit 20` · `--limit 10-20` |
| `--sample-id` | Run only specific sample id(s). | `--sample-id 44,63,91` |
| `--epochs` | Repeat each sample N times (default 1). | `--epochs 5` |
| `--epochs-reducer` | Combine epochs: `mean`, `median`, `mode`, `max`, `at_least_{n}`, `pass_at_{k}`. | `--epochs-reducer pass_at_1` |
| `--no-epochs-reducer` | Don't reduce — aggregate all samples × epochs together. | `--no-epochs-reducer` |

### Parallelism

| Flag | Meaning | Example |
|---|---|---|
| `--max-connections` | Max concurrent model API calls (default 10). The main rate-limit lever. | `--max-connections 30` |
| `--max-samples` | Max samples in flight per task (default = `--max-connections`). | `--max-samples 40` |
| `--max-subprocesses` | Max concurrent subprocess calls (default = CPU count). | `--max-subprocesses 8` |
| `--max-sandboxes` | Max concurrent containers (default = 2 × CPU count). | `--max-sandboxes 16` |
| `--max-tasks` | Max tasks run in parallel (default 1). | `--max-tasks 4` |
| `--max-dataset-memory` | Page samples to disk above this MB (huge datasets). | `--max-dataset-memory 512` |

### Errors & limits

Per-sample **limits** stop runaway agents and surprise bills; **error** flags
decide whether a bad sample sinks the whole run.

| Flag | Meaning | Example |
|---|---|---|
| `--fail-on-error` | Tolerance for sample errors: a fraction (0–1) or a count (>1). Default: any error fails the eval. | `--fail-on-error 0.1` |
| `--no-fail-on-error` | Keep running other samples even if some error. | `--no-fail-on-error` |
| `--retry-on-error` | Retry erroring samples (once, or `=N` times). | `--retry-on-error=2` |
| `--score-on-error` | Score errored samples instead of failing mid-run. | `--score-on-error` |
| `--message-limit` | Max messages per sample (caps agent loops). | `--message-limit 30` |
| `--token-limit` | Max tokens per sample. | `--token-limit 100000` |
| `--time-limit` | Max wall-clock seconds per sample. | `--time-limit 300` |
| `--working-limit` | Max **active** (model+tool) seconds per sample, excluding waits. | `--working-limit 120` |
| `--cost-limit` | Max dollars per sample (needs model cost data). | `--cost-limit 0.05` |
| `--model-cost-config` | JSON/YAML of model prices for `--cost-limit`. | `--model-cost-config costs.yaml` |

### Eval logs

| Flag | Meaning | Example |
|---|---|---|
| `--log-dir` | Where logs go (local path or `s3://…`). Default `./logs`. | `--log-dir s3://my-evals/run1` |
| `--log-format` | `eval` (default, compact) or `json`. | `--log-format json` |
| `--log-level` | Console log level: `debug`/`trace`/`http`/`info`/`warning`/`error`/`critical`. | `--log-level info` |
| `--log-level-transcript` | Log level captured **in the eval transcript**. | `--log-level-transcript debug` |
| `--no-log-samples` | Don't store per-sample detail (smaller logs). | `--no-log-samples` |
| `--no-log-images` | Don't store images/media in the log. | `--no-log-images` |
| `--no-log-realtime` | Don't stream events live (affects live viewing). | `--no-log-realtime` |
| `--log-buffer` | Samples buffered before a write (durability vs. speed). | `--log-buffer 10` |
| `--log-shared` | Sync events to the log dir so others see live updates. | `--log-shared 10` |

### Scoring

| Flag | Meaning | Example |
|---|---|---|
| `--no-score` | Run without scoring; score later with `inspect score`. | `--no-score` |
| `--no-score-display` | Hide realtime scoring output. | `--no-score-display` |

### Sandboxes

| Flag | Meaning | Example |
|---|---|---|
| `--sandbox` | Set/override the sandbox: `<type>` or `<type>:<config>`. | `--sandbox docker:compose.yml` |
| `--no-sandbox-cleanup` | Keep containers after the run (for debugging). | `--no-sandbox-cleanup` |

### Display & misc

| Flag | Meaning | Example |
|---|---|---|
| `--display` | UI mode: `full`/`conversation`/`rich`/`plain`/`log`/`none`. Use `none` in CI. | `--display none` |
| `--no-ansi` | No ANSI colour codes (clean CI logs). | `--no-ansi` |
| `--approval` | Tool-call approval policy file (human-in-the-loop). | `--approval approval.yaml` |
| `--env` | Set an environment variable for the run (repeatable). | `--env HF_TOKEN=hf_…` |
| `--tags` | Tag the run (shows in the log). | `--tags smoke,nightly` |
| `--metadata` | Attach metadata `key=value` to the run. | `--metadata project=evalsv3` |
| `--debug` / `--debug-errors` | Wait for a debugger / raise task errors instead of logging them. | `--debug-errors` |
| `--help` | Show the full, current option list for the command. | `inspect eval --help` |

---

## Configuring with `.env` and environment variables

Inspect auto-loads a `.env` from the working directory (searching parents), so put
API keys and common defaults there instead of repeating flags.

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

INSPECT_EVAL_MODEL=openai/gpt-4o-mini     # default --model
INSPECT_LOG_DIR=./logs                    # default --log-dir
INSPECT_LOG_LEVEL=warning
INSPECT_EVAL_MAX_CONNECTIONS=20
INSPECT_EVAL_MAX_RETRIES=5
```

Most flags have an env equivalent — usually the flag name upper-cased with an
`INSPECT_EVAL_` prefix:

| CLI flag | `eval()` arg | Environment variable |
|---|---|---|
| `--model` | `model` | `INSPECT_EVAL_MODEL` |
| `--limit` | `limit` | `INSPECT_EVAL_LIMIT` |
| `--max-connections` | `max_connections` | `INSPECT_EVAL_MAX_CONNECTIONS` |
| `--log-dir` | `log_dir` | `INSPECT_LOG_DIR` |
| `--log-level` | `log_level` | `INSPECT_LOG_LEVEL` |
| `--log-format` | `log_format` | `INSPECT_LOG_FORMAT` |

**Tip — one key, any model:** set `OPENROUTER_API_KEY` and use model ids like `openrouter/openai/gpt-4o` or `openrouter/anthropic/claude-3.5-sonnet`; switch models by changing just `--model` / `INSPECT_EVAL_MODEL`.

Explicit flags always override `.env` / env values. Provider keys
(`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `DEEPSEEK_API_KEY`, …)
are read from the environment too. **Never commit `.env`.**

---

## Other commands

### `inspect eval-set` — run a suite with retries

```bash
inspect eval-set examples/01_hello/task.py examples/02_multiple_choice/task.py \
  --model openai/gpt-4o-mini --log-dir logs/suite
```

Accepts all `inspect eval` options, plus it groups logs under one `--log-dir` and
automatically retries failed tasks (tune with `--retry-attempts` and
`--retry-wait`). Re-running the same command resumes where it left off.

### `inspect view` — the log viewer

| Flag | Meaning | Example |
|---|---|---|
| `--log-dir` | Which logs to browse (local or `s3://`). | `inspect view --log-dir logs` |
| `--port` / `--host` | Serve on a specific port/host. | `inspect view --port 7575` |

### `inspect score` — score a log after the fact

```bash
inspect score logs/2026-…​.eval --scorer model_graded_qa   # apply/replace a scorer
```

Useful with `inspect eval --no-score` (generate now, grade later / try different
scorers without re-running the model).

### `inspect log` — work with log files

| Subcommand | Meaning | Example |
|---|---|---|
| `inspect log list` | List logs in a dir (optionally as JSON). | `inspect log list --json` |
| `inspect log dump` | Print a log's header as JSON (no samples). | `inspect log dump logs/…​.eval` |
| `inspect log convert` | Convert between `eval` and `json` formats. | `inspect log convert --to json logs/` |
| `inspect log schema` | Print the JSON schema of the log format. | `inspect log schema` |

### `inspect trace` — diagnose stuck runs

| Subcommand | Meaning |
|---|---|
| `inspect trace list` | List recent trace files. |
| `inspect trace anomalies` | Find subprocess/sandbox calls that hung, timed out, or errored. |
| `inspect trace dump` | Dump a trace file as JSON. |

### `inspect sandbox` — manage sandboxes

```bash
inspect sandbox cleanup docker                       # remove all leftover containers
inspect sandbox cleanup docker inspect-…-default-1   # remove one
```

### Other helpers

| Command | Meaning |
|---|---|
| `inspect list tasks` | List the `@task`s discovered under the current directory. |
| `inspect cache clear` | Clear the model-output cache. |
| `inspect info` | Print Inspect version and environment details. |

---

## Worked recipes

```bash
# fast smoke test — 5 samples, deterministic, cheap model
inspect eval task.py --model openai/gpt-4o-mini --limit 5 --temperature 0

# reliable measurement — repeat 5×, take pass@1, cap concurrency to dodge rate limits
inspect eval task.py --model openai/gpt-4o --epochs 5 --epochs-reducer pass_at_1 \
  --max-connections 20

# vary the grader without touching code (model roles)
inspect eval task.py --model openai/gpt-4o-mini --model-role grader=openai/gpt-4o

# pass arguments into the @task function
inspect eval task.py -T subset=hard -T shots=5

# bound a long agentic run (limits + sandbox concurrency)
inspect eval agent_task.py --model openai/gpt-4o \
  --message-limit 30 --token-limit 100000 --time-limit 300 --max-sandboxes 8

# persist logs to S3 and view them from anywhere
inspect eval task.py --model openai/gpt-4o --log-dir s3://my-evals/run-2026-06
inspect view --log-dir s3://my-evals/run-2026-06

# generate now, grade later (cheap experiments with scorers)
inspect eval task.py --model openai/gpt-4o --no-score
inspect score logs/2026-…​.eval --scorer model_graded_qa

# CI-friendly: no colours, no live UI, tolerate a few sample errors
inspect eval task.py --model openai/gpt-4o-mini \
  --display none --no-ansi --fail-on-error 0.1

# run a whole suite with automatic retries
inspect eval-set examples/ --model openai/gpt-4o-mini --log-dir logs/suite
```

In this repo, the [`scripts/`](../scripts/) helpers wrap these for you:
`scripts/run_example.sh`, `scripts/run_all.sh`, and `scripts/view_results.sh`.

---

*Flags and defaults change between Inspect releases — when in doubt, trust
`inspect eval --help` and the [official docs](https://inspect.aisi.org.uk/options.html).*
