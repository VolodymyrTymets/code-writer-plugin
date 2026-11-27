# The TypeScript stack layer

Step 4.5 of `/setup` for a repo whose `Stacks:` line contains `typescript`. Same bootstrap PR, no second command.

**Status:** the rule files and the stack section are written in T3. Until `rules/stack-typescript/ts-core.md` exists in the plugin, skip steps 2 and 3 (still detect, fill the core placeholders and the command map, run step 4 and add the settings entries), keep `typescript` in the `Stacks:` line, and say in the PR that the TypeScript rules are not shipped yet. Never write them by hand into the repo from memory.

## Step 1 — Detect, then confirm in one line

```bash
ls package-lock.json pnpm-lock.yaml yarn.lock bun.lockb bun.lock package.json tsconfig*.json 2>/dev/null
cat .nvmrc .node-version 2>/dev/null; grep -n '"engines"\|"packageManager"' package.json 2>/dev/null
ls eslint.config.* .eslintrc* biome.json* .prettierrc* vitest.config.* jest.config.* 2>/dev/null
grep -n '"\(lint\|test\|typecheck\|build\|dev\)"' package.json 2>/dev/null
```

Report one line, for example: *"pnpm, Node 20, tsc strict, eslint, vitest"*. Ask only when detection is ambiguous, for example two lockfiles (usually one is stale, which is worth reporting).

## Step 2 — Install the rule files

Copy `ts-tooling.md`, `ts-core.md` and `testing-ts.md` from `rules/stack-typescript/` into `.claude/rules/`. Not `protected-paths.md`: step 4 installs it under its own name. If the repo already has hand-written TypeScript rules there, **merge, never overwrite**.

## Step 3 — Append the stack section and fill the placeholders

Append `rules/stack-typescript/CLAUDE.stack-section.md` to `CLAUDE.md` after the command map, **only if it is not already there**. Rule IDs must not collide with another stack's section in a repo with two stacks (T3 decides the prefixes).

| Placeholder | Typical value |
|-------------|---------------|
| `{{DEPENDENCY_MANAGER}}` | `npm`, `pnpm`, `yarn` or `bun`, from the lockfile and `packageManager` |
| `{{RUNTIME_VERSION_FILE}}`, `{{RUNTIME_VERSION}}` | `.nvmrc` or `.node-version` and its content, or `engines.node` |
| `{{CMD_INSTALL}}` | `pnpm install --frozen-lockfile` or the manager's equivalent |
| `{{CMD_LINT}}` | the declared `lint` script. Static analysis only |
| `{{CMD_TEST}}`, `{{CMD_TEST_AFFECTED}}` | the declared test script, and the file-scoped form of the runner |

A type check is a `| typecheck | ... |` row in the command map and a B1 gate. Run each command once. Record the count of existing findings in the cell when lint has a backlog (rule C1).

## Step 4 — Install the stack's guard files

Copy each only if it is not already there, and never append to `protected-paths.md` or `destructive-commands.txt`.

- `rules/stack-typescript/protected-paths.md` to `.claude/rules/protected-paths.typescript.md`, plus this repo's own generated output under its headings.
- `templates/stack-typescript/destructive-commands.ts.txt` to `.claude/rules/destructive-commands.typescript.txt`. It ships with T3; skip it until the file exists.

## Step 5 — Settings and verification

Add this stack's install, lint and test commands to `allow` and `ask` in `.claude/settings.json`. Do not touch `permissions.deny`. `grep -r '{{' CLAUDE.md .claude/` returns nothing. Run every command in the map.

## Export manifest

Exactly these files are copied for `typescript`, each once. `protected-paths.md` ships now (step 4 installs it as `protected-paths.typescript.md`) and the rest are created by T3; this list is the contract T3 must keep or update.

- `rules/stack-typescript/ts-tooling.md`
- `rules/stack-typescript/ts-core.md`
- `rules/stack-typescript/testing-ts.md`
- `rules/stack-typescript/CLAUDE.stack-section.md`
- `rules/stack-typescript/protected-paths.md`
- `templates/stack-typescript/destructive-commands.ts.txt`
