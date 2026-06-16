#!/usr/bin/env python3
"""Analyse Inspect eval logs and write a comprehensive report as Markdown AND HTML.

It reads every `.eval` log under a directory, computes metrics and per-condition
breakdowns (grouping by `metadata.condition` / `metadata.truth` / `metadata.level`
when present), pulls a few sample transcripts, and then — if a model is reachable —
asks an LLM to interpret the results. Without a key/network (or with --no-llm) it
still writes a full statistics report.

It always writes two files: `<out>.md` and `<out>.html` (a self-contained styled
page, no extra dependencies).

Why an LLM via Inspect's model layer (not a raw API call)? It reuses the same
provider abstraction and `.env` keys the rest of the repo uses, so it works with
OpenAI / Anthropic / DeepSeek / etc. unchanged.

Usage:
    python scripts/analyze_logs.py                      # ./logs -> logs/ANALYSIS.{md,html}
    python scripts/analyze_logs.py logs --model openai/gpt-5.5
    python scripts/analyze_logs.py logs --no-llm        # stats only, no model call
    python scripts/analyze_logs.py logs --out report --max-transcripts 3
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import html as _html
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from inspect_ai.log import list_eval_logs, read_eval_log
except Exception as e:  # pragma: no cover
    sys.exit(f"inspect-ai not importable ({e}). Activate your venv / pip install inspect-ai.")


# ---------- defensive readers over the log structures ----------

def _text_of(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    for c in content:
        t = getattr(c, "text", None)
        if t is not None:
            parts.append(t)
        elif c.__class__.__name__.endswith("Image") or getattr(c, "type", "") in ("image", "image_url"):
            parts.append("[image]")
    return " ".join(parts)


def _input_text(sample) -> str:
    inp = getattr(sample, "input", "")
    if isinstance(inp, str):
        return inp
    return " | ".join(
        f"{getattr(m, 'role', '?')}: {_text_of(getattr(m, 'content', ''))}" for m in inp
    )


def _first_score(sample):
    for name, sc in (getattr(sample, "scores", None) or {}).items():
        return name, sc
    return None, None


def _truncate(s: str, n: int) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def collect(log_dir: str, max_transcripts: int):
    evals = []
    for info in list_eval_logs(log_dir):
        try:
            log = read_eval_log(info.name)
        except Exception as e:
            evals.append({"task": Path(info.name).name, "error": str(e)})
            continue

        metrics = {}
        if getattr(log, "results", None) is not None:
            for sc in log.results.scores:
                for mname, m in sc.metrics.items():
                    metrics[f"{getattr(sc, 'name', 'score')}/{mname}"] = getattr(m, "value", None)

        samples = list(getattr(log, "samples", []) or [])
        groups = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        for s in samples:
            md = getattr(s, "metadata", None) or {}
            _, sc = _first_score(s)
            correct = 1 if (sc is not None and str(getattr(sc, "value", "")) in ("C", "1", "1.0", "CORRECT")) else 0
            for key in ("condition", "truth", "level"):
                if key in md:
                    g = groups[key][str(md[key])]
                    g[0] += correct
                    g[1] += 1

        transcripts = []
        for s in samples[:max_transcripts]:
            _, sc = _first_score(s)
            md = getattr(s, "metadata", {}) or {}
            transcripts.append(
                {
                    "input": _truncate(_input_text(s), 300),
                    "output": _truncate(getattr(getattr(s, "output", None), "completion", "") or "", 400),
                    "score": str(getattr(sc, "value", "")) if sc else "",
                    "answer": str(getattr(sc, "answer", "")) if sc else "",
                    "explanation": _truncate(str(getattr(sc, "explanation", "")) if sc else "", 200),
                    "metadata": {k: md[k] for k in ("condition", "truth", "level", "pair") if k in md},
                }
            )

        evals.append(
            {
                "task": str(getattr(log.eval, "task", "?")),
                "model": str(getattr(log.eval, "model", "?")),
                "status": str(getattr(log, "status", "?")),
                "n_samples": len(samples),
                "metrics": metrics,
                "groups": {k: dict(v) for k, v in groups.items()},
                "transcripts": transcripts,
            }
        )
    return evals


def render_evidence(evals) -> str:
    lines = ["# Eval results — evidence\n", "## Overview\n",
             "| Task | Model | Status | N | Metrics |", "|---|---|---|---|---|"]
    for e in evals:
        if "error" in e:
            lines.append(f"| {e['task']} | – | read-error | – | {e['error']} |")
            continue
        mtxt = ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                         for k, v in e["metrics"].items()) or "—"
        lines.append(f"| {e['task']} | {e['model']} | {e['status']} | {e['n_samples']} | {mtxt} |")
    lines.append("")
    for e in evals:
        if "error" in e:
            continue
        lines.append(f"## {e['task']}  ·  {e['model']}\n")
        for key, vals in e["groups"].items():
            lines.append(f"**Accuracy by `{key}`:**\n")
            lines.append(f"| {key} | correct/total | accuracy |")
            lines.append("|---|---|---|")
            for v, (c, t) in vals.items():
                lines.append(f"| {v} | {c}/{t} | {(c / t if t else 0):.0%} |")
            lines.append("")
        if e["transcripts"]:
            lines.append("**Sample transcripts:**\n")
            for i, tr in enumerate(e["transcripts"], 1):
                meta = " ".join(f"{k}={v}" for k, v in tr["metadata"].items())
                lines.append(f"- *Sample {i}* {('[' + meta + ']') if meta else ''} — "
                             f"score=`{tr['score']}` answer=`{tr['answer']}`")
                lines.append(f"  - input: {tr['input']}")
                lines.append(f"  - output: {tr['output']}")
                if tr["explanation"]:
                    lines.append(f"  - explanation: {tr['explanation']}")
            lines.append("")
    return "\n".join(lines)


# ---------- LLM interpretation ----------

SYSTEM_PROMPT = (
    "You are a rigorous AI-evaluations analyst. You are given structured results "
    "from UK AISI Inspect evals: an overview table, per-condition accuracy "
    "breakdowns, and sample transcripts. Write a clear Markdown report with:\n"
    "1. Executive summary (3-5 bullets).\n"
    "2. Per-eval interpretation: what each eval measures, what the numbers mean, "
    "and — where relevant — the AI-safety signal (sandbagging = lower accuracy "
    "under an incentive; strategic deception = low honesty; scheming = a behaviour "
    "score where C means the behaviour occurred). Compare conditions explicitly.\n"
    "3. Caveats: tiny sample sizes, mock/scripted models (e.g. mockllm), benchmark "
    "saturation, anything limiting the conclusion.\n"
    "4. Recommended next steps.\n"
    "Be precise; do NOT overclaim. If N is small, say it is indicative only. Use "
    "tables where helpful."
)


async def llm_analysis(model_name: str, evidence: str) -> str:
    from inspect_ai.model import GenerateConfig, get_model

    model = get_model(model_name)
    prompt = SYSTEM_PROMPT + "\n\n---\nResults to analyse:\n\n" + evidence + "\n\n---\nWrite the report now."
    out = await model.generate(prompt, config=GenerateConfig(max_tokens=3000, temperature=0.2))
    return out.completion


# ---------- tiny, dependency-free Markdown -> HTML ----------

def _inline(text: str) -> str:
    t = _html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html_body(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    para: list[str] = []
    in_list = False
    i, n = 0, len(lines)

    def flush_para():
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            para.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < n:
        line = lines[i]
        if line.strip().startswith("```"):
            flush_para(); close_list(); i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(_html.escape(lines[i])); i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>"); continue
        if line.lstrip().startswith("|") and i + 1 < n and "-" in lines[i + 1] \
                and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            flush_para(); close_list()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in header)
            body = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"); continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para(); close_list()
            lvl = len(m.group(1)); out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if re.match(r"^\s*([-*_])\1\1+\s*$", line):
            flush_para(); close_list(); out.append("<hr>"); i += 1; continue
        if line.lstrip().startswith(">"):
            flush_para(); close_list()
            q = re.sub(r"^\s*>\s?", "", line)
            out.append(f"<blockquote>{_inline(q)}</blockquote>"); i += 1; continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_para()
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{_inline(m.group(1))}</li>"); i += 1; continue
        if not line.strip():
            flush_para(); close_list(); i += 1; continue
        para.append(line.strip()); i += 1
    flush_para(); close_list()
    return "\n".join(out)


HTML_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>
:root{{--ink:#11202e;--muted:#5f7286;--line:#c8d2de;--bg:#f4f6f8;--card:#fff;--accent:#0f9e8c;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,Arial,sans-serif;line-height:1.6}}
.wrap{{max-width:920px;margin:0 auto;padding:40px 24px 80px}}
h1,h2,h3,h4{{font-family:'Space Grotesk',Inter,sans-serif;line-height:1.2}}
h1{{font-size:30px;margin:0 0 8px}} h2{{font-size:22px;margin:34px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}}
h3{{font-size:17px;margin:22px 0 6px}}
code{{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:.88em;background:#eef2f6;padding:1px 5px;border-radius:4px;color:#0c7e70}}
pre{{background:#0e1820;color:#d6e0ea;border-radius:10px;padding:14px 16px;overflow-x:auto}}
pre code{{background:none;color:inherit;padding:0}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px;background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden}}
th,td{{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{background:#eef2f6;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}}
tr:last-child td{{border-bottom:none}}
blockquote{{margin:12px 0;padding:8px 14px;border-left:3px solid var(--accent);background:#eef7f5;color:var(--muted);border-radius:0 6px 6px 0}}
ul{{padding-left:22px}} li{{margin:3px 0}} a{{color:#4763d0}} hr{{border:none;border-top:1px solid var(--line);margin:26px 0}}
.foot{{margin-top:40px;color:var(--muted);font-size:12px;font-family:'JetBrains Mono',monospace}}
</style></head><body><div class="wrap">
{body}
<div class="foot">Generated by scripts/analyze_logs.py · Inspect eval analysis</div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Analyse Inspect eval logs into a Markdown + HTML report.")
    ap.add_argument("log_dir", nargs="?", default="logs")
    ap.add_argument("--model", default="openai/gpt-5.5",
                    help="analyst model for the interpretation (default: openai/gpt-5.5)")
    ap.add_argument("--no-llm", action="store_true", help="skip the LLM step (stats only)")
    ap.add_argument("--max-transcripts", type=int, default=2)
    ap.add_argument("--out", default=None, help="output path/base (default: <log_dir>/ANALYSIS)")
    args = ap.parse_args()

    if not Path(args.log_dir).exists():
        sys.exit(f"no log directory '{args.log_dir}' — run an example first.")
    evals = collect(args.log_dir, args.max_transcripts)
    if not evals:
        sys.exit(f"no .eval logs found under '{args.log_dir}'.")

    evidence = render_evidence(evals)
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [f"# Eval analysis\n\n_Generated {stamp} from `{args.log_dir}/` ({len(evals)} log(s))._\n"]

    if args.no_llm:
        parts.append("> LLM interpretation skipped (`--no-llm`). Statistics only.\n")
    else:
        try:
            interpretation = asyncio.run(llm_analysis(args.model, evidence))
            parts += [f"> Interpretation by `{args.model}`.\n", "## Analysis\n", interpretation, "\n---\n"]
        except Exception as e:
            parts.append(f"> LLM step unavailable ({e}). Statistics only — re-run with a "
                         f"reachable `--model` for the written analysis.\n")
    parts.append(evidence)
    report_md = "\n".join(parts)

    # resolve output paths (always produce .md and .html)
    base = args.out or str(Path(args.log_dir) / "ANALYSIS")
    base = base[:-3] if base.endswith(".md") else (base[:-5] if base.endswith(".html") else base)
    md_path, html_path = base + ".md", base + ".html"

    Path(md_path).write_text(report_md)
    html = HTML_TEMPLATE.format(title="Eval analysis", body=md_to_html_body(report_md))
    Path(html_path).write_text(html)
    print(f"wrote {md_path}")
    print(f"wrote {html_path}   ({len(evals)} logs)")


if __name__ == "__main__":
    main()
