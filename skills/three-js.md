---
name: three-js
description: Build immersive 3D web experiences with AI assistance — scroll-driven scenes, interactive objects, and production-ready Three.js or React Three Fiber workflows.
version: 1.0
date: May 2026
works-with: Claude, GPT-4o, Cursor, VS Code Copilot
---

# Three.js with AI

> 3D on the web is no longer a specialist skill. Use AI to architect, build, and optimize scenes you couldn't ship alone.

## When To Use This

- You are adding 3D to a product page, portfolio, or marketing site
- You need scroll-driven or interaction-driven scene control
- You want AI to handle boilerplate (camera setup, lighting rigs, asset loading) so you can focus on narrative
- You are working with Three.js directly or via React Three Fiber (R3F)

## Workflow

1. **Set up scene architecture and performance budgets before writing a single line.** Define draw call limits, target frame rate, and mobile behavior. Constraints produce better 3D decisions than freedom.
2. **Load assets with intentional lighting and camera placement.** Never use default lighting. Define your key light, fill, and ambient values. Camera position tells the story.
3. **Connect interactions and scroll timelines to narrative beats.** What moment in the scroll reveals the product? What click triggers the scene transition? Map it before implementing it.
4. **Optimize render cost before deployment.** Draco-compress geometry, use KTX2 textures, and profile with Chrome DevTools. A beautiful scene that runs at 20fps is not shippable.

## Signal Prompt

```
Build a Three.js scene for: [describe the experience — product reveal, portfolio piece, landing page background].

Constraints:
- Target frame rate: 60fps on desktop, 30fps on mobile
- Max draw calls: [number, or leave blank for AI to suggest]
- Scroll-driven: [yes/no]
- React Three Fiber or vanilla Three.js: [specify]

Requirements:
1. Scene setup: camera, lighting rig, and renderer configuration
2. Asset loading with appropriate compression and fallbacks
3. Interaction or scroll timeline mapped to [describe narrative moment]
4. Performance checklist before final output

Explain each major decision so I understand the architecture.
```

## Expected Output

A fully commented Three.js or R3F scene with performance-aware architecture, interaction wiring, and an optimization checklist.

## Compatible With

Claude · GPT-4o · Cursor · VS Code Copilot · Three.js · React Three Fiber
