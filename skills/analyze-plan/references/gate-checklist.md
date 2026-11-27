# Gate checklist

## 1. Completeness vs the spec
- [ ] Every acceptance criterion maps to at least one requirement
- [ ] Every requirement maps to an acceptance criterion (no invented scope — rule C1)
- [ ] Edge cases from the spec appear in the plan or are explicitly deferred
- [ ] Out-of-scope items really are absent from the plan

## 2. Constitution
- [ ] **B1** every requirement states how it will be **executed**, not only tested
- [ ] **B5** evidence type named per requirement (screenshot / request-response / failing-then-passing test)
- [ ] **C1** no refactors, renames, formatting or version bumps riding along
- [ ] **C2** no new runtime dependency without an approval line
- [ ] **C3** no writes to protected paths (generated code, vendored and build output). First read every `.claude/rules/protected-paths*.md`: they are not in context on their own
- [ ] **C4/C5** no destructive or production-touching step
- [ ] **D1** an existing precedent is named, or an ADR is planned for the new pattern
- [ ] **E1** doc updates listed in the same PR
- [ ] **A4** one PR, opened as a draft

## 3. Architecture and layering
- [ ] Files land where `ARCHITECTURE.md` says they belong
- [ ] The layering the repo already uses is respected; no layer skipped without an ADR
- [ ] No module reaches into another module's internals — only its public surface
- [ ] The rules in `.claude/rules/` that match the touched paths are satisfied (the stack pack owns those)
- [ ] Anything the plan introduces as a *new* pattern is flagged for an ADR

## 4. Contracts and data
- [ ] Boundary changes flagged as breaking or additive, with the consumer list
- [ ] Regeneration step present for anything generated from the contract
- [ ] A change to a persisted format or stored data says how existing data is handled, with a rollback note
- [ ] Consumers that cannot be updated in lockstep (shipped devices, third parties) accounted for

## 5. Business fit
- [ ] The plan serves the ranked goal it claims to serve
- [ ] Where two valid options collided, the choice matches the ranking in `BUSINESS_MODEL.md`
- [ ] Nothing contradicts a non-negotiable
- [ ] No settled ADR is silently reopened

## 6. Risk and size
- [ ] Requirements are independently verifiable and commit-sized
- [ ] The riskiest unknown is addressed first, not last
- [ ] Nothing in the plan needs prod access, client credentials, or data the agent may not read
