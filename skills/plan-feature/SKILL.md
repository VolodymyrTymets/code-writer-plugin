---
name: plan
description: Use when starting work on a new feature, story or ticket, before writing any code. Reads the codebase and docs first, asks only genuine gaps, and produces a spec plus an implementation plan that must pass the `/analyze` gate.
argument-hint: "[TICKET-ID or a short description]"
---

# Plan a feature

You are producing two artefacts and then **stopping for a human go-ahead**. You are not implementing anything in this skill.

## Step 1 — Read before you ask (rule D1, F1)

Work through @references/discovery-checklist.md silently, in one pass, before your first question: the ranked goals, the architecture, the glossary, the settled decisions, the ticket, then **the nearest existing implementation of the same shape** and the tests around it.

Report in two or three lines what pattern you are going to follow and where it lives. If you cannot find a precedent, say so explicitly — that is a signal the change needs an ADR.

## Step 2 — Ask only genuine gaps (max two rounds, rule F1)

A question is worth asking only if the answer changes the plan **and** you cannot get it from the code, the docs or the ticket. Batch them. Prefer a decision with a stated assumption over a question.

@references/question-quality.md has the test, the shapes that pass it and the ones that do not, and the form a batched round takes.

## Step 3 — Write the spec

`docs/features/<TICKET>/spec.md` using @references/plan-template.md (spec part): problem, scope, acceptance criteria as a checklist, edge cases, **explicit out-of-scope**, open questions with your assumed answer.

## Step 4 — Write the plan

`docs/features/<TICKET>/plan.md` using @references/plan-template.md (plan part). Requirements:

- **Ordered requirements**, each independently verifiable and small enough to land in one commit. This ordering is what `develop-feature` iterates over.
- Per requirement: the files to add/change (real paths), the layer each touches, the test that proves it, and how it will be **executed** for verification (endpoint call / page / screen).
- Contract changes called out separately (public interfaces, shared types, persisted formats) — these have knock-on effects for other consumers.
- Risks and unknowns, with the cheapest experiment that removes each one.
- Docs to update in the same PR (rule E1).
- An estimate in complexity terms (S/M/L per requirement), not hours.

Keep it under 150 lines. A plan nobody reads is not a plan.

## Step 5 — Gate and stop

Run `/analyze` on your own plan, passing the plan path. It runs forked and read-only by construction, so the context that just wrote the plan is not the one judging it — which also means anything you decided in this conversation but did not write down will not be seen. Fix what it blocks — **change the plan, never the constitution**. Then present a summary (≤10 lines: goal, ordered requirements, the three biggest risks, what is out of scope) and **wait for an explicit go-ahead**. Do not start implementing, do not create branches, do not scaffold files.

The go-ahead is not a chat message — a human writes `Approved-by: <name> · <date>` into the plan file. `guard-plan-approval` blocks writes to code until that line exists, so an unapproved plan cannot quietly become an implementation.

## Definition of done for this skill

- [ ] `spec.md` and `plan.md` written, with acceptance criteria as a checklist
- [ ] The precedent pattern named, with a path
- [ ] `analyze-plan` passed (or its blocks listed and resolved in the plan)
- [ ] Assumptions stated explicitly
- [ ] Waiting for go-ahead, nothing implemented
