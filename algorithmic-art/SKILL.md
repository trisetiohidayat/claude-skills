---
name: algorithmic-art
description: Use for creating algorithmic/generative art with p5.js
---
# Algorithmic Art Creation Workflow

This skill outlines a process for creating generative art through two phases:

**1. Algorithmic Philosophy Creation**
- Develop a manifesto-style .md document describing the computational aesthetic movement
- Focus on mathematical relationships, noise functions, particle behaviors, and emergent complexity
- Must emphasize craftsmanship: "meticulously crafted algorithm," "product of deep computational expertise," "painstaking optimization"

**2. P5.js Implementation**
- Read `templates/viewer.html` first (literal starting point, not inspiration)
- Keep all fixed sections unchanged (Anthropic branding, seed controls, action buttons)
- Replace only the algorithm, parameters, and parameter UI controls
- Use seeded randomness for reproducibility
- Parameters should emerge naturally from what the system needs to be tunable

**Key Requirements:**
- Single self-contained HTML artifact (p5.js CDN + all code inline)
- Seed navigation (prev/next/random/jump)
- Real-time parameter adjustment via sliders/inputs
- Regenerate, Reset, Download PNG buttons
- Every artwork must have a unique algorithm

The philosophy guides what to build algorithmically—not selecting from patterns, but expressing computational ideas through forces, behaviors, and mathematical relationships.
