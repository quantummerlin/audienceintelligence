---
name: web-performance
description: Diagnose sluggish websites and produce a prioritized optimization plan that improves Core Web Vitals, LCP, and user-perceived speed under real-world conditions.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Web Performance Optimization

> Speed is a product feature. Every 100ms of load time costs conversions. Use AI to find and fix the highest-impact bottlenecks first.

## When To Use This

- You need better Core Web Vitals scores (LCP, INP, CLS) before a launch or audit
- You are diagnosing sluggish interactions, janky scrolling, or heavy page loads
- You want a repeatable optimization workflow rather than one-off fixes
- You are preparing a site for Google Search performance signals

## Workflow

1. **Benchmark first, fix second.** Run PageSpeed Insights, Chrome DevTools Lighthouse, and WebPageTest. Collect LCP, INP, CLS, TTFB, and total blocking time. You cannot prioritize without data.
2. **Attack the loading path.** Eliminate render-blocking scripts and CSS. Lazy-load images below the fold. Preload the LCP element explicitly. Serve next-gen image formats (WebP, AVIF).
3. **Reduce runtime work.** Defer non-critical JavaScript. Use `will-change` sparingly and only for elements you know will animate. Profile main thread work to find long tasks.
4. **Implement caching and prevent regressions.** Set aggressive Cache-Control headers for static assets. Add a Lighthouse CI step to your deployment pipeline so performance can't degrade silently.

## Signal Prompt

```
Audit this website for real-world performance: [paste URL or describe the site/stack].

Provide:
1. Top 5 bottlenecks ranked by impact on LCP, INP, and CLS
2. Specific fix for each bottleneck — code change, config change, or tooling recommendation
3. Estimated improvement for each fix (high/medium/low)
4. Implementation order: what to fix first for the biggest immediate gain
5. A regression prevention strategy — how to keep these fixes in place over time

Assume a non-specialist developer will implement these changes.
```

## Expected Output

A prioritized performance fix list — ranked by impact, with specific implementation steps and a regression prevention plan.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Any web stack
