<!--
  Stack section for the project constitution. `/setup` (step 4.5) appends this block to CLAUDE.md
  under the command map. Bullets only: a second table row with the same task name would replace the first.
  Keep it short: the depth lives in .claude/rules/.
-->

- **TS1** `.claude/rules/ts-tooling.md`, `ts-core.md` and `testing-ts.md` apply to all TypeScript code. They add to the core rules and never override them; if they appear to conflict, core wins and you raise it.
- **TS2** Install and run only through the declared package manager and the `package.json` scripts. Never mix managers or create a second lockfile.
- **TS3** No `any`, `// @ts-ignore` or `eslint-disable` without a human-approved `// WHY:`.
