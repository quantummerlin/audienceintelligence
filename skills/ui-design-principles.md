---
name: ui-design-principles
description: Audit any interface using first-principles UI heuristics and get a prioritized fix list — clarity, hierarchy, conversion, and accessibility issues ranked by impact.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# UI Design Principles Audit

> Subjective design debates slow everything down. Replace opinions with a heuristic framework and get to decisions faster.

## When To Use This

- You need to review a screen or page for clarity, usability, and conversion strength
- Your team is having subjective design debates that could be resolved with a framework
- You want AI to audit an interface and return a prioritized fix list, not just observations
- You are doing a pre-launch quality check on UI before user testing

## Workflow

1. **Evaluate hierarchy, contrast, and spacing before details.** Is there a clear focal point? Does the primary action stand out? Is there enough breathing room? Fix these before touching colors or typography.
2. **Align layout and copy with user task priority.** What does the user need to do on this screen? Is the most important action the most visually prominent element? If not, that is your first fix.
3. **Check affordance and feedback in core interactions.** Do buttons look like buttons? Does the user know what just happened when they click? Affordance and feedback problems destroy trust faster than visual inconsistency.
4. **Apply consistency and accessibility checks before sign-off.** Same spacing tokens across similar elements. WCAG AA contrast on all text. Focus indicators on every interactive element.

## Signal Prompt

```
Audit this interface using first-principles UI heuristics.

[Describe the screen, paste a screenshot description, or share a URL]

Evaluate against:
1. Visual hierarchy — is there a clear focal point and action priority?
2. Spacing and breathing room — does it feel cluttered or balanced?
3. Affordance — do interactive elements look interactive?
4. Message clarity — can a new user understand the purpose in 5 seconds?
5. Consistency — do similar elements look and behave the same way?
6. Accessibility — contrast ratios, focus states, text size

Return: a prioritized list of fixes (P1/P2/P3), the rationale for each, and a specific implementation recommendation.
```

## Expected Output

A prioritized UI fix list with rationale and specific implementation notes — actionable, not just observational.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Figma · Any interface
