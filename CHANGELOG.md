# Changelog

Format: **Deleted** first — a smaller plugin each release is the goal.

## Unreleased

**Set-up repos get stricter.** The protected-paths guard used to read only the first two blocks of a file, so entries
`/setup` had appended below them (the Python ones) were ignored. They are now enforced. Unlabelled additions placed
after the ask-first list now ask for confirmation. No file needs to change for this.

**Optional manual step for set-up repos, to load less in every session.** Do not copy the new
`protected-paths.md` over yours: that would erase the entries added for your repo. Instead:

1. Add these two lines to the frontmatter of `.claude/rules/protected-paths.md`:

   ```yaml
   paths:
     - ".claude/rules/protected-paths*.md"
   ```

2. In `CLAUDE.md`, replace the line that imports `@docs/RUNBOOK.md` with
   ``- How to run things and what goes wrong: `docs/RUNBOOK.md` — read it when a command or the environment fails``.

### Deleted
- **Two always-loaded files**: core `protected-paths.md` now loads only when a protected-paths list is read or edited
  (the guard still reads it, so blocking is unchanged), and `CLAUDE.md` no longer imports `docs/RUNBOOK.md`.
- **Python-only stack hooks**: both now serve TypeScript too.
- **The "TypeScript rules not shipped yet" path in `/setup`**: choosing TypeScript now installs a layer.
- **Appending stack entries to shared files**: `/setup` no longer appends to `protected-paths.md` or
  `destructive-commands.txt`. `templates/stack-python/protected-paths.py.md` moved to
  `rules/stack-python/protected-paths.md`.
- **Lockfile and build-output globs in the core list**: they moved to the stack lists. A repo set up from now on with
  `Stacks: none` has no default protection for them, and a Python-only one none for `out/`, `*-lock.json` and
  `*-lock.yaml`.
- **The "not Python, skip" branch of `/setup`**: step 4.5 no longer skips a repo that is not Python. It follows the `Stacks:` line instead.
- **The `rln-agent` name**: plugin `rln-agent`, marketplace `rln` and repository `rln-agent` are gone. The plugin is
  now `code-writer`, the marketplace `code-writer` and the repository `code-writer-plugin`. The environment variable
  `RLN_PROTECTED_BRANCHES` is removed with no fallback; use `CODE_WRITER_PROTECTED_BRANCHES`.
- **Node**: the nine `bin/*.mjs` hooks, `bin/lib/util.mjs` and the two `tests/*.test.mjs` suites. Node.js is no longer a
  requirement of the plugin or of its tests.
- The `format the changed files` row and its table in the Python stack section, with `{{CMD_FORMAT}}`.
- The `typecheck` row and `{{CMD_TYPECHECK}}`: no Python repo this plugin targets runs one by default.
- The `build-validator` agent (typecheck and build runner); `test-runner` and `code-reviewer` remain.

### Added
- **Context budget**: `bin/context-cost.py` lists the lines a repo loads in every session (`CLAUDE.md`, its `@`
  imports and rule files without `paths:`). `/setup` runs it and reports the result, and the structure test fails a
  Python, TypeScript or Both export above 250 lines. CONTRIBUTING and README explain what loads when.

### Changed
- **Repos with a `package.json` or Node lockfile get stricter**, set up or not: `guard-dependency-manager` blocks another
  Node manager (`ts-tooling-1`), forced and global installs (`ts-tooling-2`) and lockfile deletion (`ts-tooling-3`),
  and asks before a new runtime dependency. A confirmation question no longer stops later commands on the same line
  from being checked.
- `format-changed` also formats `.ts`, `.tsx`, `.mts` and `.cts` files where the repo declares prettier or biome.
- Each stack installs `protected-paths.<stack>.md` and `destructive-commands.<stack>.txt`, and the guards read every
  such file. A `!` exception applies within its own file. The C4 message names the file that matched.
- `rules/stack-typescript/protected-paths.md` is new.
- TypeScript layer: `ts-tooling.md`, `ts-core.md`, `testing-ts.md`, stack rules `TS1`–`TS3`, destructive-command
  patterns, and React, NestJS and React Native files installed only when `package.json` lists the framework.
- A repo with both stacks gets labelled command-map rows (`lint (ts)`) and one `Gate paths (<label>)` line per stack.
  The definition-of-done gate (B1) then requires the rows of every stack whose files were edited and names each missing
  one; an `e2e` run no longer stands in for a split test row. Without the lines, either row satisfies the gate.
- `/setup` asks first which stack the repo uses (TypeScript, Python or Both), detecting from `pyproject.toml`, `requirements*.txt`, `package.json` and `tsconfig.json`, and records `Stacks: python, typescript` in `CLAUDE.md`. Only the chosen stacks' files are copied, each once. Repos set up earlier get the line inferred and inserted on a re-run. `references/stack-typescript.md` is added.
- Renamed to `code-writer`, version 0.2.0. Install with `claude plugin install code-writer@code-writer`; existing
  users must reinstall and change `rln-agent@rln` in their `enabledPlugins`. Hook messages are prefixed `[code-writer]`
  and the plan gate is `code-writer:plan-gate`. The description now says Python and TypeScript projects.
- Hooks and tests are Python. `bin/*.py` use only the standard library and run as `python3 bin/<name>.py` (Python 3.9+),
  with the same rule IDs and block messages. `tests/` is pytest (`requirements-dev.txt`), same cases as before plus
  parametrised variants. The old and new helpers were compared on a shared corpus (0 differences) and the old and new
  hooks on 706 payloads against a fixture repo (the only difference was the session briefing, which at that point
  also listed a `format` row).
- `testing-python.md` grew from 10 to 19 rules: fixture scoping and factories, mocking at the lookup seam, fakes over
  `MagicMock` and `create_autospec`, injected clock and seeded randomness, import-time side effects, GUI and
  hardware fakes, strict markers, flaky tests. `write-tests` now points at the stack testing rules.
- The default command map has a single static check, `lint`, and it is a B1 gate whenever the map holds a real
  command (`none` skips it). `typecheck` and `format` rows are optional: a repo that adds one has it enforced, as the
  hooks are generic. The opt-in `format-changed` hook does not read the map and is unchanged.
- The map parser reads `none` as "no such task" (it used to demand a command literally named `none`) and accepts a
  note after the backticked command, so `` `ruff check .` (report only) `` is no longer dropped.

## 0.1.0 — 2026-10-12 ·

First release as `rln-agent`: the plugin, moved to a Python flow and simplified.

### Deleted
- **The JS/TS stack layer**: `rules/stack-js/` (backend core, NestJS / Express / Fastify, REST / GraphQL, React,
  React Native, JS tooling, JS testing), `templates/stack-js/`, and `mcp/web.json`, `mcp/mobile.json`, `mcp/backend.json`.
- **Eight stack skills**: `backend-feature`, `graphql-resolver`, `api-contract`, `db-migration`, `react-feature`,
  `react-data-layer`, `rn-screen`, `rn-verify-on-device`. 17 skills became 9.
- **All database material**: the `db-migration` skill, the non-local-database-host check (C5) and its
  `local-db-hosts.txt`, the `migrate reset` / destructive-SQL patterns, the `{{CMD_MIGRATE}}` command-map row, the
  migration path rule and the schema lines in the gate, review and PR checklists.

### Changed
- Names: plugin `rln-agent`, marketplace `rln`, repository `VolodymyrTymets/rln-agent`, hook messages prefixed
  `[rln-agent]`, protected-branch override `RLN_PROTECTED_BRANCHES`. The version restarts at 0.1.0.
- `guard-dependency-manager` now follows pip, uv, poetry or pipenv, whichever the repo declares. It blocks a different
  installer, a bare `pip install` outside a venv, `--break-system-packages`, and deleting a requirements or lock file;
  a new runtime dependency asks first. Rule IDs `js-tooling-*` became `py-tooling-*`.
- `format-changed` formats `.py` files with `ruff format`, and only when the repo declares a `[format]` section.
- The CI evidence check scans for Python suppressions (`# noqa`, `# type: ignore`, `pytest.mark.skip`, …) instead of
  JS ones. The settings template denies `twine upload`, `uv publish` and `poetry publish`.

### Added
- `rules/stack-python/` (`python-tooling`, `python-core`, `testing-python`, `CLAUDE.stack-section`),
  `templates/stack-python/` and `skills/setup-project/references/stack-python.md`.
- pip and uv fixtures in `tests/hooks.test.mjs`.

### Not changed
- The workflow (`/feature`, `/plan`, `/analyze`, `/implement`, `/review-pr`, `/fix-bug`), the four subagents and
  the other seven hooks. Hooks remain Node scripts.
