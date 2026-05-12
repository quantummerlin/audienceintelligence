---
name: tailwind-tips
description: A practical Tailwind execution playbook — quick-win patterns for layout, spacing, typography, and responsive design that improve speed and consistency immediately.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Tailwind Quick-Win Patterns

> The Tailwind patterns that cut the most time and produce the most consistent results. No theory — just what works.

## When To Use This

- You want faster implementation without messy class sprawl
- You are troubleshooting layout, spacing, or typography inconsistencies
- You need a reference playbook your team can follow without debates
- You are cleaning up an existing Tailwind codebase

## Workflow

1. **Identify repeated interface patterns in your project.** Navigation, cards, hero sections, form elements. These are your extraction targets.
2. **Apply compact class strategies for readability.** Put layout first, typography second, color third, interaction states last. Every developer on the team follows the same order.
3. **Promote reusable snippets and document conventions.** A 10-line README on class ordering prevents hours of code review debates.
4. **Continuously trim dead styles and accidental complexity.** Use the Tailwind CSS IntelliSense VS Code extension or PurgeCSS reports to catch unused classes before they accumulate.

## Signal Prompt

```
Give me a practical Tailwind execution playbook with quick-win patterns for:

1. Responsive flexbox and grid layouts (common patterns, not documentation)
2. Typography scale — consistent heading and body sizing across breakpoints
3. Spacing discipline — margin/padding patterns that don't drift over time
4. Interactive states — hover, focus, disabled patterns worth standardizing
5. Dark mode toggle approach
6. 5 common mistakes to avoid

Format as a developer-ready reference guide. Specific classes and patterns only — no explanations of what Tailwind is.
```

## Expected Output

A developer reference playbook — patterns, anti-patterns, and class conventions — ready to drop into your project's documentation.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Tailwind CSS v3/v4
