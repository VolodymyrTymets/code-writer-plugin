# PR body template

```markdown
## <TICKET> <title>

### What changed
- ...

### Why
<the business reason, one or two lines; link the spec>
Spec: `docs/features/<TICKET>/spec.md` · Plan: `docs/features/<TICKET>/plan.md`

### Contract impact
- API: none | <endpoint> <breaking?> <consumers updated in this PR?>
- Shared types: none | regenerated with `<command>`

### Verification
<the evidence block - see evidence-format.md>

### Not verified
- ...

### Review focus
<the two or three places a reviewer should look hardest, and why>

### Docs
- [ ] spec acceptance criteria ticked
- [ ] ARCHITECTURE.md / DOMAIN_GLOSSARY.md / ADR (or "no change needed")
```

Opened as a **draft**. A human marks it ready.
