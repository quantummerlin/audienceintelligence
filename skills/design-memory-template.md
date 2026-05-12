---
name: design-memory-template
description: A reusable markdown scaffold for capturing a project's visual DNA — typography, color, spacing, components, motion, and voice — before asking any AI to generate anything.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot, Any image or design AI
---

# Design Memory Template

> AI forgets your brand between sessions. This file gives it a permanent memory. Build it once, attach it everywhere.

## Why This Exists

When you generate page 1 in one session and page 5 in another, the AI has no memory of what you built before. Without a design memory file, every generation starts from default assumptions — and defaults look like everyone else.

`design-memory.md` is the fix. It's a portable, structured brief you attach to every prompt. It keeps taste, spacing, color, and motion rules consistent across tools, sessions, and team members.

## What To Capture

1. **Brand intent** — tone, audience, what feeling the brand should produce
2. **Visual DNA** — primary and accent colors (hex), typography stack and scale, spacing unit, corner radii
3. **Component rules** — how buttons, cards, inputs, and navigation should behave
4. **Motion language** — duration scale, easing defaults, what should and shouldn't animate
5. **Imagery direction** — photography style, illustration approach, what to avoid
6. **Voice and copy** — headline tone, reading level, phrases to avoid
7. **Quality gate** — the 5 checks every output must pass before shipping

## Signal Prompt

```
Create design-memory.md for this project:

Project: [name]
Audience: [describe them]
Core feeling the brand should produce: [e.g. intelligent, warm, premium, urgent]
Reference sites or brands with similar aesthetic: [list 2-3]

Capture:
1. Brand intent in 3 sentences
2. Visual DNA: exact hex values, font names, spacing unit (4px or 8px grid), border radius
3. Component rules: button styles, card anatomy, form field behavior
4. Motion: transition duration, easing, what animates vs. what stays static
5. Imagery: photography mood, what to avoid
6. Voice: tone, reading level, 5 words that should never appear in copy
7. Quality gate: 5 checks before any asset ships

Make it concise enough to paste into a prompt. Specific enough to prevent generic output.
```

## Expected Output

A complete `design-memory.md` file you can attach to any AI prompt to maintain visual consistency across your entire project.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Midjourney · Any image or design AI

## Pair With

Use this skill with the **Anti-AI Slop Design** skill to enforce consistency at scale.
