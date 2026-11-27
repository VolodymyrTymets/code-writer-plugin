---
description: NestJS rules - modules, dependency injection, validated DTOs, guards, errors, testing.
paths:
  - "**/*.module.ts"
  - "**/*.controller.ts"
  - "**/*.service.ts"
  - "**/*.guard.ts"
  - "**/*.pipe.ts"
  - "**/*.interceptor.ts"
  - "**/*.dto.ts"
  - "**/*.gateway.ts"
  - "**/*.resolver.ts"
  - "**/main.ts"
---

# NestJS rules

These add to `ts-core.md`. Follow the repo's module layout and naming first (rules D1, D2).

1. **Controllers translate, services decide.** A controller or resolver maps the request and response; business logic and data access live in providers.
2. Get dependencies by constructor injection. Do not `new` a provider. A provider used by another module is exported by its own module and that module is imported; do not declare it twice.
3. A circular dependency is a design problem: restructure before reaching for `forwardRef`.
4. **Every request body, query and parameter is validated** by the repo's pipe and DTOs. With `ValidationPipe`, an undecorated property is not validated; keep the repo's `whitelist` settings.
5. A new route states its authorisation: the guard the neighbours use, or an explicit public marker. Changing auth is an escalation (rule F2).
6. Throw the framework's HTTP exceptions or the repo's own, mapped by its filters. Do not return an error object with a success status.
7. Read configuration through the repo's config provider, not `process.env` inside a service.
8. Entities do not leave the API as they are: return the repo's response shape so internal fields stay inside.
9. Unit-test providers with `Test.createTestingModule` or plain construction, replacing only boundary providers; cover a new route end to end where the repo has e2e tests.
