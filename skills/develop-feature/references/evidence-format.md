# Evidence block

Paste the real output. Truncate long logs to the informative lines, never invent them. Commands come from
the command map in `CLAUDE.md`.

```markdown
### Verification
- lint: `<lint command>` → 0 warnings, 0 errors
- tests: `<affected tests command>` → 34 passed, 0 failed (2 new)
- executed: POST /v1/orders → 201, body: {"id":"ord_123","status":"PENDING"}
- executed: POST /v1/orders with an empty cart → 422, code `CART_EMPTY`
- executed (UI): order confirmation screen reached via Cart → Checkout → Pay; screenshot below; no new console errors
- data change: applied locally, `select status from orders limit 1` → 'PENDING'; rollback: drop the column while nothing reads it

### Not verified
- The second platform build — no device available in this session
- Behaviour above 1k concurrent orders — out of scope for this ticket
```

Rules:

- Every line names the **command** and its **result**. A command without a result is a claim, not evidence.
- `### Not verified` is never omitted while anything is unverified (rule B2). Write "nothing" only if that is true.
- The `evidence-check` CI job fails the PR when this block is missing or empty.
