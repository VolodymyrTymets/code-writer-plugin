# Contributing to code-writer

How the plugin is built, why it is shaped this way, and what a change needs before it merges. For using the
plugin on a repository, see [README.md](README.md). This file is the only design document.

## One plugin, two layers

| Layer | Lives in | Rule of thumb |
|-------|----------|---------------|
| core | `rules/core/`, the 9 workflow skills, 7 core hooks in `bin/`, `mcp/base.json` | never names a language, framework or dependency manager — the hooks read the repo's own command map instead |
| stack-python | `rules/stack-python/`, 2 stack hooks, `templates/stack-python/` | names them on purpose |
| stack-typescript | `rules/stack-typescript/`, `templates/stack-typescript/`, no hooks yet | names them on purpose |

The layers are separated by directory rather than by repository. A boundary between directories is free to
move; one between repositories is not, and two repos mean two installs and a silently degraded config for anyone
who forgets the second. What the split is worth — hooks that read the command map instead of hardcoding tooling —
is kept and enforced by the tests. Supporting another language means a new `rules/stack-<lang>/` and its two hooks;
the core does not change.

## Layout

| Path | Contents |
|------|----------|
| `rules/core/` | `CLAUDE.template.md` — the constitution, rule IDs A1–G3 and T1–T4 · `testing.md` · `protected-paths.md` (universal entries only) |
| `rules/stack-python/` | `python-tooling.md` · `python-core.md` · `testing-python.md` · `CLAUDE.stack-section.md` · `protected-paths.md` |
| `rules/stack-typescript/` | `ts-tooling.md` · `ts-core.md` · `testing-ts.md` · `CLAUDE.stack-section.md` · `protected-paths.md` · optional `ts-react.md`, `ts-nestjs.md`, `ts-react-native.md` |
| `skills/` | **flat, 9 skills**: `setup-project`, `feature`, `plan-feature`, `analyze-plan`, `develop-feature`, `write-tests`, `write-docs`, `review-pr`, `fix-bug` |
| `agents/` | `test-runner`, `code-reviewer`, `plan-gate` (the forked, write-tool-free context `/analyze` runs in) |
| `hooks/hooks.json` + `bin/` | 9 hooks, stdlib-only Python 3.9+; shared helpers in `bin/lib/util.py`. `bin/context-cost.py` is not a hook: it reports the lines a repo loads every session (see Context budget) |
| `mcp/` | `base.json` — library docs (context7) and code navigation (serena) |
| `templates/` | `docs/` templates, project `settings.json` (**the deny list lives here, not in the plugin**), PR template, CI checks (`github/workflows/agent-checks.yml`), `destructive-commands.txt`, and `stack-python/` and `stack-typescript/` destructive commands |
| `evals/` | skill eval cases for `claude plugin eval` — see `evals/README.md` |
| `tests/` | pytest: the hook behaviour suite (`test_hooks.py`) and the structure guard (`test_structure.py`) |

Skills are **flat on purpose**: nesting inside a plugin's `skills/` is not a documented Claude Code feature.
The plugin's `rules/`, `templates/` and `mcp/` directories, by contrast, are not read by Claude Code at all — they
are an inert library that `/setup` copies from.

### Command names

A plugin skill takes its command from frontmatter `name:`, not from its directory — the opposite of a project
skill. That is why `plan-feature/` answers to `/plan`. `/review` belongs to a bundled skill, which is why
self-review is `/review-pr`. The map lives in `tests/test_structure.py` (`COMMANDS`), which fails if a skill's
`name:` drifts from it, if a name collides with a built-in, or if any document references a command that does
not exist.

### Why hooks and not prompts

A rule written in a prompt is a request; a hook is a mechanism. The write gates (`guard-protected-paths`,
`guard-plan-approval`) are wired for `Bash` and for `mcp__.*` as well as the edit tools, because a write through a
shell redirection or an MCP server is the same act as a write through `Write`. The definition-of-done gate only counts
a verification command that ran on its own line and exited zero: a piped or `|| true`-ed run says nothing about the
tool. Most new rules belong in a lint rule or a hook, not in a prompt.

## Testing

```bash
python -m pytest tests/test_hooks.py       # hook behaviour across fixture repos
python -m pytest tests/test_structure.py   # frontmatter, budgets, completeness, placeholder coverage, layer hygiene
claude plugin validate ./ --strict      # expect exactly one warning: the root CLAUDE.md is guidance for working in this repo, not plugin context
```

Fixtures on purpose: the core fixture's command map is driven through `make`, so a core hook that secretly depends
on one ecosystem's tooling fails the suite; the pip and uv fixtures, the Node repos (one per lockfile) and the
Both repos exercise the two stack hooks and prove the dependency guard follows whichever manager the repo declares.
The Node formatter tests use stub binaries; the ruff test is skipped on a machine without `ruff`.

The structure guard checks what review keeps missing: every export stays under the context ceiling, each stack layer is complete and path-scoped, every `{{PLACEHOLDER}}` in
`rules/` is documented in `/setup`, no skill has a nested subdirectory, no hook names a payload field Claude Code does
not send, and both write gates are wired for `Bash` and `mcp__.*`. A stack term in a **core hook** fails the build;
anywhere else in the core layer it warns.

The repo has no CI workflow of its own yet — run both suites locally before opening a PR.
(`templates/github/workflows/agent-checks.yml` is the check `/setup` installs into other repos.)

A hook change without a test case is not accepted: these guards run on real repositories, where a false block wastes
a developer's turn and a missed block means the rule quietly stopped existing.

## Context budget

Everything the plugin installs competes with the user's code for the model's context window. A second stack roughly
doubles the stack rules, so most of them must cost nothing until needed.

| What it is | When it is in context | Cost for a two-stack repo |
|------------|-----------------------|---------------------------|
| `CLAUDE.md` and its stack sections | every session, in full | paid always: keep each stack section to about 8 lines and the file under 200 |
| files `CLAUDE.md` imports with `@path` | every session, in full | paid always: an import organises, it does not save |
| rule files without `paths:` | every session | paid always: no rule file the plugin ships is one |
| rule files with `paths:` | only after Claude reads or edits a matching file | paid on demand: TypeScript rules do not load while editing `.py` files |
| hooks (`bin/*.py`) | run outside the model; only their messages enter: a block message, and the session briefing | small |
| skills | the description is always listed, the body loads when invoked | small: do not add skills per stack |

The loading behaviour is Claude Code's, described at <https://code.claude.com/docs/en/memory>.

**The ceiling.** *Always-loaded* means the first three rows: `CLAUDE.md`, everything it imports (four hops at most) and
every `.claude/rules/**/*.md` without `paths:`. Lines are raw lines as `wc -l` counts them, comments and frontmatter
included. `tests/test_structure.py` builds the Python, TypeScript and Both exports from `rules/` and `templates/`,
counts them with `bin/context-cost.py` and fails any above `CONTEXT_CEILING`, listing each counted file. The `docs/`
templates the constitution imports count too; `RUNBOOK.md` is only pointed at, so it does not. The ceiling covers what the plugin ships, not what `/setup`
or the repo adds later (labelled command rows, filled docs). Raise it only on purpose, in a PR that says why.
`/setup` runs the same script on the repo it set up and reports the result.

Rules of thumb:

1. A rule file without `paths:` is a bug. The structure test fails a stack one and warns on a core one. Core
   `protected-paths.md` is scoped to the lists themselves: the hook reads the file, so no session has to carry it.
2. Prefer a lint rule or a hook over a prompt rule. A hook costs no context until it speaks.
3. Never export a stack the user did not choose. An unused rule is not free.
4. Put framework guidance in optional files, installed only when the framework is present.
5. If a rule file grows past about 50 lines, split it by `paths:` so only the relevant part loads.

## Adding to this plugin

1. Ask whether it is stack-specific. If yes it goes to `rules/stack-python/` (or a new `stack-<lang>/`) and, if it is a
   skill, into the layer lists in `tests/test_structure.py`; if not, to `rules/core/`.
2. Project-specific knowledge never enters this repo (rule G2). Generalise it first.
3. `claude plugin validate ./ --strict` plus both test suites before opening a PR.
4. `CHANGELOG.md` leads with **what was deleted** — a smaller core each quarter is the goal. A release that needs a
   manual step in existing installs says so at the top of its entry.

## Guard rule files

Each writer owns its own file in the target repo's `.claude/rules/`, so no two append to one:

- `protected-paths.md` (from `rules/core/`, plus the repo's own entries) and `protected-paths.<stack>.md` (from
  `rules/stack-<stack>/protected-paths.md`).
- `destructive-commands.txt` (the repo's own) and `destructive-commands.<stack>.txt` (from `templates/stack-<stack>/`).

The hooks read exactly those name shapes; `protected-paths-notes.md` is ignored. Protected-path blocks are sorted by
the latest `Never write` / `Ask first` heading (blocks above the first one: by position), and a `!` exception applies
within its file. Put each fence on its own line. A repo with no protected-paths file gets every list under `rules/` as a fallback. A glob that two
stacks need is listed in both, so removing one stack's file leaves the other's protection whole.

## The `Stacks:` line

`/setup` asks which stack a repo uses and records the answer as one line in the repo's `CLAUDE.md`. Every later
`/setup` re-run reads it, so the format is a contract. The stack hooks do not read it: they are switched by the repo's
own manifests and lockfiles, and each hook is tagged with its stacks in `STACK_HOOKS` (`tests/test_structure.py`).
Their rule IDs are cited in the stack's tooling rule file.

- Shape: `Stacks: python, typescript`, matched by `^Stacks:\s*(.+)$`. Plain text: no bold, no backticks.
- Values: the names of the stacks `/setup` knows, lowercase, comma separated. A stack is known when
  `skills/setup-project/references/stack-<name>.md` exists with an `## Export manifest`. Its rule files may land later:
  a stack ships once its `*-core.md` rule file exists. `Stacks: none` means no
  stack known to `/setup` (the PR names the missing rules).
- Repos set up before this line existed have a stack section but no line. `/setup` infers the stack from the section,
  asks for confirmation, inserts the line and does not append the section again.
- Rollback: delete the line. `/setup` falls back to detect-then-confirm.
- Each stack reference (`skills/setup-project/references/stack-<name>.md`) ends with an `## Export manifest`: a bullet
  list of repo-relative paths, one per line. `/setup` copies exactly those files for a chosen stack, and
  `tests/test_structure.py` checks that the sets for Python, TypeScript and Both never overlap.
- A reference may also end with `## Optional files`: bullets of the form ``- `<path>` — `<dependency>` ``, each copied
  only when a `package.json` in the repo lists the dependency.
- With two stacks, a task both have gets a second, labelled row (`lint (ts)`); the hooks key rows by name. Label with
  `ts` or `py`, never the full name (`typescript` contains `types`).
- Each stack reference gives one ``Gate paths (<label>): `glob` ...`` line for two-stack repos. `record-activity`
  records which row ran, and `verify-dod` requires the rows of each label whose globs match an edited file. The hooks
  learn stacks from these lines only; without them either row satisfies the gate. A new stack adds its own line.
