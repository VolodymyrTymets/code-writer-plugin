---
name: setup
description: Day-one bootstrap of the code-writer config in a repository. Greenfield runs a guided interview; brownfield derives the rules from the code that already exists; the stack is asked first and only the chosen stack layers are installed. Produces CLAUDE.md, .claude/rules, .mcp.json, docs/ and the CI checks as one PR.
argument-hint: "[greenfield|brownfield] (auto-detected if omitted)"
disable-model-invocation: true
---

# Set up a project

Run once per repository. Output: a single PR titled `chore: bootstrap agent config` — never a direct commit to a protected branch (rule A1).

## Step 0 — Detect the mode

Brownfield if there is application source code with history (`git log --oneline | wc -l` > ~20 and `src`/`apps` populated). Greenfield otherwise. Announce which mode you are in and why, then confirm with the human in one line.

## Step 1 — Read the repo (both modes, before asking anything)

The dependency manifest(s) and any workspace declaration, the lockfile, the runtime version pin, the compiler/analyser config, the lint and format config, the declared task scripts, `.github/workflows/**` or the equivalent pipeline files, container and compose files, `README.md`, the persistence schema, the app/build configuration, and any existing `CLAUDE.md`.

From this, fill as much of the command map as you can **without asking**: install, lint, test, affected tests, build, dev, e2e. Only ask about what the repo does not tell you.

## Step 1.5 — Which stack? (before anything is copied)

Ask this before the interview and before any file is written. Greenfield or brownfield, the question is the same.

1. **Read an existing answer.** If `CLAUDE.md` has a `Stacks:` line, that is the answer: confirm it in one line and move on. If it has **no `Stacks:` line** but already holds a stack section from an earlier `/setup`, infer the stack from that section (a Python section means `python`), ask the human to confirm, insert the line, and never append the section again.
2. **Detect.** Look at the repo root and two levels down (`apps/*`, `packages/*`), skipping `node_modules`, `.venv` and `venv`. `pyproject.toml` or `requirements*.txt` suggests Python. `package.json` or `tsconfig.json` suggests TypeScript. Both together suggests Both. Nothing found (an empty greenfield repo) means no suggestion.
3. **Ask** with `AskUserQuestion`: TypeScript, Python or Both, with the detected option first. The user's answer wins over detection. Any other stack (Go, Rust...) is answered through "Other" and recorded as `Stacks: none`; the PR then names which stack rules the repo will need and who writes them.
4. **Record** the answer as `{{STACKS}}` in the `Stacks:` line of `CLAUDE.md` (format: see CONTRIBUTING.md). Step 4.5, the interview and every later re-run read this line and nothing else.

Re-run with a changed answer: install the stack that is missing, list the files of a stack that was dropped, and delete nothing.

## Step 2 — Greenfield: the interview

Follow @references/interview.md. Rules: batch questions, never ask what step 1 already answered, and keep the whole interview under ~15 minutes of the human's time. `docs/BUSINESS_MODEL.md` goals and non-negotiables are **required** output — an unranked goal list gives the agent no way to break a tie later.

## Step 3 — Brownfield: convention discovery

Follow @references/brownfield-discovery.md. The principle: **the constitution is derived from the code that already exists**, not from generic preferences. Read 5–10 representative files per area, surface conventions that are *unusual, opinionated, tribal or consistent*, ask why for each, draft each as a candidate rule, and let the developer confirm / edit / skip one by one. Never silently import a convention you merely inferred.

## Step 4 — Write the config

1. `CLAUDE.md` from the plugin's `rules/core/CLAUDE.template.md`, every `{{PLACEHOLDER}}` filled. Confirmed brownfield conventions go under the project-specific section at the bottom. **Check the line count — if over 200, move depth into `.claude/rules/`.**
2. `.claude/rules/` — `testing.md` and `protected-paths.md` from `rules/core/`, with the repo's real protected paths appended (dependency directories, build output, generated clients, platform build folders). Stack rule files come from the chosen stacks' `rules/stack-<name>/` folders in step 4.5 — **only the chosen stacks**, never a stack "just in case".
3. `.claude/settings.json` from `templates/settings.project.json` — `enabledPlugins` set, the repo's real commands in `allow` and `ask`. The whole `permissions` block is a **starter this repo then owns**: permissions cannot live in a plugin at all (only `agent` and `subagentStatusLine` apply from one; every other key is read and silently discarded), so nothing upstream updates any of it later. `allow` and `ask` fill mechanically from the command map, and a gap there shows up at once as extra prompts. `permissions.deny` is where a gap stays invisible: a missing rule changes nothing anyone sees, and for reads of secrets no hook covers the same ground, so a repo without it has no deny layer whatsoever. That is why it takes judgement rather than substitution — adapt it in both directions, neither is optional:
   - **Add** what the plugin cannot know about. Hunt for: infrastructure state that stores secrets in the clear (`*.tfstate`, `*.tfvars`), registry and cluster credentials (`.npmrc`, `.netrc`, `kubeconfig`, `*.ovpn`), framework secret stores (a Rails `master.key` and `credentials.yml.enc`, a `.pypirc`), and this ecosystem's irreversible publish verbs (`cargo publish`, `gem push`, `twine upload`, `helm push`, `flyctl deploy`).
   - **Remove or carve out** what over-blocks *this* repo — after seeing it block, not by guessing. The patterns match by extension and substring, so `*credentials*.json` catches a test fixture and `*.key` catches an i18n bundle; a `Read` deny also blocks writes, so the agent can neither read nor create the file. Either drop the entry or carve the file out with a `!` negation placed **below** the rule it carves from.

   Keep the `.env` values, the key material and the merge/publish rules unless the PR says why not — those are the ones the constitution's A4 and A6 depend on. If the repo already has `.claude/settings.json`, merge into it rather than overwrite it.
4. `.mcp.json` (repo root - Claude Code does not read `.claude/.mcp.json`) from `mcp/base.json`. Secrets as `${ENV_VAR}` only, never inline.
5. `docs/` from `templates/`: `ARCHITECTURE.md`, `BUSINESS_MODEL.md`, `DOMAIN_GLOSSARY.md`, `AGENT_TOOLING.md`, `RUNBOOK.md`, `decisions/` (+ the ADR template), `features/`.
6. `.github/PULL_REQUEST_TEMPLATE.md` and `.github/workflows/agent-checks.yml` from `templates/github/`.
7. `.claude/rules/destructive-commands.txt` from `templates/` — add this repo's own irreversible commands (device copies, publishes, cache wipes) so the guard blocks them by name.
8. `.gitignore`: add `.claude/settings.local.json` and `.claude/.state/`.

### Placeholders in the core template

| Placeholder | Value comes from |
|-------------|------------------|
| `{{PROJECT_NAME}}` | the repo / product name |
| `{{PROTECTED_BRANCHES}}` | the repo's real protected branches (ask, then verify against branch protection) |
| `{{CMD_INSTALL}}`, `{{CMD_LINT}}`, `{{CMD_TEST}}`, `{{CMD_TEST_AFFECTED}}`, `{{CMD_BUILD}}`, `{{CMD_DEV}}`, `{{CMD_E2E}}` | the declared task scripts, **each one actually run once** to confirm it works. Use `none` where the repo genuinely has no such task — never invent a command |
| `{{STACKS}}` | the stack answer from step 1.5, written as `python`, `typescript`, `python, typescript` or `none`. Plain text, no bold, no backticks |
| `{{DEPENDENCY_MANAGER}}` | the manifest's declared manager |
| `{{RUNTIME_VERSION_FILE}}`, `{{RUNTIME_VERSION}}` | the version pin file the repo uses, and the version in it |
| `{{I18N_NOTE}}` | `""` if the repo has no i18n, otherwise one clause naming the key convention |

Any placeholder left unfilled is a bug: the agent will read it literally. `grep -r '{{' CLAUDE.md .claude/` must come back empty (step 6).

## Step 4.5 — The stack layers

For each stack in the `Stacks:` line, follow its reference: @references/stack-python.md or @references/stack-typescript.md. Each reference ends with an `## Export manifest`; copy exactly those files, each one once, and no file of a stack that was not chosen. `Stacks: none` skips this step.

In a repo with two stacks, `protected-paths.md` and `destructive-commands.txt` are shared files. Each stack appends its own block once, under a comment naming the stack, until they are split per stack.

Python, in short:

```bash
ls uv.lock poetry.lock Pipfile requirements*.txt pyproject.toml .python-version ruff.toml 2>/dev/null
ls -d .venv venv 2>/dev/null
```

Install `python-tooling.md`, `python-core.md` and `testing-python.md` from `rules/stack-python/` into `.claude/rules/`,
merging with any Python rules the repo already has instead of overwriting them. Then append the filled
`rules/stack-python/CLAUDE.stack-section.md` to `CLAUDE.md` and extend `protected-paths.md` and
`destructive-commands.txt` from `templates/stack-python/`.

## Step 5 — Seed the knowledge layer

Do not leave templates empty — an empty doc is worse than none, because the agent will trust it.

- `ARCHITECTURE.md`: fill from what you actually read — the real workspace layout, where data truth lives, the API contract location, environments, the two or three key flows.
- `BUSINESS_MODEL.md`: from the interview (greenfield) or from the human in three questions (brownfield): what is the product, the top three ranked goals, the non-negotiables.
- `DOMAIN_GLOSSARY.md`: extract the domain nouns already in the code (entity/model names, route segments) and ask the human to confirm each meaning and its client-facing word.
- `decisions/`: record decisions **already made** in the repo as ADRs (persistence layer, state management, auth approach, repo tooling) — brownfield usually yields three to six.

## Step 6 — Verify the setup itself

- Every `{{PLACEHOLDER}}` gone: `grep -r '{{' CLAUDE.md .claude/ docs/` returns nothing.
- Every command in the command map actually runs (run them).
- `CLAUDE.md` under 200 lines.
- The hooks fire: try a write to a protected path and confirm it is blocked; confirm the definition-of-done gate can read the command map (it quotes your commands back when it blocks).
- The deny list is live, not merely written. The check that counts is behavioural: reading a `.env` in this repo must be refused, and reading `.env.example` must still work. Then run `claude doctor`: under **Invalid settings** it names any rule Claude Code rejected, with the file, the key and the reason. It does not print the rules that were accepted, and it does not catch every bad one (a deny rule naming a tool that does not exist was not reported), so treat it as a way to find a broken rule, never as proof that the rest are in force.
- MCP servers connect (`/mcp`).

## Step 7 — Hand over

Open the PR, then tell the human: what was created, which conventions were adopted (brownfield), what still needs their input, and the workflow to use from now on (`/plan` → `/analyze` → `/implement` → `/review-pr`; the draft PR is the last stage of `/implement`). Walk the rest of the team through it — there is no onboarding command yet.

## Definition of done
- [ ] Mode detected and confirmed
- [ ] Stack asked before any file was copied; the `Stacks:` line is in `CLAUDE.md`
- [ ] Command map filled and every command verified to run
- [ ] `CLAUDE.md` complete, under 200 lines, no placeholders
- [ ] Rule files, settings, `.mcp.json`, `destructive-commands.txt`, `docs/`, PR template, CI check in place
- [ ] `permissions.deny` present in `.claude/settings.json`, adapted to this repo in both directions, and observed to block a `.env` read while blocking nothing legitimate — no other layer carries it
- [ ] Stack layers: only the chosen stacks' manifests installed, once each (merged with the repo's own), stack sections appended, `CLAUDE.md` still under 200 lines
- [ ] Every command in the map verified to run (or marked `none`)
- [ ] Knowledge docs actually filled, not left as templates
- [ ] Existing decisions captured as ADRs (brownfield)
- [ ] One PR opened, nothing committed to a protected branch
