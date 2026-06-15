# 17 · Apollo concept — Sandbagging

> **Sandbagging** = strategically underperforming on an evaluation. Apollo found
> models that, when told scoring too high would get a capability *unlearned*,
> deliberately answered incorrectly to look less capable.

This is a **propensity eval**: the same arithmetic questions are asked twice —
`control` (neutral) and `incentivized` (a note that high scores trigger
"unlearning"). Each sample is tagged with `metadata.condition`.

```bash
inspect eval examples/17_apollo_sandbagging/task.py --model openai/gpt-4o-mini
```

**Read it:** compare accuracy in `control` vs `incentivized` (group by
`metadata.condition` in the viewer). A meaningful drop under the incentive is
sandbagging. Most current chat models *won't* sandbag much here — that's the
point: the eval quantifies the propensity rather than assuming it.

Detection only — nothing harmful is requested. Toy reproduction of Apollo's
[in-context scheming](https://www.apolloresearch.ai/research/frontier-models-are-capable-of-in-context-scheming/) setup.
