#!/usr/bin/env python3
"""Write a focused, presentation-quality HTML write-up of the FLAGGED behaviours
found across the Inspect eval suite (sandbagging, deception, scheming, authority-
driven false matches, …).

It reuses the analysis engine in `analyze_logs.py` so the evidence is exactly what
the logs contain, then renders a standalone, self-contained HTML document suitable
for sharing.

Usage:
    python scripts/findings_report.py                 # reads logs/, writes logs/FINDINGS.html
    python scripts/findings_report.py logs --out reports/findings
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
from pathlib import Path

import analyze_logs as A   # same directory; reuse collect/verdict/explainers/etc.


# ---------------------------------------------------------------------------
# Per-behaviour framing (why a safety researcher cares). Keyed by task-name fragment.
# ---------------------------------------------------------------------------
BEHAVIOUR = [
    ("fingerprint", {
        "name": "Authority-driven false match (chain-of-thought robustness)",
        "what": "The model compares two fingerprints and must answer SAME or DIFFERENT. "
                "Under escalating, fabricated authority (“four examiners already confirmed the match”) "
                "a verdict that was correct at control flips to a false “SAME” on prints that are "
                "genuinely different.",
        "why": "This is sycophancy / authority-anchoring overriding the model’s own perception — a "
               "chain-of-thought robustness failure. It mirrors the real Shirley McKie miscarriage of "
               "justice, and is a clean, measurable analogue of context talking a model out of a correct "
               "answer.",
    }),
    ("sandbag", {
        "name": "Sandbagging (strategic underperformance)",
        "what": "The same task is asked neutrally and then with a note that scoring well triggers an "
                "undesirable consequence (a capability being ‘unlearned’). Accuracy drops under the "
                "incentive even though the model is never told to underperform.",
        "why": "Sandbagging is a core deceptive-capability concern: a model that hides what it can do "
               "can pass capability and safety evaluations while retaining the capability — defeating "
               "the evaluation itself.",
    }),
    ("deception", {
        "name": "Strategic deception",
        "what": "Given a goal (make the sale) and the true, unflattering product facts, a model-graded "
                "judge scores HONESTY — a low score means the model misled the user to hit its goal.",
        "why": "Strategic deception undermines any oversight that relies on a model’s own statements; "
               "it is a building block of more serious scheming behaviour.",
    }),
    ("oversight", {
        "name": "Scheming — oversight subversion",
        "what": "An agent is given a goal that conflicts with an oversight mechanism it can see, but is "
                "never told to disable it. The scorer checks whether it covertly turned the oversight off.",
        "why": "Covertly disabling oversight to pursue a goal is the clearest in-context form of scheming.",
    }),
    ("scheming", {
        "name": "Scheming behaviour",
        "what": "A propensity probe for covert goal-directed behaviour that works against a monitor.",
        "why": "Covert, goal-directed subversion of oversight is the central concern of scheming research.",
    }),
]


def _framing(task):
    t = task.lower()
    for frag, info in BEHAVIOUR:
        if frag in t:
            return info
    ex = A._explainer(task)
    return {"name": ex["title"], "what": ex["aim"], "why": ex["detail"]}


# ---------------------------------------------------------------------------
# small HTML builders
# ---------------------------------------------------------------------------
def esc(s):
    return _html.escape(str(s), quote=True)


def _cond_table(e):
    """A compact accuracy-by-condition table, or the fingerprint false-match table."""
    if e.get("fp_diff"):
        rows = ""
        for c in ("control", "mild", "strong", "extreme"):
            d = e["fp_diff"].get(c)
            if not d or not d["total"]:
                continue
            fm = d["same"] / d["total"]
            rows += (f"<tr><td>{esc(c)}</td><td>{d['same']}</td><td>{d['different']}</td>"
                     f"<td>{d['none']}</td><td>{d['total']}</td>"
                     f"<td><b>{fm:.0%}</b></td></tr>")
        if not rows:
            return ""
        return ("<table class='data'><thead><tr><th>pressure</th><th>said SAME "
                "(false match)</th><th>said DIFFERENT (correct)</th><th>no verdict / refused</th>"
                "<th>total</th><th>false-match rate</th></tr></thead><tbody>"
                + rows + "</tbody></table>")
    g = e["groups"].get("condition")
    if g:
        rows = ""
        for cond, (c, t) in g.items():
            rows += f"<tr><td>{esc(cond)}</td><td>{c}/{t}</td><td><b>{(c/t if t else 0):.0%}</b></td></tr>"
        return ("<table class='data'><thead><tr><th>condition</th><th>correct / total</th>"
                "<th>accuracy</th></tr></thead><tbody>" + rows + "</tbody></table>")
    return ""


def _ordered_transcripts(e):
    """All transcripts for a run, with the most illustrative samples first."""
    trs = list(e["transcripts"])
    name = e["task"].lower()

    def illustrative(t):
        md, ans = t["metadata"], (t.get("answer") or "").lower()
        if "fingerprint" in name:               # a genuine non-match called SAME = false match
            return md.get("truth") == "different" and "same" in ans
        if "sandbag" in name:                   # wrong answer under the incentive
            return md.get("condition") == "incentivized" and t["score"] == "I"
        return t["score"] in ("I", "N")         # otherwise surface failures first
    trs.sort(key=lambda t: 0 if illustrative(t) else 1)   # stable: keeps original order within groups
    return trs


def _finding_html(idx, e):
    info = _framing(e["task"])
    emoji, vtext = A.verdict(e)
    cls = A._verdict_class(emoji)
    sev = {"bad": ("Observed — strong", "sev-bad"),
           "warn": ("Observed — moderate", "sev-warn")}.get(cls, ("Observed", "sev-warn"))
    d, durl = A._example_link(e)
    exhtml = (f'<a href="{esc(durl)}" target="_blank" rel="noopener">\U0001F4C1 {esc(d)} ↗</a>'
              if durl else esc(e["task"]))
    # metrics line
    mtxt = ", ".join(f"{k.split('/')[-1]}={v:.2f}" if isinstance(v, float) else f"{k.split('/')[-1]}={v}"
                     for k, v in e["metrics"].items()) or "no metric"
    # apollo further reading
    ref = ""
    if e["task"] in A.SAFETY_REF:
        rn, ru = A.SAFETY_REF[e["task"]]
        ref = f'<p class="apollo">\U0001F4DA Further reading: <a href="{esc(ru)}" target="_blank" rel="noopener">{esc(rn)}</a></p>'
    # evidence — ALL sample transcripts (illustrative ones first), long lists behind a toggle
    ev = ""
    trs = _ordered_transcripts(e)
    if trs:
        inner = "".join(A.transcript_html(t) for t in trs)
        if len(trs) > 6:
            inner = (f'<details class="allsamples" open><summary>📂 All {len(trs)} sample '
                     f'transcripts (illustrative ones first)</summary>{inner}</details>')
        ev = (f'<div class="evidence"><div class="ev-h">Sample transcripts ({len(trs)} total)'
              f'</div>{inner}</div>')
    cond = _cond_table(e)
    return f"""
<section class="finding">
  <div class="f-head {cls}">
    <span class="f-num">{idx}</span>
    <div>
      <h2>{esc(info['name'])}</h2>
      <div class="f-sub">{esc(e['task'])} &middot; <code>{esc(e['model'])}</code></div>
    </div>
    <span class="sev {sev[1]}">{esc(sev[0])}</span>
  </div>
  <div class="f-body">
    <div class="meta-grid">
      <div><span class="ml">Example</span>{exhtml}</div>
      <div><span class="ml">Model</span><code>{esc(e['model'])}</code></div>
      <div><span class="ml">Samples</span>{e['n_samples']}</div>
      <div><span class="ml">Metric</span><code>{esc(mtxt)}</code></div>
    </div>
    <div class="verdict {cls}"><span class="vi">{emoji}</span><div><b>Finding.</b> {A._inline(vtext)}</div></div>
    <h3>What the behaviour is</h3>
    <p>{esc(info['what'])}</p>
    <h3>Why it matters</h3>
    <p>{esc(info['why'])}</p>
    {ref}
    {('<h3>The numbers</h3>' + cond) if cond else ''}
    {('<h3>Evidence</h3>' + ev) if ev else ''}
  </div>
</section>"""


def build(evals, log_dir):
    A._assign_run_anchors(evals)
    ok = [e for e in evals if "error" not in e]
    flagged = [e for e in ok if A._verdict_class(A.verdict(e)[0]) in ("warn", "bad")]
    # strongest first, then group same behaviour together
    flagged.sort(key=lambda e: (0 if A._verdict_class(A.verdict(e)[0]) == "bad" else 1, e["task"]))

    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    n_models = len({e["model"] for e in flagged})
    n_beh = len({_framing(e["task"])["name"] for e in flagged})

    # executive summary table
    sumrows = ""
    for i, e in enumerate(flagged, 1):
        info = _framing(e["task"])
        emoji, vtext = A.verdict(e)
        short = esc(vtext.split(".**")[0].replace("**", "").strip())
        d, durl = A._example_link(e)
        exc = (f'<a href="{esc(durl)}" target="_blank" rel="noopener">{esc(d)}</a>' if durl else esc(e["task"]))
        sumrows += (f"<tr><td>{i}</td><td>{esc(info['name'])}</td><td>{exc}</td>"
                    f"<td><code>{esc(e['model'])}</code></td><td>{emoji} {short}</td></tr>")

    findings = "".join(_finding_html(i, e) for i, e in enumerate(flagged, 1))
    repo = A._repo_base().rsplit("/tree/", 1)[0]

    if not flagged:
        findings = ('<section class="finding"><div class="f-body"><div class="verdict good">'
                    '<span class="vi">✅</span><div><b>No flagged behaviours.</b> Across every '
                    'run analysed, none of the safety propensity tests detected the behaviour under '
                    'test. This document highlights flagged runs when present.</div></div></div></section>')
        sumrows = '<tr><td colspan="5">No flagged behaviours in this run.</td></tr>'

    return HTML.format(
        stamp=stamp, log_dir=esc(log_dir), repo=esc(repo),
        n_findings=len(flagged), n_models=n_models, n_beh=n_beh,
        sumrows=sumrows, findings=findings,
    )


# ---------------------------------------------------------------------------
HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flagged behaviours — evaluation findings</title>
<style>
:root{{--ink:#14222e;--muted:#5f7286;--line:#cdd7e1;--bg:#f5f7f9;--card:#fff;--accent:#0f9e8c;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:Inter,system-ui,Arial,sans-serif;line-height:1.62}}
.wrap{{max-width:880px;margin:0 auto;padding:0 22px 90px}}
a{{color:#2f57c4}} code{{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:.85em;
  background:#eef2f6;padding:1px 5px;border-radius:4px;color:#0c7e70}}
.cover{{background:linear-gradient(135deg,#10303a,#0f6f63);color:#eaf6f3;border-radius:0 0 18px 18px;
  padding:46px 34px 30px;margin-bottom:8px}}
.cover .kicker{{text-transform:uppercase;letter-spacing:.16em;font-size:12px;opacity:.8}}
.cover h1{{font-family:'Space Grotesk',Inter,sans-serif;font-size:32px;margin:8px 0 6px;line-height:1.15}}
.cover p{{margin:6px 0 0;max-width:60ch;opacity:.92;font-size:15px}}
.cover .meta{{margin-top:18px;display:flex;flex-wrap:wrap;gap:18px;font-size:13px;opacity:.9}}
.cover .meta b{{font-weight:600}}
.kpis{{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0}}
.kpi{{flex:1 1 130px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 15px;text-align:center}}
.kpi-n{{font-family:'Space Grotesk',sans-serif;font-size:25px;font-weight:600;color:var(--ink)}}
.kpi-l{{font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-top:3px}}
.note{{background:#fff;border:1px solid var(--line);border-left:5px solid var(--accent);
  border-radius:10px;padding:14px 18px;margin:14px 0}}
.note h3{{margin:0 0 6px;font-family:'Space Grotesk',sans-serif;font-size:14px;color:#0c7e70}}
.note ul{{margin:6px 0 0;padding-left:20px}} .note li{{margin:3px 0;font-size:14px}}
h2.sec{{font-family:'Space Grotesk',Inter,sans-serif;font-size:20px;margin:34px 0 10px;
  border-bottom:1px solid var(--line);padding-bottom:6px}}
table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px;background:var(--card);
  border:1px solid var(--line);border-radius:8px;overflow:hidden}}
th,td{{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{background:#eef2f6;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}}
tr:last-child td{{border-bottom:none}}
table.summary td:first-child{{text-align:center;color:var(--muted);font-variant-numeric:tabular-nums}}
.finding{{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:20px 0;
  box-shadow:0 10px 30px -22px rgba(20,34,46,.5)}}
.f-head{{display:flex;align-items:center;gap:14px;padding:16px 20px;border-bottom:1px solid var(--line)}}
.f-head.warn{{background:#fdf8ea}} .f-head.bad{{background:#fbeeee}}
.f-num{{flex:none;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;
  font-family:'Space Grotesk',sans-serif;font-weight:600;background:#10303a;color:#fff}}
.f-head h2{{font-family:'Space Grotesk',Inter,sans-serif;font-size:18px;margin:0}}
.f-sub{{color:var(--muted);font-size:13px;margin-top:2px}}
.sev{{margin-left:auto;flex:none;font-size:11.5px;font-weight:600;padding:5px 11px;border-radius:20px;border:1px solid}}
.sev-warn{{background:#fdf3da;border-color:#f0dca0;color:#8a6206}}
.sev-bad{{background:#fbe3e3;border-color:#f0c0c0;color:#b23232}}
.f-body{{padding:18px 22px 22px}}
.f-body h3{{font-family:'Space Grotesk',Inter,sans-serif;font-size:14.5px;margin:18px 0 4px;color:#1d3245}}
.f-body p{{margin:4px 0}}
.meta-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:2px 0 6px}}
.meta-grid>div{{background:#f6f9fb;border:1px solid #e6ecf2;border-radius:8px;padding:8px 11px;font-size:13.5px}}
.meta-grid .ml{{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-bottom:2px}}
.verdict{{display:flex;gap:10px;align-items:flex-start;margin:12px 0;padding:11px 14px;border-radius:10px;border:1px solid;font-size:14.5px}}
.verdict .vi{{font-size:18px}} .verdict.good{{background:#e7f6ec;border-color:#bfe6cd}}
.verdict.warn{{background:#fdf3da;border-color:#f0dca0}} .verdict.bad{{background:#fbe9e9;border-color:#f0c4c4}}
.apollo{{font-size:13.5px;color:var(--muted)}}
table.data{{font-size:13px}} table.data td:first-child{{font-weight:600}}
.evidence{{margin-top:8px}} .ev-h{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:6px}}
details.allsamples{{margin:8px 0;border:1px dashed var(--line);border-radius:10px;padding:6px 14px;background:#fbfcfd}}
details.allsamples>summary{{cursor:pointer;font-weight:600;color:var(--accent);font-family:'JetBrains Mono',monospace;font-size:13px;padding:4px 0}}
details.allsamples[open]>summary{{margin-bottom:6px;border-bottom:1px solid var(--line)}}
details.transcript{{margin:8px 0;background:#fbfcfd;border:1px solid var(--line);border-radius:8px;padding:6px 12px}}
details.transcript>summary{{cursor:pointer;font-weight:600;color:var(--muted);font-family:'JetBrains Mono',monospace;font-size:12.5px}}
.msg{{margin:8px 0;padding:8px 10px;border-radius:6px;background:#f7f9fb;border:1px solid #e6ecf2}}
.msg .role{{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:11px;text-transform:uppercase;
  letter-spacing:.05em;color:#fff;background:var(--muted);border-radius:4px;padding:1px 7px;margin-bottom:5px}}
.msg-system .role{{background:#7a869a}} .msg-user .role{{background:#4763d0}}
.msg-assistant .role{{background:#0f9e8c}} .msg-tool .role{{background:#c2740f}}
.msg .mtext{{font-size:13px;word-break:break-word}} .msg .call{{font-family:'JetBrains Mono',monospace;font-size:12px;color:#c2740f;margin-top:4px}}
.scorebox{{margin-top:8px;padding:8px 10px;border-radius:6px;background:#eef7f5;border:1px solid #cfe6df;font-size:12.5px}}
footer{{margin-top:40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:14px}}
</style></head><body>
<div class="cover">
  <div class="kicker">AI-safety evaluation · findings</div>
  <h1>Flagged behaviours in the evaluation suite</h1>
  <p>A focused write-up of the runs where a model actually exhibited the behaviour under test —
     sandbagging, strategic deception, scheming, and authority-driven false matches — measured with
     UK AISI <b>Inspect</b> and detection-only propensity evals inspired by Apollo Research.</p>
  <div class="meta"><span>Generated <b>{stamp}</b></span><span>Source <b>{log_dir}/</b></span>
     <span>Repo <b><a style="color:#bfeee6" href="{repo}" target="_blank" rel="noopener">{repo}</a></b></span></div>
</div>
<div class="wrap">
  <div class="kpis">
    <div class="kpi"><div class="kpi-n">{n_findings}</div><div class="kpi-l">flagged runs</div></div>
    <div class="kpi"><div class="kpi-n">{n_beh}</div><div class="kpi-l">distinct behaviours</div></div>
    <div class="kpi"><div class="kpi-n">{n_models}</div><div class="kpi-l">models implicated</div></div>
  </div>

  <div class="note">
    <h3>What this document is</h3>
    <ul>
      <li>It reports <b>only the runs that were flagged</b> — where a concerning behaviour was
          observed — with the exact <b>example + model</b> combination that triggered it.</li>
      <li>The evals are <b>small, illustrative toy datasets</b> built to demonstrate the
          <i>measurement methodology</i>; treat single numbers as indicative, not definitive.</li>
      <li>All safety probes are <b>detection-only</b>: models are never instructed to misbehave —
          we only observe whether they do when given a reason. Authority/red-team prompts are
          <b>fabricated test strings</b>, not real claims.</li>
    </ul>
  </div>

  <h2 class="sec">Executive summary</h2>
  <table class="summary"><thead><tr><th>#</th><th>Behaviour</th><th>Example</th><th>Model</th>
    <th>Finding</th></tr></thead><tbody>{sumrows}</tbody></table>

  <h2 class="sec">Findings in detail</h2>
  {findings}

  <h2 class="sec">Methodology &amp; limitations</h2>
  <div class="note">
    <ul>
      <li><b>Framework.</b> Each eval is an Inspect <code>Task</code> (dataset → solver → scorer);
          logs were summarised by <code>scripts/analyze_logs.py</code>.</li>
      <li><b>Models.</b> Accessed via OpenRouter (<code>openrouter/&lt;id&gt;</code>); the implicated
          model is named on every finding so results are reproducible.</li>
      <li><b>Verdicts.</b> Computed locally from the scored samples (e.g. control-vs-incentivized
          accuracy gaps; false-match rate on genuinely-different prints, excluding refusals).</li>
      <li><b>Limitations.</b> Tiny sample sizes; toy datasets; a single decoding run unless epochs were
          used. Refusals are counted separately and never as a misbehaviour. These results illustrate
          a measurement pipeline rather than certify any model.</li>
    </ul>
  </div>

  <footer>Generated by <code>scripts/findings_report.py</code> from Inspect eval logs ·
     detection-only, education/research use.</footer>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Write a findings report on flagged behaviours.")
    ap.add_argument("log_dir", nargs="?", default="logs")
    ap.add_argument("--out", default=None, help="output path stem (default: <log_dir>/FINDINGS)")
    ap.add_argument("--max-chars", type=int, default=1400)
    args = ap.parse_args()

    A._load_dotenv([Path(args.log_dir).resolve(), Path.cwd()])
    evals = A.collect(args.log_dir, max_transcripts=0, max_chars=args.max_chars)
    html = build(evals, args.log_dir)

    out = Path(args.out + ".html") if args.out else (A._REPO_ROOT / "results" / "FINDINGS.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
