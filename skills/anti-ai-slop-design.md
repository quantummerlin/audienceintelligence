---
name: anti-ai-slop-design
description: A quality enforcement workflow for AI-generated design — design memory first, deep iteration second, remix only after craft is locked. Stops generic output before it ships.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot, Any image AI
---

# Anti-AI Slop Design

> The first screen looks great. The fifth screen looks like everyone else's. This skill fixes that.

## When To Use This

- Your AI-generated designs are consistent on the first pass but drift into generic on follow-up pages
- You need your brand system to survive across multiple AI generation sessions
- You are producing web pages, slides, social content, or marketing assets at volume and quality is slipping
- You want a repeatable quality gate before anything ships publicly

## Workflow

1. **Build `design-memory.md` before any generation.** Document: brand intent, typography rules, color roles, spacing rhythm, component patterns, motion language. This file is your AI's source of truth for every session. See the Design Memory Template skill.
2. **Attach design memory and references to every prompt.** Every generation pass starts with: "Use design-memory.md as your source of truth." No exceptions.
3. **Run focused iteration loops — not single-pass generation.** Generate 3 distinct directions, not one. Score each against your quality gate. Pick the strongest and iterate it through 3 refinement passes.
4. **Apply the quality gate before shipping.** Check: visual consistency with prior pages, originality (no generic template patterns), conversion clarity (does the message land in 5 seconds?), and language hygiene (no em dashes — use commas, periods, or colons instead).
5. **Remix into other formats only after craft is locked.** Slides, social cuts, mobile variants — only after the master version passes the gate.

## Signal Prompt

```
Use design-memory.md as the source of truth for this project.

Generate 3 distinct design directions for: [describe page or asset].

For each direction:
- Apply the brand system from design-memory.md strictly
- Reject any generic template patterns (gradient blobs, stock hero layouts, default card grids)
- Write a self-review: consistency score, originality score, conversion clarity score
- Use no em dashes (—). Replace with commas, periods, or colons.

Select the highest-scoring direction. Run 3 iteration passes on it before producing any derivative formats.

Do not proceed to derivatives until I approve the refined master version.
```

## Expected Output

3 scored design directions, a refined winner after iteration passes, and derivative formats produced from the approved master — not from generic defaults.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Midjourney · Stable Diffusion · Any image or web AI

## Pair With

Use this skill with the **Design Memory Template** skill for the strongest results.
