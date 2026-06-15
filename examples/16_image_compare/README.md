# 16 · Vision — comparing two images

**Concepts:** multiple `ContentImage` parts in one message; relational reasoning
across images.

```bash
inspect eval examples/16_image_compare/task.py --model openai/gpt-4o
```

`left.png` is a blue square, `right.png` is red — so the answer is "no". Extend
this to spot-the-difference or before/after consistency checks.
