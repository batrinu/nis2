---
name: canvas-design
description: >
  Create museum-quality visual art, posters, and designs as PNG or PDF files using
  design philosophy principles. Use when the user asks to create a poster, piece of art,
  visual design, infographic, cover art, brand visual, or any static visual output.
  Also trigger for "make something beautiful", "design a poster", "create artwork",
  "visual identity", or when the user wants a visually striking deliverable that goes
  beyond standard document formatting.
---

# Canvas Design: Visual Art Creation

Create original visual designs that look like they were crafted by a top-tier designer over many hours. Output .png or .pdf files.

## Two-Step Process

1. **Create a Design Philosophy** (the aesthetic manifesto)
2. **Express it on Canvas** (the artwork itself)

## Step 1: Design Philosophy Creation

Before touching any code or canvas, create an aesthetic manifesto — a philosophy that guides every visual decision.

### How to Create a Philosophy

**Name the movement** (1-2 evocative words):
- "Brutalist Joy" / "Chromatic Silence" / "Metabolist Dreams"
- "Concrete Poetry" / "Analog Meditation" / "Geometric Silence"

**Articulate the philosophy** (4-6 paragraphs) covering:
- **Space and form** — How do elements occupy the canvas?
- **Color and material** — What's the palette logic?
- **Scale and rhythm** — What creates visual pulse?
- **Composition and balance** — Symmetry or tension?
- **Visual hierarchy** — Where does the eye go first?

### Philosophy Examples

**"Concrete Poetry"** — Communication through monumental form and bold geometry.
Massive color blocks, sculptural typography, Brutalist spatial divisions, Polish poster energy.
Text as rare, powerful gesture — never paragraphs, only essential words.

**"Chromatic Language"** — Color as the primary information system.
Geometric precision where color zones create meaning. Think Josef Albers meets data visualization.
Words only to anchor what color already shows.

**"Analog Meditation"** — Quiet visual contemplation through texture and breathing room.
Paper grain, ink bleeds, vast negative space. Japanese photobook aesthetic.
Images breathe across pages. Text appears sparingly.

### Critical Guidelines
- **Emphasize craftsmanship** — The philosophy MUST stress that the final work should appear meticulously crafted, labored over, the product of deep expertise
- **Avoid redundancy** — Each design aspect mentioned once, with depth
- **Leave creative space** — Specific enough to guide, open enough for interpretation
- **Minimal text always** — Text is sparse, essential-only, integrated as visual element

Output the philosophy as a `.md` file.

## Step 2: Canvas Creation

With the philosophy established, create the artwork.

### Execution Principles

1. **Museum/magazine quality** — This should look like it belongs in a gallery or high-end publication
2. **90% visual, 10% text** — Information lives in design, not paragraphs
3. **Repeating patterns and shapes** — Build visual rhythm through systematic repetition
4. **Limited color palette** — Intentional, cohesive, never random
5. **Typography as art** — When text appears, it's a design element, not just content
6. **Nothing overlaps unintentionally** — Every element has breathing room
7. **Everything within boundaries** — Proper margins, no elements falling off the canvas

### Technical Approach

Use Python with libraries like:
- **Pillow/PIL** — Image composition, drawing, text rendering
- **reportlab** — PDF generation with precise layout control
- **cairo/pycairo** — Vector graphics, complex shapes
- **matplotlib** — When data visualization is part of the art

### Typography Rules
- Use different fonts for different roles (display vs label)
- Font should usually be thin/light for sophistication
- Text is contextual — a punk poster has aggressive type, a gallery piece has whisper-quiet labels
- Download and use quality fonts, don't settle for system defaults

### Quality Checklist Before Delivery
- [ ] Does it look like it took hours to create?
- [ ] Is the color palette cohesive and intentional?
- [ ] Is text minimal and integrated as a visual element?
- [ ] Do all elements have clear spacing — nothing overlapping?
- [ ] Is there a clear visual hierarchy?
- [ ] Does it embody the design philosophy?
- [ ] Could this hang in a gallery or appear in a magazine?

### Final Refinement Pass

**CRITICAL**: After the first version, take a second pass:
- Don't add more graphics — refine what exists
- Make it crisper, more cohesive with the philosophy
- If the instinct is to add a new element, STOP and ask: "How can I make what's already here more of a piece of art?"
- Tighten spacing, adjust color values, perfect alignments

### Multi-Page Option

If requested, create additional pages that:
- Follow the same design philosophy but are distinctly different
- Tell a visual story across pages
- Feel like a coffee table book, not a repeated template
- Bundle in a single PDF

Output the final result as a `.pdf` or `.png` file alongside the design philosophy `.md` file.
