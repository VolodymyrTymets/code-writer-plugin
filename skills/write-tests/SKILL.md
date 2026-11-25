---
name: write-tests
description: Use when writing or fixing tests, or when a change needs coverage - picks the right test level, the right mocking boundary, and keeps tests deterministic. Language- and framework-neutral.
argument-hint: "[file or feature to cover]"
---

# Write tests

Read `.claude/rules/testing.md` first; this skill is the procedure, that file is the law. Runner flags and
framework helpers come from the stack testing rules installed beside it (`.claude/rules/testing-*.md`, for
example `testing-python.md`) and from the existing tests — follow them, do not invent a second style.

## 1. Pick the level (then write one test, not three)

| The thing that can break | Level |
|--------------------------|-------|
| A calculation, a mapper, a validation rule | unit — no mocks needed |
| A business rule that orchestrates several pieces | unit with the data layer substituted |
| The contract at a boundary: status codes, payload shape, authorization | integration against real infrastructure (disposable database, real router) |
| A user-visible behaviour of a component or screen | component test driven the way a user drives it |
| A journey across screens or services | end to end |
| A regression | the level where the bug actually lived |

If you cannot name what would break, do not write the test.

## 2. Find the existing pattern before writing

Read two or three neighbouring tests. Match their structure, their helpers, their factory usage and their
naming. A test written in a second style is a maintenance tax even when it passes.

## 3. Mocking boundary

Substitute: the network edge, the clock, randomness, IDs, third-party services, notifications, payments.
Do not substitute: your own data layer in an integration test, the framework, the router, or the thing under test.

## 4. Determinism

Fixed clock, seeded data, explicit ordering independence, no shared mutable state, no sleeps — wait for a
condition. If the test only passes on your machine, it is not a test yet.

## 5. Cover the paths that actually fail

- The failure path, not only the happy one.
- Boundaries: empty, one, many, maximum, null/absent, duplicate.
- Authorization: the wrong user, the missing role, the expired session.
- Concurrency where the code allows two writers.

## 6. Assertions

Assert on observable behaviour and public contracts, never on internal structure. The failure message must
identify the cause without a debugger — assert on values, not booleans.

## Definition of done
- [ ] Level chosen, with one line saying why
- [ ] Existing test patterns followed
- [ ] Failure path and boundaries covered, not just the happy path
- [ ] Deterministic: no sleeps, no unseeded randomness, no order dependence
- [ ] Test command from the command map run and green, with the real output captured
- [ ] Nothing skipped, `.only`-ed or weakened to pass (rule B3)
