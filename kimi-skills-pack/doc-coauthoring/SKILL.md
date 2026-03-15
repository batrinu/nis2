---
name: doc-coauthoring
description: >
  Structured workflow for co-authoring documentation, proposals, technical specs, decision docs,
  RFCs, PRDs, and similar structured content. Use when the user wants to write documentation,
  create proposals, draft specs, write technical docs, or any substantial writing task.
  Trigger when user mentions writing docs, creating proposals, drafting specs, "write a doc",
  "draft a proposal", "create a spec", "PRD", "design doc", "decision doc", or "RFC".
  Guides through context gathering, iterative refinement, and reader testing.
---

# Doc Co-Authoring Workflow

A structured 3-stage workflow for creating documentation that actually works for readers.

## When to Use

- Writing technical specs, PRDs, design docs, decision docs, RFCs
- Creating proposals or reports
- Any substantial writing task (more than a quick paragraph)
- When the user seems to have a lot of context in their head that needs to get on paper

## The Three Stages

1. **Context Gathering** — Get everything out of the user's head
2. **Refinement & Structure** — Build section by section through brainstorming and editing
3. **Reader Testing** — Test the doc with a fresh perspective to catch blind spots

## Stage 1: Context Gathering

**Goal:** Close the knowledge gap. The user knows 10x more than you about this topic.

### Step 1: Ask Meta Questions

Start with 5 questions about the document itself:

1. What type of document is this? (spec, decision doc, proposal, etc.)
2. Who's the primary audience?
3. What should the reader DO or FEEL after reading this?
4. Is there a template or format to follow?
5. Any constraints or deadlines?

Tell the user they can answer in shorthand — efficiency matters.

### Step 2: Encourage Info Dumping

Ask the user to dump everything they know. Suggest areas:
- Background on the project/problem
- Why alternative solutions were rejected
- Team context (dynamics, past incidents, politics)
- Technical architecture or dependencies
- Timeline pressures
- Stakeholder concerns

Tell them: **Don't worry about organizing it. Just get it all out.**

### Step 3: Ask Clarifying Questions

After the info dump, generate 5-10 specific clarifying questions based on gaps.

Allow shorthand answers: "1: yes, 2: no because backwards compat, 3: ask Sarah"

### Exit Condition

You're ready to move on when your questions show understanding — when you can ask about edge cases and trade-offs without needing basics explained.

## Stage 2: Refinement & Structure

**Goal:** Build the document section by section through brainstorming, curation, and iteration.

### Propose Structure

If the user doesn't have a template, suggest 3-5 sections appropriate for the doc type:

**Decision Doc:** Problem → Context → Options → Recommendation → Next Steps
**Technical Spec:** Overview → Architecture → API Design → Data Model → Migration → Risks
**PRD:** Problem → Users → Requirements → Success Metrics → Timeline → Open Questions
**Proposal:** Executive Summary → Problem → Solution → Cost/Benefit → Implementation Plan

### For Each Section

1. **Clarify** — Ask 3-5 questions about what should go in this section
2. **Brainstorm** — Generate 5-20 candidate points to include
3. **Curate** — User picks what to keep, remove, or combine (e.g., "Keep 1,4,7. Remove 3. Combine 11+12")
4. **Gap check** — Ask if anything important is missing
5. **Draft** — Write the section based on selections
6. **Refine** — Make surgical edits based on user feedback (never reprint the whole doc)

**Key instruction for the user:** "Instead of editing the doc directly, tell me what to change. This helps me learn your style for future sections."

### Near Completion

When 80%+ of sections are done, re-read the entire document and check for:
- Flow and consistency across sections
- Redundancy or contradictions
- Generic filler that doesn't carry weight
- Whether every sentence earns its place

## Stage 3: Reader Testing

**Goal:** Verify the doc works for someone with zero context.

### Step 1: Predict Questions

Generate 5-10 questions a reader would realistically ask when encountering this document.

### Step 2: Test

**If you can spawn a sub-agent / fresh context:**
Test each question with a fresh instance that only has the document (no conversation history).

**If you can't:**
Ask the user to:
1. Open a fresh conversation
2. Paste the document
3. Ask the generated questions
4. Report what the fresh AI got wrong or struggled with

### Step 3: Additional Checks

Also test for:
- Ambiguity or unclear language
- Assumed knowledge that isn't stated
- Internal contradictions

### Step 4: Fix

For every issue found, loop back to Stage 2 to fix the problematic sections.

### Exit Condition

The doc is ready when a fresh reader (human or AI) can consistently answer questions correctly without surfacing new gaps.

## Final Handoff

When complete:
1. Recommend the user do a final read-through themselves
2. Suggest double-checking facts, links, and technical details
3. Remind them to update the doc as real reader feedback arrives
4. Offer to create an appendix with decision rationale or context

## Process Tips

- **Be direct** — Procedural tone, not salesy
- **Handle deviations** — If user wants to skip a stage, let them
- **Address gaps immediately** — Don't let missing context accumulate
- **Quality over speed** — Each iteration should make meaningful improvements
- **Never dump the whole doc** — Use targeted edits, not full rewrites
