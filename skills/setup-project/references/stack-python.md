# The Python stack layer

Step 4.5 of `/setup` in detail. Same bootstrap PR — this is one `/setup`, not a second command.

## Step 1 — Detect, then confirm in one line

```bash
ls uv.lock poetry.lock Pipfile Pipfile.lock pdm.lock requirements*.txt pyproject.toml 2>/dev/null
cat .python-version 2>/dev/null; grep -n "requires-python" pyproject.toml 2>/dev/null
ls ruff.toml .ruff.toml 2>/dev/null; grep -n "^\[tool\.\(ruff\|pytest\|mypy\|black\)" pyproject.toml 2>/dev/null
ls pytest.ini tox.ini noxfile.py conftest.py tests 2>/dev/null | head
ls -d .venv venv 2>/dev/null
```

Report one line: *"pip + pinned requirements.txt in `.venv`, Python 3.9, ruff, pytest, no typechecker"*. Ask only when detection is genuinely ambiguous — for example both `requirements.txt` and `poetry.lock` exist (usually one is stale, which is itself worth reporting).

## Step 2 — Install the rule files

Copy these from `rules/stack-python/` into `.claude/rules/`:

| File | Always? |
|------|---------|
| `python-tooling.md` | yes |
| `python-core.md` | yes |
| `testing-python.md` | yes, and it replaces nothing — `testing.md` from core stays beside it |

If the repo already has hand-written Python rules in `.claude/rules/`, **merge, never overwrite**: keep the repo's own wording where it is stricter, and let the plugin file carry only what the repo does not already say.

## Step 3 — Append the stack section to the constitution

Take `rules/stack-python/CLAUDE.stack-section.md` and, **only if it is not already in `CLAUDE.md`**, append it to `CLAUDE.md` after the core command map.

Fill the core placeholders for a Python repo:

| Placeholder | Typical value |
|-------------|---------------|
| `{{DEPENDENCY_MANAGER}}` | `uv`, `poetry`, `pipenv`, or `pip (pinned requirements.txt, inside a venv)` |
| `{{RUNTIME_VERSION_FILE}}`, `{{RUNTIME_VERSION}}` | `.python-version` and its content, or `requires-python` in `pyproject.toml` |
| `{{CMD_INSTALL}}` | `uv sync`, `poetry install`, or `pip install -r requirements.txt` |
| `{{CMD_LINT}}` | `ruff check .` (or what the repo declares). Static analysis only. A real command is a B1 gate |
| `{{CMD_TEST}}`, `{{CMD_TEST_AFFECTED}}` | `python -m pytest -q`, and the file-scoped form |
| `{{CMD_BUILD}}`, `{{CMD_E2E}}` | usually `none` |

There are no typecheck or format placeholders. If the repo already runs mypy or pyright, or a formatter check, add a `| typecheck | `mypy .` |` or `| format | `ruff format --check .` |` row by hand and it becomes a B1 gate; otherwise leave it out. (The opt-in `format-changed` hook does not read the map: it formats an edited file only when the repo declares a `[format]` section.)

Run each command once. If the lint command reports a backlog of existing findings, record the count in the command-map cell — fixing it is its own PR (rule C1).

Re-check the line count afterwards: `CLAUDE.md` stays under 200 lines.

## Step 4 — Install the stack's guard files

Copy each only if it is not already there, and never append to `protected-paths.md` or `destructive-commands.txt`.
A stack already installed by an earlier `/setup` (its block appended to those files) is skipped.

- `rules/stack-python/protected-paths.md` to `.claude/rules/protected-paths.python.md`, plus this repo's own generated or binary output (compiled UI resources, model files, stubs) under its headings.
- `templates/stack-python/destructive-commands.py.txt` to `.claude/rules/destructive-commands.python.txt`, plus anything this repo can do irreversibly (copying to a device, wiping a data directory).

## Step 5 — Settings and verification

- Add this stack's allow/ask entries to `.claude/settings.json`: the install, lint and test commands, and `Bash(<manager> add:*)` / `Bash(pip install:*)` under `ask`. The stack layer does not touch `permissions.deny`.
- Confirm the hooks fire: a bare `pip install x` must be blocked (outside an active venv), and a requirements-file install inside the venv must pass.
- `grep -r '{{' CLAUDE.md .claude/` returns nothing.
- Run every command in the map.

## Definition of done (folded into setup-project's own list)
- [ ] Dependency manager, interpreter version, linter and test runner detected and confirmed
- [ ] The three Python rule files installed (merged with any the repo already had)
- [ ] Stack section appended and filled; `CLAUDE.md` still under 200 lines
- [ ] `protected-paths.python.md` and `destructive-commands.python.txt` installed, with this repo's real entries
- [ ] Every command in the map verified to run (or marked `none`)

## Export manifest

Exactly these files are copied for `python`, each once. `.claude/rules/` gets the rule files and the two guard files under their installed names (step 4), `CLAUDE.md` gets the section.

- `rules/stack-python/python-tooling.md`
- `rules/stack-python/python-core.md`
- `rules/stack-python/testing-python.md`
- `rules/stack-python/CLAUDE.stack-section.md`
- `rules/stack-python/protected-paths.md`
- `templates/stack-python/destructive-commands.py.txt`
