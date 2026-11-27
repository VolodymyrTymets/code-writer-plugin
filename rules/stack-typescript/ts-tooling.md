---
description: TypeScript tooling rules - one package manager, a pinned runtime, lockfile installs, compiler and lint config, dependency additions, generated artefacts.
paths:
  - "**/package.json"
  - "**/package-lock.json"
  - "**/pnpm-lock.yaml"
  - "**/pnpm-workspace.yaml"
  - "**/yarn.lock"
  - "**/bun.lock"
  - "**/bun.lockb"
  - "**/tsconfig*.json"
  - "**/eslint.config.*"
  - "**/biome.json*"
  - "**/.nvmrc"
  - "**/.node-version"
---

# TypeScript tooling rules

Core rules T1–T4 already cover the command map, the pinned runtime, the single dependency manager and pipeline files. These add what is specific to TypeScript. The repo's own conventions win over these (rule D2).

1. The package manager is the one the repo declares: `packageManager` in `package.json`, otherwise the lockfile (`package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `bun.lock` or `bun.lockb` → bun). Never mix managers and never create a second lockfile.
2. Reproduce an install from the lockfile: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable` (Yarn 1: `--frozen-lockfile`), `bun install --frozen-lockfile`. If that fails because the lockfile is out of date, report it; do not delete or hand-edit the lockfile.
3. The runtime is the one `.nvmrc`, `.node-version` or `engines` pins. If the local version differs, stop and report (rule T2).
4. Run the scripts `package.json` declares, through the command map. Do not call a tool with ad-hoc flags that bypass the repo's config.
5. A new dependency is a decision: justify need, size, licence and maintenance in the PR. Build and test tools go in `devDependencies`. In a workspace, add it to the package that imports it, not to the root. A version bump of an existing dependency is its own PR (rule C1).
6. Compiler and lint settings are not loosened to make code pass: no weaker `strict` options, no new `exclude` entry, no rule turned off, without a human-approved `// WHY:` (rule B3). Tightening them is a separate PR.
7. Type-check with the repo's `typecheck` command. A passing test run or bundle is not a type check: several runners and bundlers strip types without checking them.
8. Generated output (API clients, ORM clients, schema types) is never hand-edited; change the source and re-run the generator from the command map (rule C3).
9. Never commit `node_modules/`, build output, `*.tsbuildinfo` or coverage; they are protected paths. Registry tokens never go into a committed `.npmrc` (rule A6).
