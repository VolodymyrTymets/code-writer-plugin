---
name: feature
description: Take a ticket through the whole lifecycle in one command - plan, human approval, the analyze gate in a fresh context, implementation with per-requirement gates, self-review and a draft PR. Use when a human wants the full flow rather than driving each stage themselves.
argument-hint: "[TICKET-ID]"
disable-model-invocation: true
---

# Feature, end to end

A **thin orchestrator**. Each stage's real instructions live in its own skill, and you invoke them —
do not restate their content here. That matters mechanically: on compaction only the first ~5k tokens of
each recently invoked skill are re-attached, so a fat wrapper loses the detail it duplicated. If a stage's
content seems to have faded after compaction, **re-invoke that stage's skill** rather than working from memory.

You are also not allowed to shortcut the approval. The `guard-plan-approval` hook will block writes to code
until the plan carries a signature, so skipping stage 2 does not save time — it just produces a blocked turn.

## Stage 1 — Plan

Invoke `/plan <TICKET>`. It reads the code and docs first, asks at most two rounds of genuine questions, and
writes `docs/features/<TICKET>/spec.md` and `plan.md`.

## Stage 2 — Human approval (the point of this command)

Present, in at most 12 lines: the goal in one sentence, the ordered requirements, the **three biggest risks**,
and what is explicitly out of scope. Then call **`AskUserQuestion`** with three options:

- **Approve** — proceed to the gate
- **Change** — they say what to change; edit the plan and ask again
- **Cancel** — stop, leave the plan on disk

Never summarise the plan as "looks good, proceed?" — a question that invites a rubber stamp defeats the
stage. Show the risks and the out-of-scope list, because those are what a human catches and you do not.

On approval, write the signature into the plan file, which is what unblocks the hook:

```
Approved-by: <name> · <YYYY-MM-DD>
```

## Stage 3 — Analyze gate, in a fresh context

Invoke `/analyze` with the plan path. It **is** a fork — `context: fork` with a read-only gate agent is in its own
frontmatter, so you get the fresh reader whether or not you remember to ask for one, and it cannot quietly edit the
plan it is judging. The context that wrote the plan is the worst judge of it; this is why the gate reads only what is
on disk.

A BLOCK verdict returns you to stage 2 — fix the **plan**, never the constitution, then re-approve. Two
BLOCK rounds on the same plan means stop and hand it to a human (rule F2).

## Stage 4 — Implement

Invoke `/implement <TICKET>`. It works one requirement at a time with a gate after each, writes tests and
docs, and opens the **draft** PR as its last stage. Do not re-plan here; the plan is settled.

## Stage 5 — Self-review

Invoke `/review-pr`. Fix everything blocking before a human is asked to look.

## Stage 6 — Hand over

Report in at most 8 lines: what shipped, the evidence, what is **not** verified, and what needs a decision.
The PR stays a draft — a human marks it ready (rule A4).

## Definition of done
- [ ] Plan written and **approved by a human**, with the signature in the plan file
- [ ] `/analyze` passed (it runs forked and read-only; the verdict names the plan file it read)
- [ ] Every requirement implemented and gated; nothing weakened to pass (rule B3)
- [ ] Change executed and evidence captured (rule B1)
- [ ] `/review-pr` run and its blocking findings fixed
- [ ] Draft PR open; a human decides it is ready
