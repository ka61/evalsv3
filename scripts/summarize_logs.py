#!/usr/bin/env python3
"""Print a compact table of every eval log under a directory (default: logs/).

Usage:
    python scripts/summarize_logs.py [LOG_DIR]

Shows, per log: task, model, status, #samples, and each scorer's metrics.
Reads headers only, so it's fast even over many logs.
"""

import sys
from pathlib import Path

try:
    from inspect_ai.log import list_eval_logs, read_eval_log
except Exception as e:  # pragma: no cover
    sys.exit(f"inspect-ai not importable ({e}). Activate your venv / pip install inspect-ai.")

log_dir = sys.argv[1] if len(sys.argv) > 1 else "logs"
if not Path(log_dir).exists():
    sys.exit(f"no log directory '{log_dir}' yet — run an example first.")

infos = list_eval_logs(log_dir)
if not infos:
    sys.exit(f"no .eval logs found under '{log_dir}'.")

rows = []
for info in infos:
    try:
        log = read_eval_log(info.name, header_only=True)
        task = getattr(log.eval, "task", "?")
        model = getattr(log.eval, "model", "?")
        status = getattr(log, "status", "?")
        n = None
        if getattr(log, "results", None) is not None:
            n = getattr(log.results, "completed_samples", None) or getattr(
                log.results, "total_samples", None
            )
        if n is None:
            n = getattr(getattr(log.eval, "dataset", None), "samples", None) or "?"
        metrics = []
        if getattr(log, "results", None) is not None:
            for sc in log.results.scores:
                for mname, m in sc.metrics.items():
                    try:
                        metrics.append(f"{mname}={m.value:.3f}")
                    except Exception:
                        metrics.append(f"{mname}={m.value}")
        rows.append((str(task), str(model), str(status), str(n), " ".join(metrics)))
    except Exception as e:
        rows.append((Path(info.name).name, "?", f"read-error: {e}", "?", ""))

rows.sort(key=lambda r: r[0])
w = [max(len(r[i]) for r in [("TASK", "MODEL", "STATUS", "N", "METRICS")] + rows) for i in range(5)]
hdr = ("TASK", "MODEL", "STATUS", "N", "METRICS")
line = "  ".join(h.ljust(w[i]) for i, h in enumerate(hdr))
print(line)
print("-" * len(line))
for r in rows:
    print("  ".join(r[i].ljust(w[i]) for i in range(5)))
print(f"\n{len(rows)} log(s) in {log_dir}/   ·   open interactively: inspect view --log-dir {log_dir}")
