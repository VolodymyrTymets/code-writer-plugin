# The TypeScript stack layer

Step 4.5 of `/setup` for a repo whose `Stacks:` line contains `typescript`. Same bootstrap PR, no second command.

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

### Framework files, only if the repo uses the framework

```bash
find . -name package.json -not -path '*/node_modules/*' -exec grep -HnE '"(react|react-native|@nestjs/core)"[[:space:]]*:' {} +
```

Copy a file of `## Optional files` into `.claude/rules/` only when a `package.json` found this way lists its dependency; no match means no file. A React Native app lists `react` too, so it gets both. In a monorepo, narrow each file's `paths:` to the apps that list the dependency (`apps/web/**/*.tsx`), so mobile rules do not load for web code.

## Step 3 — Append the stack section and fill the placeholders

Append `rules/stack-typescript/CLAUDE.stack-section.md` to `CLAUDE.md` after the command map, **only if it is not already there**. Its rule IDs are `TS1`–`TS3`, so they sit beside another stack's section. In a repo with two stacks the command map follows step 4.5 of `/setup`: labelled rows such as `lint (ts)`.

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
- `templates/stack-typescript/destructive-commands.ts.txt` to `.claude/rules/destructive-commands.typescript.txt`., plus anything this repo can do irreversibly (a seed script that wipes data, a store or registry upload).

## Step 5 — Settings and verification

Add this stack's install, lint and test commands to `allow` and `ask` in `.claude/settings.json`. Do not touch `permissions.deny`. `grep -r '{{' CLAUDE.md .claude/` returns nothing. Run every command in the map.

## Definition of done (folded into setup-project's own list)
- [ ] Package manager, runtime version, compiler, linter and test runner detected and confirmed
- [ ] The three TypeScript rule files installed (merged with any the repo already had)
- [ ] Framework files installed only for the frameworks the repo lists, `paths:` narrowed in a monorepo
- [ ] Stack section appended; `typecheck` row added if the repo type-checks; `CLAUDE.md` still under 200 lines
- [ ] `protected-paths.typescript.md` and `destructive-commands.typescript.txt` installed, with this repo's real entries
- [ ] Every command in the map verified to run (or marked `none`)

## Export manifest

Exactly these files are copied for `typescript`, each once. `.claude/rules/` gets the rule files and the two guard files under their installed names (step 4), `CLAUDE.md` gets the section.

- `rules/stack-typescript/ts-tooling.md`
- `rules/stack-typescript/ts-core.md`
- `rules/stack-typescript/testing-ts.md`
- `rules/stack-typescript/CLAUDE.stack-section.md`
- `rules/stack-typescript/protected-paths.md`
- `templates/stack-typescript/destructive-commands.ts.txt`

## Optional files

Copied only when a `package.json` in the repo lists the dependency after the dash (step 2).

- `rules/stack-typescript/ts-react.md` — `react`
- `rules/stack-typescript/ts-nestjs.md` — `@nestjs/core`
- `rules/stack-typescript/ts-react-native.md` — `react-native`
