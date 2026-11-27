# Brownfield convention discovery

Goal: derive the constitution from **this** codebase, so the agent works the way the repo already works from day one. You are documenting tribal knowledge, not grading the code.

## 1. Sample deliberately (not exhaustively)

Per deployable unit or area, read 5–10 **representative** files:
- the newest non-trivial feature (current conventions) and one older one (legacy conventions — note the difference)
- one file of each recurring kind the repo has: boundary handler, business logic unit, data access, view/component, test, background job
- the config surface: which lint rules are already enabled, how strict the compiler/analyser is, CI steps, git hooks

Use Serena/grep for shape questions ("how do we do error handling?") instead of reading directories.

## 2. Look for four signals only

| Signal | Meaning | Example |
|--------|---------|---------|
| **Consistent** | done the same way in 5+ places → a real convention | every unit of business logic returns a result object instead of throwing |
| **Opinionated** | a deliberate choice against the framework default | no re-export index files anywhere |
| **Unusual** | surprising to an outsider; will be "fixed" by mistake | request objects live beside their handler, not in a shared folder |
| **Tribal** | knowledge that exists only in people's heads | "never touch `legacy/billing` — it is reconciled nightly" |

Ignore: formatting (the formatter owns it), personal style noise, and anything an existing lint rule already enforces — that rule is already mechanical, so writing it down again only costs tokens.

## 3. Ask why, per candidate (batched)

For each candidate, present: what you observed, where (2–3 paths), and your draft rule in one sentence. Ask "is this intentional?" The human answers one of:

- **confirm** → goes into `CLAUDE.md` (if universal) or `.claude/rules/*` (if area-specific)
- **edit** → they correct the wording; use theirs verbatim
- **skip** → it is accidental, or being migrated away from; do not encode it
- **legacy** → record it as "existing code does X, new code does Y", with the boundary path

Aim for 10–20 confirmed rules, not 60. A rule that is not real will be violated and teach the agent that rules are optional.

## 4. Special things to hunt for explicitly

- **No-touch zones**: generated code, vendored code, legacy modules, anything with an out-of-band process → straight into `protected-paths.md`, under a `### Never write` heading
- **The real command map**, including the undocumented step everyone knows ("you must re-run the generator after touching the schema")
- **Local environment gotchas** → `RUNBOOK.md`
- **Decisions visible in the code** (persistence layer, state management, auth approach, repo tooling) → ADRs marked "recorded retroactively on <date>, not re-litigated"
- **Known landmines**: the flaky test, the endpoint that a client polls

## 5. Report

```markdown
## Discovery summary
- areas sampled: <unit A> (8 files), <unit B> (6), <unit C> (5)
- confirmed conventions: 14 (7 → CLAUDE.md, 7 → .claude/rules/)
- no-touch zones: 4 → protected-paths.md
- decisions recorded retroactively: 5 ADRs
- skipped candidates: 9 (accidental or already linted)
- open questions for the team: 2
```
