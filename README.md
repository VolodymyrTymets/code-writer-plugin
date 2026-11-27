# code-writer

A Claude Code plugin that gives a Python or TypeScript repository one spec-driven workflow (plan → human approval → gate →
implement → self-review → draft PR), a verification-first definition of done, reviewer subagents, and hooks that
mechanically block the mistakes a prompt alone does not prevent. Python and TypeScript layers add rules for tooling,
code and tests, and a dependency-manager guard and an opt-in formatter cover both.

Maintaining the plugin itself? See [CONTRIBUTING.md](CONTRIBUTING.md).

## Requirements

- Claude Code 2.1.x
- `python3` 3.9 or newer on `PATH` — every hook is a Python script that uses only the standard library, so it needs no
  virtualenv and no `pip install`. It is run by that system `python3`, not by your project's venv. Tested on macOS; on
  Windows `python3` must resolve to a real interpreter
- A git repository. If branch names carry a ticket (`feat/ABC-142-export`), the plan gate and the session
  briefing read it from there

## Quick start

```bash
claude plugin marketplace add VolodymyrTymets/code-writer-plugin
claude plugin install code-writer@code-writer
```

`marketplace add` fails with "SSH authentication failed" or "Repository not found"? See
[TROUBLESHOOTING.md](TROUBLESHOOTING.md).

Then, inside the repository:

```
/setup                  # once per repo: asks the stack (TypeScript, Python or Both), then interview or brownfield discovery
/feature ABC-142        # the whole lifecycle for one ticket
```

`/setup` opens a PR with `CLAUDE.md` (the constitution and the command map), the rules for the stacks you chose, `.claude/settings.json`
with the permission deny list, `.mcp.json`, the `docs/` skeleton, a PR template and the CI agent checks. Review and
merge it before starting feature work — until then the hooks have no command map to read.

`/setup` asks the stack first and installs only what you answer: **Python** gets the Python layer, **TypeScript** the TypeScript layer, **Both** each layer once. The answer is one line in `CLAUDE.md`, `Stacks: python, typescript`, which a re-run reads. Your answer wins over what `/setup` detects.

To make the plugin install for everyone who opens the repo, `/setup` also writes this into `.claude/settings.json`:

```json
{
  "enabledPlugins": { "code-writer@code-writer": true },
  "extraKnownMarketplaces": {
    "code-writer": { "source": { "source": "github", "repo": "VolodymyrTymets/code-writer-plugin" } }
  }
}
```

### Approving a plan

`/plan` writes `docs/features/<TICKET>/plan.md` and stops. Code for that ticket cannot be written until a
human adds a signature line to the plan:

```
Approved-by: <name> · <YYYY-MM-DD>
```

Approval is a line in a file, not a chat message, so it is durable and shows up in the PR diff. A deliberate
exception is written the same way, with its reason: `Approved-by: spike, no review - ABC-142`. Docs, the
spec and the plan itself stay writable while you wait.

## Commands

| Command | What it does |
|---------|--------------|
| `/feature <TICKET>` | **Start here.** The whole lifecycle: plan → human approval → gate → implement → self-review → draft PR |
| `/setup` | Once per repo — asks the stack first (TypeScript, Python or Both), then interview or brownfield discovery |
| `/plan <TICKET>` | Reads code and docs, asks only real gaps, writes spec + plan |
| `/analyze` | The gate: plan vs constitution, rules, architecture, acceptance criteria. Runs in a read-only fork, so it only sees what is **written in the plan** |
| `/implement <TICKET>` | One requirement at a time, a quality gate after each, tests, docs, **draft PR** |
| `/review-pr` | Self-review before a human's time is spent (not `/review` — that name belongs to a built-in) |
| `/fix-bug` | Reproduce first, root cause, minimal fix, regression test |
| `/write-tests`, `/write-docs` | Test and documentation procedures |

Every command also works namespaced, e.g. `/code-writer:plan`, if another plugin owns the short name.

`/feature` never starts on its own: the model cannot invoke it. If you just say "build ABC-142", you get
`/plan` and then `/implement` — the approval step is still enforced, by the hook rather than by the wrapper.

## When a hook blocks you

Every block names a rule ID and the allowed alternative. The common ones:

| You see | Why | What to do |
|---------|-----|------------|
| **B4** — plan not approved | A plan exists for the branch's ticket without an `Approved-by:` line | Get a human decision and add the line (above). No ticket in the branch or no plan file means the gate stays silent |
| **B1** — definition of done | You are stopping with code changed but no lint / tests / execution recorded | Run the commands the message quotes from your command map, **each on its own line**. `make test \| tail`, `make lint \|\| true` and `make test ; echo done` do not count — the exit code is not the tool's. After two blocks the gate hands control back to you |
| **C3** — protected path | Secrets, lockfiles, build output, generated code — also when written through the shell (`>`, `sed -i`, `cp`) or an MCP tool | Edit the source of truth instead. Pipeline and agent-config files ask for confirmation rather than block |
| **C4 / C5** — destructive command | `rm -rf` outside build dirs, publish/deploy, infrastructure CLIs, anything aimed at a production host | Run it yourself if it is really intended. Repo-specific patterns live in the `destructive-commands*.txt` files below |
| **A1–A4** — git | Commit/push on a protected branch, plain `--force`, `--no-verify`, amending pushed commits, merging or approving a PR | Branch first; use `--force-with-lease`; merging stays a human action |
| **py-tooling-1…3** — dependencies | A different installer than the repo declares, `pip install` outside a venv, `--break-system-packages`, deleting a lock or requirements file | Use the declared manager, install through `.venv/bin/pip` or an activated venv, change the declaration instead of deleting it. A new runtime dependency asks for confirmation |
| **ts-tooling-1…3** — dependencies | A different Node manager than the repo declares, `--force`, `--legacy-peer-deps`, `--ignore-engines`, a global install, deleting a lockfile | Use the declared manager, add the tool to `devDependencies`, fix the conflict the install reports. A new runtime dependency asks for confirmation |

Protected branches default to `main master develop staging release`; set `CODE_WRITER_PROTECTED_BRANCHES=a,b,c` to change them.

## Configuring a repository

There is one contract between this plugin and a repository: **the command map in `CLAUDE.md`**.

```markdown
| Task | Command |
|------|---------|
| lint | `ruff check .` |
| affected tests | `python -m pytest -q tests/test_<module>.py` |
```

The hooks read that table and never hardcode tooling. The definition-of-done gate quotes these commands when it
blocks, the session briefing shows them, the subagents run them. `/setup` fills it; keep it true — a wrong entry is
worse than an empty one, and a task the repo does not have is written `none`.

Two more files extend the guards per repo:

| File | Purpose | Written by |
|------|---------|------------|
| `.claude/rules/protected-paths.md` | Never-write and ask-first globs every repo has: secrets, generated code, CI and container files | `/setup` — plus this repo's generated, vendored and platform paths |
| `.claude/rules/protected-paths.<stack>.md` | The same for one stack: dependency directories, lockfiles, build output | `/setup`, one per chosen stack |
| `.claude/rules/destructive-commands.txt` | One regex per line of irreversible commands specific to this repo, blocked as C4 | `/setup` seeds it |
| `.claude/rules/destructive-commands.<stack>.txt` | The same for one stack | `/setup`, for a stack that ships one |

The guards read every file of each kind. In a protected-paths file, a fenced block counts under the latest
`Never write` or `Ask first` heading, and a `!` line carves an exception (e.g. `.env.example`) from its own file only.
With `Stacks: none` nothing covers lockfiles or build output until you add them.

### The Python layer

`/setup` copies three rule files from `rules/stack-python/` into `.claude/rules/`; they load only when a matching
path is touched:

| File | Covers |
|------|--------|
| `python-tooling.md` | one dependency manager, the project venv, pinned versions, ruff, new dependencies |
| `python-core.md` | type hints, error handling, logging, resources, concurrency, configuration |
| `testing-python.md` | pytest layout, fixtures, mocking boundaries, determinism, skips |

Two hooks belong to the layer: `guard-dependency-manager` (pip, uv, poetry or pipenv — whichever the repo declares)
and `format-changed`, which runs `ruff format` on an edited `.py` file **only** when the repo declares a `[format]`
section. A repo that never formatted its code is left alone, so a one-line fix stays a one-line diff. Both hooks also
serve TypeScript (below).

### The TypeScript layer

`/setup` copies three rule files from `rules/stack-typescript/` into `.claude/rules/`:

| File | Covers |
|------|--------|
| `ts-tooling.md` | one package manager, lockfile installs, pinned runtime, compiler and lint config, new dependencies |
| `ts-core.md` | no `any`, validation at boundaries, errors, promises, modules, configuration |
| `testing-ts.md` | runner conventions, typed fakes, mocking boundaries, determinism, skips |

`ts-react.md`, `ts-nestjs.md` and `ts-react-native.md` are added only when a `package.json` lists `react`,
`@nestjs/core` or `react-native`. `destructive-commands.typescript.txt` blocks registry changes, release tools,
over-the-air updates and commands that drop database contents.

The same two hooks serve this layer, each command judged only by its own ecosystem:

- `guard-dependency-manager` takes the manager (npm, pnpm, yarn, bun) from `packageManager`, otherwise from the lockfile,
  in the command's folder or a parent (`cd web && …` is followed). It applies wherever there is a `package.json` or a
  Node lockfile, whatever the `Stacks:` line says. Lockfiles of two managers and no `packageManager` means no
  wrong-manager block. Directory flags (`--prefix`, `-C`, `--dir`, `--cwd`) are not followed.
- `format-changed` formats an edited `.ts`, `.tsx`, `.mts` or `.cts` file with prettier (a config file or a `prettier`
  key in `package.json`) or biome (a `formatter` block in `biome.json` or `biome.jsonc`), only from
  `node_modules/.bin`. Both declared, neither declared or not installed means nothing happens.

In a repo with both stacks the command map has labelled rows such as `lint (ts)`. **Running either `lint` row, or
either test row, satisfies the definition-of-done gate**, so run both.

### Permissions are not part of the plugin

Claude Code applies only `agent` and `subagentStatusLine` from a plugin's own settings and silently ignores
everything else. So the deny list — unreadable `.env` and key material, no `gh pr merge`, no publish, no
force-push — lives in the repo's `.claude/settings.json`, written by `/setup` from
`templates/settings.project.json`. **A repo that has the plugin but never ran `/setup` has the hooks and none
of the permission layer.** To check: ask the agent to read `.env` (refused) and `.env.example` (allowed).
