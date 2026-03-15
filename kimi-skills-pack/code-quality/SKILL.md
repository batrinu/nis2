---
name: code-quality
description: >
  Test-driven development, systematic debugging, and code verification practices.
  Use this skill when the user asks to "add tests", "write tests", "debug this",
  "fix this bug", "why isn't this working", "code review", "improve code quality",
  "refactor", "clean up this code", or when encountering any bug, test failure,
  or unexpected behavior. Also trigger when delivering finished code to ensure
  quality checks are performed before handoff.
---

# Code Quality: TDD, Debugging & Verification

## Test-Driven Development (TDD)

### The Red-Green-Refactor Cycle

1. **RED** — Write a failing test that describes the desired behavior
2. **GREEN** — Write the minimum code to make the test pass
3. **REFACTOR** — Clean up while keeping tests green

### When to Write Tests

- **Always** for business logic, utilities, and data transformations
- **Always** for API endpoints and data fetching
- **Recommended** for complex components with state
- **Optional** for simple presentational components
- **Skip** for prototype/exploration code (but add before shipping)

### Test Structure (Arrange-Act-Assert)

```typescript
describe('TodoService', () => {
  it('should add a new todo with correct defaults', () => {
    // Arrange
    const service = new TodoService();
    
    // Act
    const todo = service.add('Buy groceries');
    
    // Assert
    expect(todo.title).toBe('Buy groceries');
    expect(todo.completed).toBe(false);
    expect(todo.id).toBeDefined();
  });
});
```

### Testing Anti-Patterns to Avoid

- ❌ Testing implementation details (internal state, private methods)
- ❌ Tests that break when you refactor (test behavior, not structure)
- ❌ Tests with no assertions
- ❌ Tests that depend on execution order
- ❌ Mocking everything (test real behavior when possible)
- ❌ Testing library/framework code instead of your code
- ❌ Snapshot tests as the only test type
- ❌ Tests that pass when the code is broken

### Good Tests Are

- **Behavioral** — Test what the code does, not how it does it
- **Predictive** — They fail when something actually breaks
- **Specific** — A failing test tells you exactly what's wrong
- **Fast** — Unit tests should run in milliseconds
- **Independent** — No shared state between tests
- **Deterministic** — Same result every time

## Systematic Debugging

### The 4-Phase Process

When encountering a bug, do NOT immediately start changing code. Follow this process:

#### Phase 1: Reproduce
- Can you reliably trigger the bug?
- What are the exact steps?
- What's the expected behavior vs actual behavior?
- Does it happen consistently or intermittently?

#### Phase 2: Isolate
- Where does the incorrect behavior originate?
- Binary search: comment out half the code. Still broken? The bug is in the remaining half.
- Check the data flow: is the input correct? Is the transformation correct? Is the output correct?
- Read error messages carefully — they often tell you exactly what's wrong.

#### Phase 3: Identify Root Cause
- Don't fix the symptom. Find the actual cause.
- Ask "why" five times (the "5 Whys" technique):
  - Why did the page crash? → A null value was accessed
  - Why was it null? → The API returned null for that field
  - Why did the API return null? → The database record was incomplete
  - Why was it incomplete? → The migration didn't set a default
  - Why? → The migration was written without checking existing data
  - **Root cause**: Migration needs a default value for existing records.

#### Phase 4: Fix and Verify
- Write a test that reproduces the bug FIRST
- Apply the fix
- Verify the test now passes
- Check that no other tests broke
- Consider: are there similar bugs elsewhere? (Same pattern, different location)

### Debugging Tools Checklist

- Console logging with structured data: `console.log({ variable, context })`
- Browser DevTools: Network tab, Console, Elements, Performance
- React DevTools: Component tree, state inspection, profiler
- Breakpoints: `debugger` statement or IDE breakpoints
- Git bisect: Find the commit that introduced the bug

## Verification Before Completion

Before declaring any task "done", run this checklist:

### Functional Verification
- [ ] Does it do what was requested?
- [ ] Does it handle empty/null/undefined inputs?
- [ ] Does it handle error cases gracefully?
- [ ] Does it handle edge cases? (very long text, special characters, rapid clicks)
- [ ] Does it work with real data, not just mock data?

### Code Quality Verification
- [ ] No unused imports or dead code
- [ ] No `console.log` left behind (except intentional logging)
- [ ] No `any` types in TypeScript (use proper types)
- [ ] No hardcoded values that should be configurable
- [ ] Functions are under 50 lines
- [ ] Component files are under 200 lines
- [ ] Consistent naming conventions throughout
- [ ] Comments explain "why", not "what"

### UI Verification
- [ ] Responsive: works at 375px, 768px, 1280px
- [ ] Accessible: keyboard navigable, proper ARIA labels
- [ ] Visual: consistent with design system, no layout shifts
- [ ] Interactions: hover/focus/active states, transitions
- [ ] Loading: shows loading state during async operations
- [ ] Error: shows user-friendly error messages

### Performance Verification
- [ ] No unnecessary re-renders (React Profiler)
- [ ] Images are optimized (lazy loading, proper sizing)
- [ ] No blocking API calls on initial render
- [ ] Lists with 100+ items use virtualization
- [ ] Bundle size is reasonable for the feature

## Code Review Mindset

When reviewing code (your own or others'), look for:

1. **Correctness** — Does it actually work?
2. **Clarity** — Can someone else understand this in 30 seconds?
3. **Consistency** — Does it match the codebase's patterns?
4. **Completeness** — Are all cases handled?
5. **Simplicity** — Can it be simpler without losing functionality?

Rate issues by severity:
- 🔴 **Critical** — Blocks shipping. Bugs, security issues, data loss risk.
- 🟡 **Important** — Should fix before shipping. Poor UX, missing error handling.
- 🟢 **Nice to have** — Can ship without. Style nits, minor improvements.
