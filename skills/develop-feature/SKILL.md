---
name: implement
description: Use when implementing a planned feature or ticket end to end. Orchestrates the flow - plan, analyze gate, one requirement at a time with a quality gate after each, tests, docs, and a draft PR with an evidence block.
argument-hint: "[TICKET-ID]"
---

# Develop a feature

You are the orchestrator. Work **one requirement at a time**, and never move to the next one until the current one is green. Context minimalism: delegate noisy work (builds, test runs, review) to subagents so their output does not fill your context.

## Phase 0 — Preconditions

1. A plan exists at `docs/features/<TICKET>/plan.md`. If not, run `/plan` first and stop for go-ahead.
2. The plan passed `/analyze`. If not, run it now, passing the plan path — it runs forked and read-only, so it sees only what the plan file says. **A BLOCK verdict stops you here.**
3. The plan carries `Approved-by:`. If not, stop and get approval — the `guard-plan-approval` hook blocks every write to code until it does, so starting anyway only burns a turn.
4. You are on a feature branch: `git switch -c feat/<TICKET>-<slug>` (rule A1 — the hook will block you on a protected branch).
5. Dependencies installed, correct runtime version (the session briefing tells you).

## Phase 1 — Implement requirement N

For each requirement in plan order:

1. **Re-read the precedent** named in the plan. Follow it; do not improvise a second pattern (rule D2).
2. Implement **only** requirement N (rule C1). No drive-by changes, no renames outside it.
3. Write the test named in the plan, in the same step — not "later" (rule B1).
4. Run the per-requirement gate below. Loop until green. Never weaken a check to pass it (rule B3).

### Per-requirement quality gate

| Check | How | On failure |
|-------|-----|-----------|
| lint | the repo lint command | fix, re-run — never disable the rule |
| tests | `@test-runner` with the affected scope | fix the code; if the test was wrong, say why in the PR |
| **execute** | call the endpoint / open the page / launch the screen (see @references/gates.md per stack) | fix, re-run |
| scope | `git diff --stat` — does the diff match requirement N only? | revert the extras |

Record the real command output as you go; you need it for the evidence block, and the Stop hook will hold you until it exists.

5. Commit requirement N: Conventional Commits with the ticket ID (rule A5).

## Phase 2 — Cross-cutting passes (once, after the last requirement)

1. **Contracts:** if a boundary or schema changed, regenerate whatever is generated from it (never hand-edit the output), then update every consumer you can find by search — in this PR.
2. **Docs (rule E1):** run `write-docs` — feature spec ticked off, `ARCHITECTURE.md` if structure moved, glossary for new terms, ADR if a new pattern was chosen.
3. **Self-review:** run `/review-pr`. Fix what it finds before a human sees the PR.
4. Optional: `@code-simplifier` for a behaviour-preserving cleanup of what you just wrote.

## Phase 3 — Draft PR

1. Push the branch.
2. Open a **draft** PR using @references/pr-template.md, including the full evidence block from @references/evidence-format.md.
3. Report to the human: what is done, what is unverified, what needs a decision. **Never mark the PR ready, never merge, never approve** (rule A4 — the hook blocks it anyway).

## When you get stuck

Two failed attempts at the same problem = stop and report (rule F2). State what you tried, your hypotheses, and the decision you need. Do not keep changing things hoping one sticks — that is how a 20-file diff appears for a 3-line bug.

## Definition of done
- [ ] Every requirement implemented, gated and committed separately
- [ ] Lint, affected tests green — none of them weakened
- [ ] Change **executed** with captured evidence for each requirement
- [ ] Docs updated in this PR
- [ ] `review-pr` run and its findings addressed
- [ ] Draft PR open with the evidence block; a human, not you, decides it is ready
