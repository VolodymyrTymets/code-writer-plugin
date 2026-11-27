---
description: TypeScript testing rules - runner conventions, typed fakes, mocking boundaries, async assertions, determinism, skips.
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
  - "**/__tests__/**/*.ts"
  - "**/__tests__/**/*.tsx"
  - "**/tests/**/*.ts"
  - "**/tests/**/*.tsx"
  - "**/vitest.config.*"
  - "**/jest.config.*"
---

# TypeScript testing rules

Follow the repo's existing tests first (rule D1): its runner (vitest, jest, `node:test`), file placement, setup files and fakes. Do not add a second runner.

## Layout and style
1. Run the file you touched first, then the affected set from the command map.
2. Name a test for the behaviour (`rejects an empty fragment`), not for the function. One behaviour per test.
3. The same behaviour over several inputs uses the runner's table form (`test.each`), not a loop or an `if` in the body.
4. Assert on values: `toEqual` / `toStrictEqual` on the result, `toThrow` with the message or class. `toBeTruthy` hides the cause. Snapshots only for small, stable output, and never re-recorded without reading the diff (rule B3).
5. `await` every async assertion (`await expect(promise).rejects…`); an unawaited one passes whatever happens.

## Mocking and fakes
6. **Mock only the boundary**: network, filesystem, subprocesses, devices, the clock, randomness. Never mock the unit under test.
7. Prefer a small typed fake that implements the real interface to a bag of mock functions; the compiler then catches a changed signature. No `as any` to build one (rule D3).
8. Module mocks (`vi.mock`, `jest.mock`) are hoisted above the imports; keep their factories free of local variables. Prefer passing the dependency in.
9. Restore mocks and timers after each test (`restoreAllMocks`, `useRealTimers`). A test never depends on another test or on run order.

## Determinism
10. Use fake timers or an injected clock; never sleep to wait. Wait for a condition with the library's bounded helper.
11. Seed or inject randomness. No real network in a unit test.
12. Set environment variables inside the test and restore them. A module that reads config at import is imported after the environment is prepared.

## Skips and types
13. **No `.only`, `.skip`, `.todo` or `xit` committed** without a human-approved `// WHY:` and a ticket (rule B3).
14. A flaky test is fixed or quarantined with a ticket in the same PR; retries are not a fix.
15. Tests are type-checked too: if the runner strips types, the `typecheck` command must include test files.
16. Coverage is a diagnostic: read the uncovered branches of what you changed; do not add tests to move a number.

## Bugs
17. A bug fix starts with a test that fails for the right reason (`fix-bug` skill); show the failing run and the passing run.
