---
name: fix-bug
description: Use when fixing a reported bug, a failing test, a crash or a production error - reproduces first, finds the root cause, makes the minimal fix, adds the regression test, and verifies.
argument-hint: "[issue link, error message, or description]"
---

# Fix a bug

Order matters. Skipping to the fix is how a symptom gets patched and the cause ships again.

## 1. Reproduce (no repro, no fix — testing rule 3)

Get to a **deterministic** reproduction before touching source:

- Exact steps, inputs, environment, user/role, data state.
- Sentry MCP if it is a production error: real stack trace, breadcrumbs, release, affected users, frequency.
- Then encode it as a **failing test** at the level where the bug lives. If you truly cannot express it as a test, write the exact manual repro steps into the PR and say why.

If you cannot reproduce it, stop and report what you tried and what information you need. Do not "fix" a bug you have not seen.

## 2. Find the root cause

- Read the failing path; use Serena to trace the call chain rather than guessing.
- Form a hypothesis, then **prove it** (a log, a breakpoint, a narrowed test) before editing.
- Ask "why did this pass review and CI?" — the answer usually reveals a missing rule or a missing test level, which is worth more than the fix.
- Two failed hypotheses in a row = stop and report (rule F2). Do not shotgun changes.

State the cause in one sentence before you write the fix. If you cannot, you have not found it yet.

## 3. Minimal fix

- Fix the cause, not the symptom. A `try/catch` around a `TypeError` is not a fix.
- Smallest change that makes the failing test pass. No refactor riding along (rule C1) — file it separately.
- If the correct fix is out of scope, stop and report (rule B4). Do not paper over it.

## 4. Prove it and prevent it

- The regression test now passes, and it **failed before** — show both.
- Run the full affected test scope; a fix that breaks a neighbour is not a fix.
- **Execute** the real path (rule B1): the request, the page, the screen.
- Check for siblings: grep for the same wrong pattern elsewhere. Report them, fix only if trivially in scope.
- Ask whether this class of bug can be made impossible: a type, a lint rule, a hook, a DB constraint (rule P1 escalation ladder). Propose it in the PR — this is how a fix stops recurring.

## 5. Report

```markdown
### Root cause
<one sentence>

### Why it was not caught
<missing test level / rule / type>

### Fix
<the minimal change>

### Prevention
<the mechanical guard proposed or added>
```

## Definition of done
- [ ] Deterministic repro, encoded as a test that failed before the fix
- [ ] Root cause stated in one sentence, proven not guessed
- [ ] Minimal fix; no unrelated changes
- [ ] Affected tests green, real path executed, evidence captured
- [ ] Siblings searched for; prevention proposed
