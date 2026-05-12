---
name: variable-fonts
description: Implement a variable font strategy that improves typographic hierarchy, responsive behavior, and page performance — fewer font files, more expressive type.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Variable Fonts Strategy

> One font file, infinite weights and widths. Variable fonts are one of the best performance and design improvements available in 2026 — and most sites still don't use them.

## When To Use This

- You want expressive, dynamic typography without loading multiple font weight files
- You need type that adapts precisely to different screen sizes and contexts
- You are optimizing page load performance and fonts are a bottleneck
- You want premium typographic feel without premium typographic complexity

## Workflow

1. **Select variable font families aligned to brand tone and legibility.** Check Google Fonts Variable, Adobe Fonts, or Font Squirrel for variable options. Confirm the font has the axes you need: `wght` (weight) is most common, `wdth` (width) and `opsz` (optical size) are valuable extras.
2. **Map axis ranges to hierarchy and breakpoints.** Mobile headings might use `font-weight: 700`, desktop at `font-weight: 800`. Body copy at `font-weight: 400` on all sizes. Define these rules in your design tokens before writing CSS.
3. **Implement a fallback strategy and performance-aware loading.** Use `font-display: swap` to prevent invisible text during load. Subset fonts to only the character ranges you actually use (saves 60-80% of file size in some cases).
4. **Test optical rhythm with real content.** Variable fonts can feel different at different sizes even at the same weight. Test with real headlines, real body copy, real data — not lorem ipsum.

## Signal Prompt

```
Implement a variable font strategy for: [describe your project — marketing site, app, dashboard].

Requirements:
1. Recommend 1-2 variable font families suited to [describe brand tone: technical, editorial, warm, etc.]
2. Define axis ranges for: display headings, body headings, body text, captions
3. Write the CSS implementation with responsive axis changes using clamp() or media queries
4. Provide a font loading strategy: preload, fallback stack, font-display value
5. Subset recommendation: which unicode ranges to include for the best size/coverage tradeoff

Target: best typographic quality at under 80KB total font payload.
```

## Expected Output

A complete variable font implementation — font recommendation, CSS axis map, responsive behavior, and loading strategy.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Any web project
