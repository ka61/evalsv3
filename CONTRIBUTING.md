# Contributing — the paved path

Set up for **solo learning**: you can push straight to `main`. The guardrails
are light — CI runs on every push, force-pushes and branch deletion are blocked,
and pre-commit catches formatting/secret slips.

## Workflow (solo)

1. **Edit**, then **commit** with [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `chore:` …). Pre-commit hooks run `ruff` and
   `gitleaks`.
2. **Push to `main`** directly: `git push`. CI (`lint`) runs on the push.

## Workflow (collaborating — optional, stricter)

When others join, switch on the stricter block in `scripts/setup_github.sh`
(require CI + 1 review, no direct pushes) and use:

1. **Branch** off `main` (`git switch -c my-change`).
2. **Open a PR.** CI (`lint`) must pass and one review is required before merge.
3. **Squash merge.** Merged branches are deleted automatically.

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt ruff pre-commit
pre-commit install        # format/lint/secret-scan on every commit
cp .env.example .env      # then add your keys
```

## What CI checks

- `ruff format --check .` and `ruff check .`
- every `examples/**/task.py` imports cleanly

Evals are **not** run in CI by default (they cost money and some need Docker).
Trigger a small run manually from the **Actions → Run eval (manual)** workflow,
which uses the repo secrets.

## Secrets

API keys live only in your local `.env` (gitignored) and in GitHub Actions
**Secrets** (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`). Set them
with `./scripts/setup_github.sh`. Never commit a key.
