---
name: review-pr
description: Use before asking a human to review, or when reviewing an existing PR or diff - checks the change against the constitution and stack rules, delegates to the reviewer subagents, and reports findings by severity.
argument-hint: "[PR number, or nothing for the current branch diff]"
---

# Review a PR

Purpose: nothing reaches a human reviewer that our own rules would have caught. This is a self-review before a human's time is spent, not a substitute for their review.

## Step 1 — Get the real diff

```bash
git fetch origin && git diff --stat origin/<base>...HEAD
git diff origin/<base>...HEAD
```
Review the **diff**, not the files. Reviewing whole files invents findings about code nobody touched.

## Step 2 — Delegate

- `@code-reviewer` — the whole diff against the constitution and the applicable `.claude/rules/*`.
- `@security-auditor` — **mandatory** when the diff touches `**/auth/**`, guards, middleware, payments, uploads, file paths, SQL, or anything that renders user input.
- `@ui-reviewer` — when a screen changed and a design reference exists.

Run them in parallel. They have no write tools; you decide what to act on.

## Step 3 — Check what subagents cannot see

- **Scope (C1):** does the diff contain anything the ticket did not ask for? Renames, formatting, version bumps → split them out.
- **Evidence (B1/B2/B5):** is the evidence block real and complete? Does "executed" describe something that actually ran?
- **Bypasses (B3):** grep the added lines for anything that silences a check — type-checker ignores, linter disables, skipped or `.only` tests, bypassed pre-commit, deleted assertions, blindly re-recorded snapshots. Each one needs a human-approved `// WHY:`. (The `bypass-scan` CI job does this too; do not rely on it to catch what you added.)
- **Docs (E1):** are the doc updates the plan promised actually here?
- **Protected paths (C3):** read every `.claude/rules/protected-paths*.md`, then check that nothing landed on a listed path.
- **Contract (backend 8):** OpenAPI, shared types and consumers updated together?
- **Secrets (A6):** any key, token, DSN, or client data in the diff, including test fixtures?

## Step 4 — Report

```markdown
## Self-review: <n> blocking, <n> should-fix, <n> nits

### Blocking
1. [B3] `orders.service:88` — the type checker is silenced with no WHY. Fix: require the field at the boundary and validate it.

### Should fix
1. [stack rule] `orders.repository:41` — a query inside a loop over the items. Fix: one batched query for all identifiers.

### Nits (not blocking)
1. ...

### Reviewer focus
<where a human should look hardest, and why>
```

Fix everything blocking before you hand the PR over. Rank by real impact — twelve nits and no findings is a failed review. If the diff is clean, say so in one line; do not manufacture findings.

## Definition of done
- [ ] Diff-based, not file-based
- [ ] `code-reviewer` run; `security-auditor` run if sensitive paths were touched
- [ ] Blocking findings fixed, with the checks re-run afterwards
- [ ] Findings carry rule IDs and concrete fixes
- [ ] PR still a draft; the human decides it is ready (A4)
