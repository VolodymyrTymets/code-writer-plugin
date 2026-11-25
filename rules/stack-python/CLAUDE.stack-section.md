<!--
  Stack section for the project constitution. `/setup` (step 4.5) appends this block to CLAUDE.md
  under the command map and fills the placeholders. Keep it short: the depth lives in .claude/rules/.
-->

- **S1** `.claude/rules/python-tooling.md`, `python-core.md` and `testing-python.md` apply to all Python code. They add to the core rules and never override them; if they appear to conflict, core wins and you raise it.
- **S2** Install and run only through the project venv or the declared manager. A bare `pip install` is blocked because it changes the wrong interpreter.
- **S3** Type hints on new public functions. No `# noqa` / `# type: ignore` without a human-approved `# WHY:`.
