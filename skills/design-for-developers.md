---
name: design-for-developers
description: Build interfaces that look intentional and premium using AI-generated design systems — visual primitives, spacing rules, and component standards developers can actually follow.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Design for Developers

> You don't need to be a designer to ship good-looking software. You need clear rules and the discipline to follow them.

## When To Use This

- You are a developer who needs to make design decisions without a designer available
- You want AI to generate a practical design system instead of just describing principles
- You are standardizing spacing, type, color, and interaction rules across a project
- You want better visual quality without slowing down engineering velocity

## Workflow

1. **Define visual primitives before any component work.** Spacing scale (4px or 8px base grid), color palette (4-6 colors maximum), typography stack (2 fonts maximum). These three choices determine 80% of how your UI feels.
2. **Translate brand intent into reusable components.** Button variants, card structures, form inputs, navigation patterns. Each component should have a documented "anatomy" — what each part does and why.
3. **Apply hierarchy rules to every screen before detail polish.** Every screen has a primary action, a secondary action, and supporting content. If everything is the same size, nothing is important.
4. **Audit consistency and accessibility before shipping.** WCAG AA contrast ratios on all text. Consistent spacing at every breakpoint. Focus states on every interactive element.

## Signal Prompt

```
Create a developer-first UI design system for: [describe your project — app, marketing site, dashboard].

Include:
1. Spacing scale (based on 4px or 8px grid) with named tokens
2. Color system: primary, secondary, neutral, semantic (success, warning, error) — hex values
3. Typography stack: 2 fonts, defined scale (xs through 4xl), line heights
4. 4 core components with implementation rules: button, card, input field, navigation item
5. Hierarchy rules: how to communicate importance across a screen
6. Accessibility checklist: the 5 checks that catch 90% of issues

Format as a developer reference guide. Include actual values, not just descriptions.
```

## Expected Output

A complete developer design system — tokens, component specs, hierarchy rules, and an accessibility checklist — ready to implement immediately.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Any framework
