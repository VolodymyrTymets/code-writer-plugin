# {{PROJECT_NAME}} — project constitution

Managed by the `rln-agent` plugin. Hard rules only; depth lives in the pointers at the bottom.
Placeholders are filled by `/setup`. Keep this file under 200 lines — if a rule needs depth, move it
to `.claude/rules/`, `docs/`, or a skill and leave a pointer.

## Command map (the only commands you should run)

| Task | Command |
|------|---------|
| install | `{{CMD_INSTALL}}` |
| lint | `{{CMD_LINT}}` |
| unit tests | `{{CMD_TEST}}` |
| affected tests | `{{CMD_TEST_AFFECTED}}` |
| build | `{{CMD_BUILD}}` |
| dev server | `{{CMD_DEV}}` |
| e2e | `{{CMD_E2E}}` |

`lint` is the static check: when the map holds a real command it is a B1 gate. `none` means the repo has no such task (never invent one). A repo that runs a type checker or a formatter check may add a `typecheck` or `format` row: each is then a gate too.

Dependency manager: **{{DEPENDENCY_MANAGER}}**. Runtime pinned by **{{RUNTIME_VERSION_FILE}}**: **{{RUNTIME_VERSION}}**.

- **T1** Run tasks through the commands above. Never invent a script name, never `cd` and guess.
- **T2** If your local runtime version differs from the pinned one, stop and report — do not work around it.
- **T3** Use the dependency manager this repo declares, and only that one. Never hand-edit or delete a lockfile.
- **T4** CI and pipeline files are changed only in a dedicated PR with a human reviewer.

## A. Git and PR

- **A1** Never commit or push to `{{PROTECTED_BRANCHES}}`. Branch as `feat|fix|chore/<TICKET>-<slug>`.
- **A2** Never `git push --force` to a shared branch; `--force-with-lease` on your own branch only.
- **A3** Never rewrite history that is already pushed and reviewed.
- **A4** One PR = one requirement. Open it as a **draft**. A human marks it ready. You never mark ready, never approve, never merge.
- **A5** Conventional Commits, imperative mood, ticket ID in the subject. No "AI generated" notes, no emoji.
- **A6** Never commit secrets, `.env*`, tokens, keystores, provisioning profiles or client data.
- **A7** The PR body uses the template: what changed, why, how it was verified (commands + output), what is NOT covered.

## B. Definition of done — verification is mandatory

- **B1** A task is done only when, for the affected code: every check the command map has passes, **and the change was executed** — the app, script or service actually run and the changed behaviour exercised. What cannot run here goes under "Not verified".
- **B2** Report the exact commands and their real output. Never claim a result you did not observe. List anything unverified under "Not verified".
- **B3** Never make a check pass by weakening it — no silencing the type checker or linter, no skipping or narrowing tests, no bypassing pre-commit hooks, no deleted assertions, no blind snapshot re-record, no removed CI steps — unless a human approved it in the PR and the line carries `WHY: <reason + ticket>`.
- **B4** If the correct fix is bigger than the ticket, stop and report. Do not paper over it.
- **B5** Attach evidence: screenshot for UI, request/response for API, the failing-then-passing test for a bug fix.

## C. Scope

- **C1** Change only what the requirement needs. No opportunistic refactors, renames, formatting sweeps or version bumps in a feature PR — propose them separately.
- **C2** Never add a runtime dependency without explicit approval. Prefer what the repo already has.
- **C3** Never edit generated, vendored or native build artefacts — see `.claude/rules/protected-paths.md`.
- **C4** Never run a destructive or irreversible command (`rm -rf`, force push, deploy, publish, copying to a device or server) without explicit human confirmation in the same message.
- **C5** Never touch production. Local and staging only, no production hosts or credentials.

## D. Code and context

- **D1** Read before you write: find the existing pattern for what you are building and follow it. A new pattern needs an ADR in `docs/decisions/`.
- **D2** This repo's conventions outrank generic best practice. When they conflict, follow the repo and raise the conflict.
- **D3** No escape hatch out of the type system in new code — no untyped catch-alls, no unchecked casts, no non-null assertions without a `WHY:` comment.
- **D4** Never invent an API. Verify library APIs with Context7 or the installed source; verify business rules in `docs/` or by asking.
- **D5** Errors are never swallowed. No empty `catch`, no silent `return null`.
- **D6** Comments explain *why*. No commented-out code. No `TODO` without a ticket ID.
- **D7** No hardcoded user-facing strings — i18n keys only.{{I18N_NOTE}}
- **D8** No secrets, tokens, PII or full request bodies in logs.

## E. Documentation

- **E1** Docs update in the same PR as the code: the feature spec, `docs/ARCHITECTURE.md` on structural change, `docs/DOMAIN_GLOSSARY.md` on new domain terms, an ADR for a settled decision.
- **E2** A stale doc found while working is a bug: fix it in the same PR or file it in the PR body.

## F. Collaboration

- **F1** When planning, ask only genuine gaps you cannot resolve from code or docs — max two rounds — then proceed and state your assumptions.
- **F2** Escalate to a human when: acceptance criteria conflict with this constitution; a security or auth decision is involved; client data or credentials are involved; the work crosses an architectural boundary or looks like more than a day.
- **F3** State uncertainty plainly. "I am not sure" beats a confident guess.

## G. Data confidentiality (never relaxed)

- **G1** Sensitive data — credentials, personal or patient-related data, recorded user data — never leaves the tools listed in `docs/AGENT_TOOLING.md`.
- **G2** Nothing project-specific is copied into the shared plugin config or another project's repo. Only generic engineering conventions may be promoted, by a human, through a PR to the plugin.
- **G3** Reference files by path instead of pasting sensitive data into a prompt.

## Where things live

- Stack rules: `.claude/rules/` — auto-loaded when you touch a matching path (installed by `/setup` for this repo's stack)
- Architecture: @docs/ARCHITECTURE.md
- Product goals & priorities (tie-breaker for judgement calls): @docs/BUSINESS_MODEL.md
- Domain terms: @docs/DOMAIN_GLOSSARY.md
- Settled decisions: `docs/decisions/`
- Agent tooling & MCP policy: @docs/AGENT_TOOLING.md
- How to run things: @docs/RUNBOOK.md
- Workflow: `/plan` → `/analyze` → `/implement` → `/review-pr`. The draft PR is the last stage of `/implement`, not a separate command.

<!-- PROJECT-SPECIFIC RULES: add below this line, keep each one short and say why. -->
