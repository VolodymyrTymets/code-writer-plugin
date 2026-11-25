# Discovery checklist

One silent pass, before the first question. The order matters: the later items are cheap to read only once the
earlier ones have told you what to look for.

## The documents

| # | Read | What you are taking from it | If it is missing |
|---|------|------------------------------|------------------|
| 1 | `docs/BUSINESS_MODEL.md` | The **ranked** goals and the non-negotiables. This is your tie-breaker when two designs are both defensible. | Say so in the plan and state which goal you assumed. An unranked list cannot break a tie. |
| 2 | `docs/ARCHITECTURE.md` | Where this kind of code belongs, and which layer may call which. | Derive it from the precedent (#6) and flag that the plan is guessing. |
| 3 | `docs/DOMAIN_GLOSSARY.md` | The exact words for names, columns, events and user-facing copy. | Harvest the terms the code already uses and propose the glossary entry as part of the plan. |
| 4 | `docs/decisions/` | Anything already settled near this change. **A settled decision is not reopened** (rule D1). | — |
| 5 | The ticket | Acceptance criteria, the actual user, what was rejected. | Ask for the acceptance criteria. This is a genuine gap. |

Grep `docs/decisions/` by the domain noun, not by the ticket ID — an ADR that constrains you was written for an
older ticket.

## The code

| # | Read | What you are taking from it |
|---|------|------------------------------|
| 6 | **The nearest existing implementation of the same shape** — the closest module, screen or endpoint | The pattern you will follow, with a path. Use Serena (`find_symbol`, `find_referencing_symbols`) or a codebase-map skill; do not read whole directories. |
| 7 | The tests around that code | The real contract — what callers depend on, what the team considers worth asserting, which fixtures exist. |
| 8 | The rule files whose `paths:` match the files you are about to touch | The constraints the gate will check you against. Reading them now is cheaper than a BLOCK later. |

## What you owe the reader before asking anything

Two or three lines, no more:

- the precedent you will follow, **with its path**, and one clause on why it is the right one
- the layer(s) the change lands in
- anything in #1–#5 you could not find

**No precedent found is itself a finding.** Say it out loud — a change with no precedent is either a new pattern
(which needs an ADR, rule D1) or a sign you are looking in the wrong place. Silence here is how a second pattern for
the same problem gets into a codebase.

## Stop conditions

Stop reading and start planning as soon as you can name the precedent and the layer. Discovery that keeps going
after that is context spend with no decision attached to it — and the plan is what the gate reads, not your notes.
