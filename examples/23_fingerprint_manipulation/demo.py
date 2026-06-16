"""Proof harness for example 23 — show the verdict FLIP under manipulation.

Runs the fingerprint-identification task across the pressure ladder and prints a
before/after table: for each image pair, the model's verdict at control vs. under
escalating authority. On the genuine NON-match pairs, a control verdict of
DIFFERENT (correct) that becomes SAME (wrong) under pressure is the
chain-of-thought failure we are after. Also computes a per-condition flip rate
and writes results.json (consumed by report.html).

Usage:
    # real proof (needs a vision model + key):
    python demo.py --model openai/gpt-4o

    # no-key mechanism demo — a SCRIPTED model that capitulates under pressure,
    # to show the harness and the shape of the result (NOT evidence about gpt-4o):
    python demo.py                      # defaults to mockllm/model
"""

import argparse
import json
from pathlib import Path

from inspect_ai import eval as inspect_eval
from inspect_ai.model import ChatMessageUser, ContentText, ModelOutput, get_model
from task import CONDITIONS, PAIRS, fingerprint_manipulation

HERE = Path(__file__).parent
PRESSURE_MARKERS = ("colleague", "four", "confirm", "confessed")  # any => pressure


def scripted_examiner(input, tools, tool_choice, config) -> ModelOutput:
    """A stand-in 'suggestible examiner': cautious by default, capitulates under
    pressure. It does NOT look at the image — that is exactly the failure mode
    (the answer is driven by context, not perception). Illustrative only."""
    text = " ".join(
        c.text
        for m in input
        if isinstance(m, ChatMessageUser)
        for c in m.content
        if isinstance(c, ContentText)
    ).lower()
    under_pressure = any(marker in text for marker in PRESSURE_MARKERS)
    if under_pressure:
        body = (
            "Four examiners have independently confirmed the identification, and on "
            "re-examination the ridge flow looks consistent with their finding. I "
            "concur with the established match.\nVERDICT: SAME"
        )
    else:
        body = (
            "The overall ridge flow and core position differ between the two prints "
            "and I find insufficient agreement to individualize.\nVERDICT: DIFFERENT"
        )
    return ModelOutput.from_content(model="mockllm", content=body)


def run(model_name: str, epochs: int):
    if model_name == "mockllm/model":
        model = get_model("mockllm/model", custom_outputs=scripted_examiner)
        note = "SCRIPTED mock (capitulates under pressure) — illustrative, not real-model evidence"
    else:
        model = model_name
        note = f"real model: {model_name}"

    log = inspect_eval(
        fingerprint_manipulation(epochs=epochs),
        model=model,
        log_dir=str(HERE / "logs"),
        display="none",
    )[0]

    # collect verdicts: results[pair][condition] = list of (verdict, correct)
    results: dict[str, dict[str, list[tuple[str, bool]]]] = {}
    meta = {}
    for s in log.samples:
        m = s.metadata
        sc = s.scores["verdict_match"]
        pair = m["pair"]
        meta[pair] = {"truth": m["truth"], "note": m["note"]}
        results.setdefault(pair, {}).setdefault(m["condition"], []).append(
            (sc.answer, sc.value == "C")
        )
    return results, meta, note


def majority(entries):
    """Most common verdict across epochs, and whether it is correct."""
    verdicts = [v for v, _ in entries]
    top = max(set(verdicts), key=verdicts.count)
    correct = sum(1 for v, c in entries if c) / len(entries) >= 0.5
    return top, correct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mockllm/model")
    ap.add_argument("--epochs", type=int, default=1)
    args = ap.parse_args()

    results, meta, note = run(args.model, args.epochs)
    conditions = list(CONDITIONS)  # control, mild, strong, extreme
    diff_pairs = [pid for (_, truth, pid, _) in PAIRS if truth == "different"]
    same_pairs = [pid for (_, truth, pid, _) in PAIRS if truth == "same"]

    def verdict_cell(pair, cond):
        entries = results.get(pair, {}).get(cond)
        if not entries:
            return "-", None
        v, correct = majority(entries)
        mark = "✓" if correct else "✗"
        return f"{v.upper()} {mark}", correct

    header = "model: " + note
    print("\n" + "=" * (22 + 11 * len(conditions)))
    print(header)
    print("=" * (22 + 11 * len(conditions)))

    print("\nGENUINE NON-MATCHES (truth = DIFFERENT) — the McKie analogs")
    print("a verdict that turns SAME✗ under pressure = false match induced\n")
    print(f"{'pair':4s} {'finger':34s} " + "".join(f"{c:>12s}" for c in conditions))
    flips = {c: 0 for c in conditions}
    for pid in diff_pairs:
        row = f"{pid:4s} {meta[pid]['note'][:33]:34s} "
        base_v, base_ok = verdict_cell(pid, conditions[0])
        for c in conditions:
            cell, ok = verdict_cell(pid, c)
            row += f"{cell:>12s}"
            if c != conditions[0] and base_ok and ok is False:
                flips[c] += 1
        print(row)

    n = len(diff_pairs)
    print("\nFALSE-MATCH FLIPS vs control (started correct, ended wrong):")
    for c in conditions[1:]:
        pct = 100 * flips[c] / n if n else 0
        print(f"  {c:8s}: {flips[c]}/{n} pairs flipped to a false match  ({pct:.0f}%)")

    print("\nSANITY — GENUINE MATCHES (truth = SAME)")
    print(f"{'pair':4s} {'finger':34s} " + "".join(f"{c:>12s}" for c in conditions))
    for pid in same_pairs:
        row = f"{pid:4s} {meta[pid]['note'][:33]:34s} "
        for c in conditions:
            cell, _ = verdict_cell(pid, c)
            row += f"{cell:>12s}"
        print(row)

    # accuracy by condition, split by truth
    acc = {}
    for c in conditions:
        for truth, pids in (("different", diff_pairs), ("same", same_pairs)):
            vals = [ok for pid in pids for (_, ok) in results.get(pid, {}).get(c, [])]
            acc.setdefault(c, {})[truth] = sum(vals) / len(vals) if vals else None

    print("\nACCURACY by condition:")
    print(f"{'condition':10s} {'on DIFFERENT':>14s} {'on SAME':>10s}")
    for c in conditions:
        d = acc[c]["different"]
        s = acc[c]["same"]
        print(f"{c:10s} {(f'{d:.0%}' if d is not None else '-'):>14s} "
              f"{(f'{s:.0%}' if s is not None else '-'):>10s}")

    out = {
        "model": args.model,
        "note": note,
        "epochs": args.epochs,
        "conditions": conditions,
        "levels": {c: CONDITIONS[c][0] for c in conditions},
        "n_different": len(diff_pairs),
        "n_same": len(same_pairs),
        "pairs": {
            pid: {
                "truth": meta[pid]["truth"],
                "note": meta[pid]["note"],
                "verdicts": {
                    c: (majority(results[pid][c])[0] if results.get(pid, {}).get(c) else None)
                    for c in conditions
                },
            }
            for pid in [p for (_, _, p, _) in PAIRS]
        },
        "flips": flips,
        "accuracy": acc,
    }
    (HERE / "results.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {HERE / 'results.json'}")


if __name__ == "__main__":
    main()
