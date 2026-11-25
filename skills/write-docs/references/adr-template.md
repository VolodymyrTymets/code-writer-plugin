# ADR template

```markdown
# ADR-<NNN> — <decision in a short imperative phrase>

- **Date:** <YYYY-MM-DD>
- **Status:** accepted | superseded by ADR-<NNN> | deprecated
- **Deciders:** <names/roles>
- **Ticket:** <TICKET>

## Context
<the forces: the requirement, the constraint, what made this a decision rather than an obvious step>

## Decision
<what we will do, in one paragraph, present tense: "We use X for Y.">

## Rejected alternatives
| Alternative | Why not |
|-------------|---------|
| <B> | <the real reason, not "we liked X more"> |
| <C> | ... |

## Consequences
- Positive: ...
- Negative / accepted cost: ...
- Follow-ups: <tickets this creates>

## Revisit when
<the condition that would make us reopen this — a scale threshold, a library release, a client requirement>
```

Numbering is sequential and never reused. Keep it under a page: an ADR nobody reads defeats the purpose.
