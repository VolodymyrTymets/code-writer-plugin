---
name: write-docs
description: Use when a change touches documentation, or at the documentation phase of a feature - places each doc type correctly, keeps docs in the same PR as the code, and writes ADRs for settled decisions.
argument-hint: "[feature, decision, or doc path]"
---

# Write docs

Rule E1: docs update **in the same PR as the code**, or the PR is incomplete. Rule E2: a stale doc found while working is a bug — fix it here or file it in the PR body. The agent believes docs, so a wrong doc is worse than a missing one.

## Placement (write it where its question lives)

| What you learned or changed | Goes to |
|-----------------------------|---------|
| Where code lives, how data flows, which environment does what | `docs/ARCHITECTURE.md` |
| Why the product exists, ranked goals, non-negotiables, out-of-scope | `docs/BUSINESS_MODEL.md` |
| A domain term with exactly one meaning | `docs/DOMAIN_GLOSSARY.md` |
| A decision now settled, with rejected alternatives | `docs/decisions/ADR-NNN-<slug>.md` |
| Scope and acceptance criteria of one feature | `docs/features/<TICKET>/spec.md` |
| How to run, seed, build, release; failure modes | `docs/RUNBOOK.md` |
| Which MCP servers this repo uses and what they may reach | `docs/AGENT_TOOLING.md` |
| An always-true rule for this repo | `CLAUDE.md` (short) or `.claude/rules/*.md` |
| A procedure | a skill, not a doc |

If a doc would repeat what the code says, do not write it. Document **why**, constraints, and structure — those are what the code cannot say.

## ADRs

One decision per file, using @references/adr-template.md. Write one when: a new pattern was introduced, a library was chosen, a layering rule was bent, or a tempting alternative was rejected for a non-obvious reason. Never delete an ADR — supersede it with a new one that links back.

## Updating vs appending

Prefer editing the section that is now wrong over appending a "Update 2026-08" note. Docs with a changelog inside them rot fastest. Date only what is genuinely time-bound (a deprecation, a migration window).

## Glossary discipline

One meaning per term. If the client says "booking" and the code says `Reservation`, the glossary maps them and the code stops drifting. New user-facing noun in the UI = a glossary line in the same PR.

## Definition of done
- [ ] Each fact placed in the file whose question it answers
- [ ] Feature spec acceptance criteria ticked to match reality
- [ ] Glossary updated for new domain terms
- [ ] ADR written if a decision was settled
- [ ] No contradiction left between two docs (grep the term you changed)
- [ ] Everything in this same PR (rule E1)
