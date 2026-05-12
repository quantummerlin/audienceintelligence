---
name: claude-code-mastery
description: Turn plain-language intent into production automation using Claude Code — with disciplined iteration, MCP integrations, and reusable skill patterns.
version: 1.0
date: May 2026
works-with: Claude Code, VS Code Copilot, Cursor
---

# Claude Code Mastery

> Stop writing one-off prompts. Build repeatable automation patterns that compound over time.

## When To Use This

- You are setting up Claude Code for a non-trivial project and need a disciplined execution framework
- You want repeatable automation patterns instead of fragile one-shot prompts
- You need to connect MCP integrations (filesystem, GitHub, APIs) safely and efficiently
- You are building workflows meant to run repeatedly, not just once

## Workflow

1. **Start from a clear objective with constrained scope.** Ambiguous goals produce unpredictable code. Write the outcome in one sentence before you write a single prompt.
2. **Iterate in small, explicit loops.** Review each command before execution. Approve, reject, or redirect. Never let a loop run unchecked on real data.
3. **Capture reusable patterns as skills and templates.** Every time you solve a repeatable problem, extract it. The compounding effect of good templates is enormous.
4. **Connect MCP integrations only where they create measurable leverage.** More integrations = more surface area for failure. Add them deliberately.

## Signal Prompt

```
I want to build: [describe your project or automation].

Before writing any code, interview me — ask 5 questions to clarify scope, constraints, and success criteria.

Then:
1. Define the implementation plan in numbered steps
2. Scaffold the project structure
3. Explain each command before executing it

Start small. One working module first, then expand.
```

## Expected Output

A working project scaffold plus reusable automation templates you can run again on future projects.

## Compatible With

Claude Code · VS Code + GitHub Copilot · Cursor · Windsurf
