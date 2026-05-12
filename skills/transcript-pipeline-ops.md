---
name: transcript-pipeline-ops
description: Operationalize YouTube transcript mining into a repeatable intelligence pipeline — from raw scrape to ranked insights to publishable artifacts.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Transcript Pipeline Ops

> Turn raw transcripts into ranked intelligence. Make the process repeatable, not a one-time grind.

## When To Use This

- You are extracting patterns, tactics, or signal from batches of YouTube transcripts
- You need consistent ranking, tagging, and packaging of insights across many sources
- You want to shorten the time from raw content capture to usable, shareable artifacts
- You are building an AI-driven content or intelligence operation at any scale

## Workflow

1. **Ingest and normalize.** Load transcript batches and standardize metadata: source, date, topic, length. Consistent fields make everything downstream faster.
2. **Score and prioritize.** Rank segments by signal strength — novelty, practical utility, frequency of appearance across sources. Surface the top 20% first.
3. **Package for output.** Transform ranked insights into concrete artifacts: prompt packs, templates, briefs, article outlines. Each output should be immediately usable.
4. **Version and audit.** Keep outputs versioned so updates are traceable and you can build on prior runs rather than starting from scratch.

## Signal Prompt

```
I have a transcript dataset from [source/topic]. Process it as follows:

1. Identify the 10 highest-signal insights — ranked by practical utility and novelty
2. For each insight, note: the core idea, a direct quote if present, and one concrete application
3. Group insights into themes
4. Package the output as a ready-to-use brief with clear implementation steps

Format: structured markdown, no filler, every claim grounded in the transcript data.
```

## Expected Output

A ranked intelligence brief — insights grouped by theme, each with a practical application and implementation guidance — ready to turn into articles, prompts, or training material.

## Compatible With

Claude · GPT-4o · Cursor · Any LLM with large context window
