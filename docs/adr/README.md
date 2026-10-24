# Architecture Decision Records (ADR)

This folder holds Architecture Decision Records for ArterIA: short documents that capture a significant, hard-to-reverse decision, the context behind it, and its consequences.

## When to write one

Write an ADR when a decision would be costly to revisit later, for example:

- Choice of traffic simulator (SUMO vs. MATSim vs. AIMSUN, etc.).
- Choice of optimization architecture (bi-level, surrogate model, RL framework).
- City-agnostic project structure and how a new city plugs in.
- Data formats or schemas shared across cities.

Don't write one for routine implementation details or easily reversible choices.

## Format

Use sequential numbering: `0001-title-in-kebab-case.md`, `0002-...`.

Suggested structure:

```markdown
# 000N. Title

Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded by 000M

## Context

What is the issue, and what forces (technical, data availability, team, time) are at play?

## Decision

What did we decide?

## Consequences

What becomes easier or harder as a result? What are the trade-offs and risks?
```
