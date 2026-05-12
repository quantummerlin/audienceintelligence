---
name: tailwind-mastery
description: Build scalable, consistent Tailwind component systems with AI — design tokens, utility conventions, and reusable patterns that survive growth.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Tailwind Mastery with AI

> Tailwind at scale requires architecture, not just classes. Use AI to build the system, not just the components.

## When To Use This

- You are building a multi-page product or marketing site and need consistent design tokens
- You want AI to scaffold a Tailwind component system with clear naming conventions
- You are scaling a codebase and utility classes are becoming hard to maintain
- You need a design-to-code workflow that moves fast without breaking consistency

## Workflow

1. **Define theme tokens and spacing rhythm first.** Colors, font sizes, spacing scale, border radii. Lock these in `tailwind.config.js` before writing any component markup.
2. **Build composable components with clear utility conventions.** Use consistent patterns: layout utilities first, then typography, then color, then interaction states. Readable order matters.
3. **Refactor repeated utility bundles into shared patterns.** If the same 8 classes appear in 10 places, extract them. Either as `@apply` groups or as a documented component class.
4. **Validate responsiveness and visual consistency.** Test at sm/md/lg breakpoints. Consistent padding and type scale across breakpoints matters more than most visual decisions.

## Signal Prompt

```
I am building a [describe project: product app / marketing site / dashboard] with Tailwind CSS.

Create a complete Tailwind component system including:
1. tailwind.config.js with custom tokens (colors, spacing scale, typography)
2. Naming conventions and utility ordering rules
3. 5 core reusable components: [button, card, input, nav, hero — or specify your own]
4. Responsive breakpoint strategy
5. A short reference guide for consistent implementation

Make the system maintainable for a small team over 12+ months.
```

## Expected Output

A documented Tailwind design system — config file, component patterns, and implementation guide — ready to use as a project foundation.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Tailwind CSS v3/v4
