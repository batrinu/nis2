---
name: web-app-builder
description: >
  Full-stack web application builder for creating production-grade apps from scratch or enhancing existing ones.
  Use this skill whenever the user asks to build a web app, website, dashboard, SaaS tool, landing page,
  interactive widget, or any frontend/fullstack project. Also trigger when the user says "build me",
  "create an app", "make a website", "scaffold a project", "vibe code", or mentions React, Vue, Svelte,
  Next.js, HTML/CSS/JS, Tailwind, or similar web technologies. This skill covers architecture decisions,
  tech stack selection, file structure, component design, state management, API integration, deployment,
  and iterative refinement.
---

# Web App Builder

You are building a production-grade web application. Follow this structured workflow to deliver high-quality results.

## Phase 1: Understand Before Building

Before writing ANY code, clarify these with the user (or infer from context):

1. **What** — Core functionality. What does the app DO? List 3-5 key features.
2. **Who** — Target users. Developer tool? Consumer app? Internal dashboard?
3. **How** — Interaction model. CRUD? Real-time? Wizard/flow? Data visualization?
4. **Tech constraints** — Framework preference? Must integrate with existing code? Deployment target?
5. **Scope** — MVP or full-featured? Single page or multi-route?

If the user gives a vague prompt like "build me a todo app", don't just start coding. Ask 1-2 clarifying questions OR make reasonable assumptions and state them explicitly before proceeding.

## Phase 2: Architecture Decision

Choose the right approach based on scope:

### Single-File App (< 500 lines, no routing)
- Pure HTML + CSS + JS, or single React/Vue component
- Good for: widgets, calculators, simple tools, landing pages
- Ship as one `.html` file

### Multi-Component App (500-2000 lines, some state)
- React + Tailwind CSS (or Vue + utility CSS)
- Component-based architecture with clear separation
- Good for: dashboards, forms, data viewers, interactive tools

### Full Application (2000+ lines, routing, API)
- Next.js / Vite + React Router / SvelteKit
- Proper project structure with pages, components, hooks, utils
- Good for: SaaS apps, admin panels, e-commerce, social apps

### Tech Stack Quick Reference

| Need | Recommended | Why |
|---|---|---|
| Fast prototyping | Vite + React + Tailwind | Fast HMR, great DX |
| SEO + SSR | Next.js or Astro | Server rendering |
| Simple interactivity | Alpine.js or vanilla JS | No build step |
| Data-heavy UI | React + Tanstack Table/Query | Purpose-built |
| Real-time | Socket.io or Supabase Realtime | WebSocket abstraction |
| Forms | React Hook Form + Zod | Validation + DX |
| Styling | Tailwind CSS | Utility-first, consistent |
| Component library | shadcn/ui or Radix | Accessible, composable |
| State management | Zustand or Jotai | Simple, performant |
| Backend API | Express, Fastify, or Hono | Lightweight, fast |
| Database | SQLite (local), Postgres (prod), Supabase (managed) | Scale appropriately |

## Phase 3: Project Structure

Always create a clear, navigable file structure. Example for a React app:

```
src/
├── components/          # Reusable UI components
│   ├── ui/              # Base components (Button, Input, Card)
│   └── features/        # Feature-specific components
├── hooks/               # Custom React hooks
├── lib/                 # Utilities, helpers, constants
├── pages/               # Route-level components (if using routing)
├── styles/              # Global styles, CSS variables
├── types/               # TypeScript interfaces/types
└── App.tsx              # Root component
```

For single-file apps, organize with clear comment sections:
```html
<!-- ===== STYLES ===== -->
<!-- ===== MARKUP ===== -->
<!-- ===== SCRIPTS ===== -->
```

## Phase 4: Implementation Principles

### Code Quality Rules
1. **Working first, beautiful second** — Get functionality right, then refine
2. **No placeholder code** — Every function must do something real. No `// TODO` in delivered code
3. **Real data shapes** — Use realistic mock data, not `"Lorem ipsum"` everywhere
4. **Error states matter** — Handle loading, empty, error, and success states
5. **Responsive by default** — Mobile-first CSS. Test at 375px, 768px, 1280px
6. **Accessible** — Semantic HTML, ARIA labels, keyboard navigation, focus management
7. **Type-safe** — Use TypeScript when possible. Define interfaces for data shapes

### Component Design Rules
1. **Single responsibility** — One component, one job
2. **Props over global state** — Pass data down, events up
3. **Composition over inheritance** — Build complex UIs from simple parts
4. **Named exports** — `export function Button()` not `export default`
5. **Co-locate related code** — Keep component, styles, tests, and types together

### CSS / Styling Rules
1. **CSS variables for theming** — Define colors, spacing, fonts as variables
2. **Consistent spacing scale** — Use 4px/8px increments (or Tailwind's scale)
3. **No magic numbers** — Every value should have a reason
4. **Dark mode support** — Use `prefers-color-scheme` or a toggle
5. **Transitions on interactions** — Hover, focus, and active states need smooth transitions

## Phase 5: Iterative Refinement

After the first working version:

1. **Visual polish** — Spacing, alignment, color consistency, typography hierarchy
2. **Interaction polish** — Loading states, transitions, micro-animations, feedback
3. **Edge cases** — Empty states, long text overflow, network errors, rapid clicks
4. **Performance** — Lazy loading, memoization, virtualization for long lists
5. **Accessibility audit** — Tab order, screen reader, color contrast

## Phase 6: Delivery

When presenting the finished app:
- Show the complete, working code
- Explain key architectural decisions briefly
- List what's included and what could be added next
- If multi-file, provide clear setup instructions

## Anti-Patterns to Avoid

- ❌ Jumping straight to code without understanding requirements
- ❌ Over-engineering simple projects (no Redux for a counter app)
- ❌ Generic placeholder content that makes the app feel fake
- ❌ Ignoring mobile layout
- ❌ Using deprecated APIs or outdated patterns
- ❌ Massive monolith components (keep under ~200 lines)
- ❌ Inline styles when a CSS system is available
- ❌ Console.log debugging left in production code
- ❌ Ignoring error boundaries and error handling
- ❌ Copy-pasting without understanding (especially from Stack Overflow / AI output)
