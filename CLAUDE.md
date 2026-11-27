# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the **source of the `code-writer` Claude Code plugin** for Python and TypeScript projects, not an application. It is also the plugin marketplace (`.claude-plugin/marketplace.json`, marketplace name `code-writer`, plugin `source: "./"`). There is no build step and no `package.json`; everything is Markdown, JSON and stdlib-only Python 3.9+ scripts. Maintainers install `requirements-dev.txt` (pytest) to run the tests.

The SessionStart hook of an installed copy may say "no CLAUDE.md - run /setup". That is for repos that use the plugin. Do not run `/setup` here.

`README.md` is the user-facing doc and `CONTRIBUTING.md` the maintainer doc and only design document.

## Commands

Run all three before a PR. The repo has no CI of its own.

```bash
python -m pytest tests/test_hooks.py        # hook behaviour against throwaway fixture repos
python -m pytest tests/test_structure.py    # structure guard
claude plugin validate ./ --strict      # one warning is expected: this very file is not loaded as plugin context
python -m pytest tests/test_hooks.py -k "<substring>"   # a single hook test
```

## Architecture

**Two layers, separated by directory, not by repo.**
- **core**: `rules/core/`, 9 workflow skills, 7 core hooks, `mcp/base.json`. It must never name a language, framework or dependency manager. The hooks read the repo's own **command map**, a markdown table in the target repo's `CLAUDE.md` (lint / affected tests ...), instead of hardcoding tooling.
- **stack-python**: `rules/stack-python/` (`python-tooling`, `python-core`, `testing-python`, `protected-paths`), `templates/stack-python/`, and its share of the 2 stack hooks (`guard-dependency-manager` for pip / uv / poetry / pipenv, `format-changed` for opt-in `ruff format`). There are no stack skills; every skill is stack-neutral and the Python knowledge is in rules.
- **stack-typescript**: `rules/stack-typescript/` (`ts-tooling`, `ts-core`, `testing-ts`, `protected-paths`, optional `ts-react` / `ts-nestjs` / `ts-react-native`) and `templates/stack-typescript/`; the same 2 stack hooks cover npm / pnpm / yarn / bun and opt-in prettier / biome. Core `protected-paths.md` holds universal entries; each stack's list installs as its own `protected-paths.<stack>.md`.

The hook lists live in `tests/test_structure.py` (`CORE_SKILLS`, `STACK_SKILLS`, `CORE_HOOKS`, `STACK_HOOKS`). A stack term in a core hook fails the build. Elsewhere in core it only warns.

**What Claude Code actually loads from this plugin:** `skills/`, `agents/`, `hooks/hooks.json` and `.claude-plugin/`. `rules/`, `templates/` and `mcp/` are an **inert library** that the `/setup` skill (`skills/setup-project`) copies into the target repo. A plugin's own settings are ignored except `agent` and `subagentStatusLine`, so the permission deny list lives in `templates/settings.project.json`.

**Hooks** (`hooks/hooks.json` → `bin/*.py`, shared helpers in `bin/lib/util.py`):
- PreToolUse guards: `guard-git`, `guard-destructive`, `guard-dependency-manager`, `guard-protected-paths`, `guard-plan-approval`. The path and plan guards are wired for `Bash` and for `Edit|Write|...|mcp__.*`, so a write through the shell or an MCP tool cannot bypass them. The structure test checks both wirings.
- `record-activity` (PostToolUse and PostToolUseFailure) logs verification runs to `.claude/.state`, which is gitignored. `verify-dod` (Stop) reads that log and blocks stopping with code changed but no lint / test run (rule B1). Where `CLAUDE.md` has `Gate paths (<label>)` lines, it requires the `(<label>)` rows of the edited files, not just any row of the kind.
- Every block message names a rule ID (A1–A4 git, B1 definition of done, B4 plan approval, C3 protected path, C4/C5 destructive and production, `py-tooling-1..3` and `ts-tooling-1..3` dependencies, G2 no project knowledge). The IDs are defined in `rules/core/CLAUDE.template.md`, the two `*-tooling` sets in their stack's tooling rule file. Keep message text and IDs stable, since docs and tests refer to them.
- `guard-git` and `guard-destructive` match on the command text, so a heredoc or `echo` that merely *contains* `rm -rf`, `curl … | sh` or `gh release create` is blocked as well. When writing such text into a file from the shell, use the Write tool instead.

**Workflow:** `/feature` → `/plan` (`plan-feature`) → human adds `Approved-by:` to `docs/features/<TICKET>/plan.md` → `/analyze` (`analyze-plan`, runs in the write-free `plan-gate` agent fork, referenced as `code-writer:plan-gate`) → `/implement` (`develop-feature`) → `/review-pr`.

**Command names come from each skill's frontmatter `name:`, not its directory.** `plan-feature/` answers to `/plan`. The map is `COMMANDS` in `tests/test_structure.py`. The test fails if a skill drifts from it, if a name collides with a built-in (`/review` is one, hence `/review-pr`), or if any doc references a command that does not exist. Commands planned but not built may appear only in `README.md` and `CHANGELOG.md`.

## Conventions when changing this repo

- A hook change needs a test case in `tests/test_hooks.py`. The suite uses a core fixture (command map through `make`) plus pip, uv, Node and Both fixtures on purpose. The test runner clears `VIRTUAL_ENV` so an active venv on the developer's machine cannot change results. The formatter test is skipped when `ruff` is not installed.
- Skills have no nested subdirectories, other than `references/`. Every `{{PLACEHOLDER}}` in `rules/` must be documented in `skills/setup-project`.
- Project-specific knowledge never enters this repo (G2). Generalise it first.
- Prefer a lint rule or a hook over a prompt rule.
- Always-loaded lines (`CLAUDE.md`, its `@` imports, rules without `paths:`) are capped per export by `CONTEXT_CEILING` in the structure test. See "Context budget" in `CONTRIBUTING.md`.
- `CHANGELOG.md` is ordered newest release first and **leads with a "Deleted" section**. The version lives in `.claude-plugin/plugin.json`.
- Default branch is `main`. Branch before committing. Hooks block commits and pushes on protected branches.
