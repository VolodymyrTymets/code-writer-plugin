# Templates

## spec.md

```markdown
# <TICKET> — <title>

## Problem
<what the user cannot do today, in the domain language of DOMAIN_GLOSSARY.md>

## Goal / business value
<which ranked goal from BUSINESS_MODEL.md this serves>

## Scope
- in: ...
- **out (explicit):** ...

## Acceptance criteria
- [ ] AC1 Given ... when ... then ...
- [ ] AC2 ...

## Edge cases
| Case | Expected behaviour | Decided by |
|------|--------------------|-----------|

## Open questions
| # | Question | My assumed answer | Needs a human? |
|---|----------|-------------------|----------------|
```

## plan.md

```markdown
# <TICKET> — implementation plan

<!-- A human writes this line to approve. Until it is here, guard-plan-approval blocks writes to code.
     A deliberate exception is written the same way, with its reason:
     Approved-by: spike, no review — <TICKET> -->
Approved-by:

Pattern followed: `<path/to/precedent>` (<why it is the right precedent>)

## Contract changes
- boundary: <endpoint / message / CLI surface, additive or breaking, which consumers>
- data: <persisted data or file-format change, how existing data is handled, rollback>
- generated output: <what is regenerated, with which command>

## Requirements (ordered, each independently verifiable)

### R1 — <title> (S/M/L)
- files: `<path>` (new), `<path>` (change: ...)
- layer: <the layer this repo uses for this kind of code>
- test: `<test path>` — <what it asserts>
- executed how: <the real call, page or run that proves it — see the gates reference for what counts>
- risk: <none | ...>

### R2 — ...

## Docs to update in this PR
- [ ] docs/features/<TICKET>/spec.md (acceptance criteria checked off)
- [ ] docs/ARCHITECTURE.md — <only if structure changed>
- [ ] docs/DOMAIN_GLOSSARY.md — <new terms>
- [ ] docs/decisions/ADR-NNN — <only if a new pattern was chosen>

## Risks
| Risk | Impact | Cheapest way to find out early |
|------|--------|-------------------------------|

## Assumptions
- ...
```
