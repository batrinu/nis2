---
name: project-planning
description: >
  Break any project into atomic, executable implementation tasks with verification steps.
  Use when the user asks to "break this down", "create a plan", "what are the steps",
  "help me organize this", "task breakdown", "implementation plan", "roadmap", or when
  facing a complex project that needs structure before coding begins. Also use when the
  user seems overwhelmed by scope or when a previous attempt failed due to lack of planning.
---

# Project Planning: Atomic Task Decomposition

Turn any project idea into a clear, ordered list of small tasks that can be executed one at a time with confidence.

## The Golden Rule

Every task must be:
- **Atomic** — Does exactly one thing
- **Verifiable** — Has a concrete "done" check
- **Independent** — Can be understood without reading other tasks
- **Time-boxed** — Completable in 2-10 minutes
- **Specific** — Includes exact file paths, function names, or commands

## Task Template

```
### Task [N]: [Brief title]

**Files:** [exact paths to create or modify]
**Do:**
  - [Specific action 1]
  - [Specific action 2]
**Verify:**
  - [Concrete check: "renders X", "returns Y", "test passes"]
**Depends on:** Task [M] (if applicable)
```

## Decomposition Process

### Step 1: Identify the Layers

For a web app, typical layers are:
1. **Data layer** — Types/interfaces, database schema, API contracts
2. **Logic layer** — Business logic, hooks, utilities, state management
3. **UI layer** — Components, pages, layouts, styles
4. **Integration layer** — API calls, auth, external services
5. **Polish layer** — Animations, error handling, loading states, accessibility

### Step 2: Order by Dependencies

Build bottom-up:
```
Data types → Business logic → Base UI → Feature UI → Integration → Polish
```

### Step 3: Group into Batches

Batches are natural checkpoint points where you can demo progress:
- **Batch 1: Foundation** — Project setup, types, base components
- **Batch 2: Core** — Main feature(s) working with mock data
- **Batch 3: Integration** — Real data, API connections, auth
- **Batch 4: Polish** — Error handling, loading states, animations
- **Batch 5: Ship** — Testing, optimization, deployment

### Step 4: Write Verification Steps

Bad: "Works correctly"
Good: "Clicking the Submit button shows a success toast and clears the form"

Bad: "API is set up"
Good: "GET /api/tasks returns JSON array with status 200"

Bad: "Component renders"
Good: "TaskCard shows title, due date, and priority badge. Checkbox toggles strikethrough on title."

## Estimation Guide

| Task Type | Typical Time |
|---|---|
| Create a TypeScript interface file | 2 min |
| Build a simple component (Button, Card) | 3-5 min |
| Build a complex component (Form, Table) | 5-10 min |
| Add a custom hook | 3-5 min |
| Set up routing (3-5 routes) | 5-8 min |
| API integration for one endpoint | 5-8 min |
| Add animations to a component | 3-5 min |
| Write tests for a component | 5-10 min |

If a task takes more than 10 minutes, it should be split.

## Example: Todo App Plan

```
## Batch 1: Foundation (15 min)

Task 1: Create project structure
  Files: src/types/, src/components/, src/hooks/, src/lib/
  Do: Create directory structure
  Verify: All directories exist

Task 2: Define data types
  Files: src/types/todo.ts
  Do: Create TodoItem interface (id, title, completed, createdAt, priority)
  Verify: File exists, types compile without errors

Task 3: Build base layout
  Files: src/App.tsx, src/styles/globals.css
  Do: Create app shell with header, main content area, CSS variables
  Verify: App renders with header showing "My Todos"

## Batch 2: Core Features (25 min)

Task 4: Build TodoItem component
  Files: src/components/TodoItem.tsx
  Do: Render title, checkbox, delete button. Accept onToggle, onDelete props.
  Verify: Renders with mock data, checkbox toggles visual state

Task 5: Build TodoList component
  Files: src/components/TodoList.tsx
  Do: Map over array of todos, render TodoItem for each, show empty state
  Verify: Shows list of 3 mock todos, shows "No todos yet" when empty

Task 6: Build AddTodo form
  Files: src/components/AddTodo.tsx
  Do: Input + button. On submit, calls onAdd with title, clears input.
  Verify: Typing + Enter adds todo, input clears after submit

Task 7: Wire up state management
  Files: src/hooks/useTodos.ts, update src/App.tsx
  Do: Custom hook with add, toggle, delete. Use useState. Wire to components.
  Verify: Can add, check off, and delete todos. State persists during session.

## Batch 3: Polish (15 min)

Task 8: Add priority support
  Files: Update TodoItem, AddTodo, useTodos
  Do: Priority selector (low/medium/high), colored badges, sort by priority
  Verify: Can set priority, badge shows correct color, list sorted

Task 9: Add animations
  Files: src/styles/globals.css, update TodoItem
  Do: Fade-in on new todo, slide-out on delete, checkbox transition
  Verify: Adding/removing todos is visually smooth

Task 10: Add localStorage persistence
  Files: Update useTodos.ts
  Do: Save to localStorage on change, load on mount
  Verify: Refresh page, todos still there
```

## When NOT to Plan

- One-line bug fixes
- Simple text or style changes
- Questions that need answers, not code
- Exploratory prototyping (plan after the prototype)

For everything else: plan first, code second.
