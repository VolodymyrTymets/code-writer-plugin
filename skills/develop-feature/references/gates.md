# Per-requirement gates

The gate is the same everywhere; only the "execute" step changes with the **kind of change**, not with the
framework. Use the commands from the command map in `CLAUDE.md` — never invent a script name. A step whose
map entry is `none` is skipped.

```
<lint>  →  <affected tests>  →  EXECUTE  →  scope check (git diff --stat)
```

## What counts as "executed" (rule B1)

| Kind of change | Execute it by | Evidence to capture |
|----------------|---------------|---------------------|
| HTTP / RPC endpoint | calling it for real — happy path **and** the main failure path | request, status, response body for both |
| UI screen or page | opening it and performing the interaction | screenshot per state (success, empty, error), console/log clean |
| Background job, queue consumer, scheduled task | triggering it with a real payload | input, log output, resulting state change |
| CLI or script | running it | command, output, exit code |
| Persisted data or file-format change | running it locally against real data and reading the result back | the before/after output, rollback note |
| Library / shared package | exercising it from a real consumer, not only its own tests | the consumer call and its result |
| Config / infrastructure file | the pipeline or process that consumes it actually parsing it | the run that proves it loads |
| Pure refactor | the characterisation tests that passed before and after | both runs, plus "no behaviour change intended" |

## Observations that belong in every gate

- The **failure path**, not only the happy path. A requirement verified only on success is half verified.
- The **log or console**: new warnings and unhandled rejections count as findings, not noise.
- **Scope**: `git diff --stat` should contain only what this requirement needed (rule C1).

## What does not count as verification

- "It lints clean" for a behaviour change.
- A unit test with every boundary mocked, for an integration requirement.
- An isolated component harness instead of the real screen.
- Re-reading your own diff.
- "It should work" (rule B2).

Framework-specific commands and device automation live in this repo's stack pack.
