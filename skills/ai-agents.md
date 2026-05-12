---
name: ai-agents
description: Design persistent AI agents that monitor, decide, and execute autonomously — with memory, scheduled actions, and cross-tool orchestration.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot, Any LLM
---

# AI Agents

> Build agents that work while you don't. Memory-first, outcome-driven, durable by design.

## When To Use This

- You need ongoing autonomous workflows that run on a schedule or in response to events
- You are building agents with persistent memory across sessions
- You want cross-tool orchestration across inbox, CRM, and collaboration apps
- You need an agent that monitors something (a pipeline, inbox, or market signal) and takes action

## Workflow

1. **Define outcomes and hard constraints first.** What must the agent achieve? What must it never do? Write these before touching any prompt.
2. **Compose the agent anatomy.** System prompt → skills → invocation schedule → integrations → memory rules. Each layer should have a clear job.
3. **Set up heartbeat checks and event-driven triggers.** Scheduled runs keep the agent alive. Event triggers (new email, Slack mention, pipeline change) keep it responsive.
4. **Evaluate with rubrics, not vibes.** Define what "good output" looks like before the first run. Score outputs and refine the behavior loop.

## Signal Prompt

```
Design an autonomous agent for the following mission: [describe task].

Before writing any prompt, answer:
- What is the agent's single most important outcome?
- What are the hard constraints it must never violate?
- What data sources or integrations does it need?
- How often should it run, and what should trigger it outside of schedule?

Then compose: system prompt, required skills, integration list, memory rules, and a quality rubric for evaluating outputs.
```

## Expected Output

A fully specified agent blueprint — system prompt, integration map, skill list, schedule, and evaluation rubric — ready to deploy and iterate.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Any LLM with tool-use support
