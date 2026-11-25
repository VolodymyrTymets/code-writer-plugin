# Greenfield interview

Batch these. Skip anything the repo already answered in step 1. Target: under 15 minutes of the human's time.

## Round 1 — the product (required for BUSINESS_MODEL.md)
1. What is this product, in two sentences, and for whom?
2. **Rank** the top three goals (e.g. 1 time-to-market, 2 correctness of billing, 3 polish). The ranking is the tie-breaker for every later judgement call — an unranked list is useless here.
3. Non-negotiables: what must never happen? (data loss, downtime in business hours, a wrong charge, a privacy breach)
4. Explicitly out of scope for this phase?
5. Client-facing language: which words does the client use for the core nouns?

## Round 2 — the stack (confirm what you read; ask only the gaps)
6. Which deployable units live in this repo, and how are they laid out?
7. Which language runtimes, and where is each version pinned?
8. Which dependency manager, and which task runner (if any)?
9. Per unit: the main framework, the data layer, the boundary format (HTTP/GraphQL/queue/CLI), the persistence layer.
10. The test tooling per level: unit, integration, end to end.
11. **The command map** — install, lint, unit tests, affected tests, build, dev, e2e. Run each one to confirm it works; a command map with a wrong entry is worse than an empty one.
12. Environments: local, staging, production — how each is reached and what the agent may touch (local and staging only, rule C5).
13. **Which stack layer applies?** Already answered in step 1.5, so do not ask again. For each chosen stack, step 4.5 detects the tooling: confirm the dependency manager, the runtime version, the linter and the test runner. For `Stacks: none`, note which rules this repo will need in `.claude/rules/` and who writes them.

## Round 3 — process
14. Protected branches and the branch naming convention.
15. Tracker and ticket ID format (used in branch names and commits).
16. Definition of done additions beyond rule B1?
17. Who reviews, and what must never merge without a specific person?
18. Design source, if any — should a design tool MCP be enabled?
19. Tooling consent: which MCP servers may reach client systems (error tracking, tracker, database)? Who approved? → `docs/AGENT_TOOLING.md`.

## Round 4 — one open question
20. "What has gone wrong on similar projects that you want the agent to never repeat?" — the answers become the first project-specific rules, and they are usually the most valuable lines in the whole file.
