---
description: TypeScript code rules - no any, validation at boundaries, narrowing, error handling, async, imports, configuration and secrets.
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.mts"
  - "**/*.cts"
---

# TypeScript code rules

Read the neighbouring modules first and follow their pattern (rule D1); these rules are the floor, not a replacement for the repo's conventions (rule D2).

1. **No `any` in new code.** Use `unknown` and narrow it. No `as` cast and no `!` non-null assertion to silence the compiler; where one is really needed it carries a `// WHY:` (rule D3).
2. **No `// @ts-ignore`, `// @ts-nocheck` or `eslint-disable`** without a human-approved `// WHY:` (rule B3). `// @ts-expect-error` is for a test that asserts a type error.
3. **Validate at the boundary.** Request bodies, environment variables, files, storage and third-party responses are `unknown` until checked by the repo's validation library or a type guard. A type annotation checks nothing at run time.
4. **Annotate exported functions** with parameter and return types. Let inference work for locals.
5. Model alternatives as discriminated unions and handle every case; an exhaustive `switch` ends in a `never` check. Prefer a union of literals to a new `enum` unless the repo uses enums.
6. **Errors are never swallowed** (rule D5). A caught value is `unknown`: check `instanceof Error` before reading it. Throw `Error` objects, not strings.
7. **Every promise is awaited, returned or explicitly handled.** No floating promises and no `async` callback where the caller ignores the result (`array.forEach`). Run independent work with `Promise.all`; keep dependent work sequential.
8. Do not mutate arguments or shared module state; use `readonly` types where a value must not change.
9. Follow the repo's module style: its path aliases, import order and export style. Use `import type` for type-only imports where the config asks for it. No new barrel files or import cycles.
10. **Configuration and secrets come from the environment or the repo's config module**, never from literals. Code shipped to a browser or a device holds no secrets, whatever the variable is called.
11. Log through the repo's logger, not `console`, in application code; never log tokens or personal data (rule D8).
12. Comments explain *why*; no commented-out code; no `TODO` without a ticket (rule D6).
