# The TypeScript stack layer

Step 4.5 of `/setup` for a repo whose `Stacks:` line contains `typescript`. Same bootstrap PR, no second command.

**Status:** the rule files below are written in T3. Until `rules/stack-typescript/` exists in the plugin, install nothing for this stack, keep `typescript` in the `Stacks:` line, and say in the PR that the TypeScript rules are not shipped yet. Never write them by hand into the repo from memory.

## Step 1 — Detect, then confirm in one line

```bash
ls package-lock.json pnpm-lock.yaml yarn.lock bun.lockb bun.lock package.json tsconfig*.json 2>/dev/null
cat .nvmrc .node-version 2>/dev/null; grep -n '"engines"\|"packageManager"' package.json 2>/dev/null
ls eslint.config.* .eslintrc* biome.json* .prettierrc* vitest.config.* jest.config.* 2>/dev/null
grep -n '"\(lint\|test\|typecheck\|build\|dev\)"' package.json 2>/dev/null
```

Report one line, for example: *"pnpm, Node 20, tsc strict, eslint, vitest"*. Ask only when detection is ambiguous, for example two lockfiles (usually one is stale, which is worth reporting).

## Step 2 — Install the rule files

Copy the files of the manifest below from `rules/stack-typescript/` into `.claude/rules/`. If the repo already has hand-written TypeScript rules there, **merge, never overwrite**.

## Step 3 — Append the stack section and fill the placeholders

Append `rules/stack-typescript/CLAUDE.stack-section.md` to `CLAUDE.md` after the command map. Rule IDs must not collide with another stack's section in a repo with two stacks (T3 decides the prefixes).

| Placeholder | Typical value |
|-------------|---------------|
| `{{DEPENDENCY_MANAGER}}` | `npm`, `pnpm`, `yarn` or `bun`, from the lockfile and `packageManager` |
| `{{RUNTIME_VERSION_FILE}}`, `{{RUNTIME_VERSION}}` | `.nvmrc` or `.node-version` and its content, or `engines.node` |
| `{{CMD_INSTALL}}` | `pnpm install --frozen-lockfile` or the manager's equivalent |
| `{{CMD_LINT}}` | the declared `lint` script. Static analysis only |
| `{{CMD_TEST}}`, `{{CMD_TEST_AFFECTED}}` | the declared test script, and the file-scoped form of the runner |

A type check is a `| typecheck | ... |` row in the command map and a B1 gate. Run each command once. Record the count of existing findings in the cell when lint has a backlog (rule C1).

## Step 4 — Extend the project-owned extension points

Append the entries of `templates/stack-typescript/protected-paths.ts.md` to `.claude/rules/protected-paths.md` and `templates/stack-typescript/destructive-commands.ts.txt` to `.claude/rules/destructive-commands.txt`, under a comment naming the stack. If the repo also has another stack, never write the same block twice.

## Step 5 — Settings and verification

Add this stack's install, lint and test commands to `allow` and `ask` in `.claude/settings.json`. Do not touch `permissions.deny`. `grep -r '{{' CLAUDE.md .claude/` returns nothing. Run every command in the map.

## Export manifest

Exactly these files are copied for `typescript`, each once. They are created by T3; this list is the contract T3 must keep or update.

- `rules/stack-typescript/ts-tooling.md`
- `rules/stack-typescript/ts-core.md`
- `rules/stack-typescript/testing-ts.md`
- `rules/stack-typescript/CLAUDE.stack-section.md`
- `templates/stack-typescript/protected-paths.ts.md`
- `templates/stack-typescript/destructive-commands.ts.txt`
