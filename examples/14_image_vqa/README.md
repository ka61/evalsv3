# 14 · Vision — single-image Q&A

**Concepts:** multimodal `Sample.input` built from `ChatMessageUser` with
`ContentText` + `ContentImage`; needs a **vision model**.

```bash
inspect eval examples/14_image_vqa/task.py --model openai/gpt-4o
```

The image (`assets/shape.png`) is a red circle; the model should answer "red".
`ContentImage(image=...)` accepts a local path, URL, or data URI.
