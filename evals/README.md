# Skill evals

Each P0 skill should get an eval case before it changes again, so a rewrite cannot silently regress triggering
or output shape. Run in CI on any PR touching `skills/**`.

```bash
claude plugin validate ./ --strict
claude plugin eval ./          # runs the cases in this directory
```

Minimum per skill: one case that must trigger it, one near-miss that must **not**, and one output-shape
assertion (e.g. `analyze-plan` must emit a PASS/BLOCK verdict with rule IDs).

Priority order for writing them: `analyze-plan` (it is a gate), `develop-feature` (it orchestrates),
`setup-project` (it runs once and is hard to undo), then the stack skills.
