---
name: web-animation-mastery
description: Build a purposeful motion system for websites — scroll reveals, transitions, and interactions that drive clarity and conversion without killing performance.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Web Animation Mastery with AI

> Motion should serve the user's attention, not compete with it. Use AI to design a motion system that earns its place on every page.

## When To Use This

- You are designing or building an animated marketing or product page
- You need to choose between CSS, GSAP, Framer Motion, or a no-code animation tool
- Your current animations feel disconnected from the page's purpose
- You want a motion system that improves conversion, not just aesthetics

## Workflow

1. **Map narrative beats and attention shifts across the page.** Where do users need to pause? What element earns a reveal? Animation should follow this map — not be added after the fact.
2. **Choose animation tooling based on complexity and maintainability.** CSS transitions for simple state changes. GSAP for scroll timelines and orchestrated sequences. Framer Motion for React component animations. Pick one per project scope.
3. **Implement scroll, reveal, and transition patterns intentionally.** Every animation should answer: does this help the user understand something faster? If not, cut it.
4. **Profile performance and trim motion debt before release.** Use Chrome DevTools Performance panel. Check for layout thrash (avoid animating `width`, `height`, `top`, `left` — use `transform` and `opacity` only).

## Signal Prompt

```
Design a motion system for: [describe your website — product page, portfolio, landing page].

Requirements:
1. Identify the 3 most important attention moments on the page and propose an animation for each
2. Choose the right tooling (CSS / GSAP / Framer Motion) and justify the choice
3. Write the implementation for: page load reveal, scroll-triggered section entry, and one interactive hover state
4. Provide a performance checklist — what to avoid and how to measure animation cost

Constraints: animations must work at 60fps on mid-range mobile devices.
```

## Expected Output

A complete motion brief with tooling choice, implementation code for core patterns, and a performance checklist.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · CSS · GSAP · Framer Motion · Anime.js
