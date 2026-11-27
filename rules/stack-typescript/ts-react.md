---
description: React component and hook rules - hooks, effects, state, keys, component boundaries.
paths:
  - "**/*.tsx"
  - "**/use*.ts"
  - "**/hooks/**/*.ts"
---

# React rules

These apply to React on any renderer and add to `ts-core.md`. Follow the repo's component, state and data-fetching patterns first (rules D1, D2).

1. **Rules of Hooks:** call hooks at the top level of a component or another hook, never in a condition, loop or callback.
2. **No effect for derived data.** Compute it during render. Handle a user action in its event handler. An effect is for synchronising with something outside React.
3. An effect that subscribes, opens or starts something returns a cleanup. Its dependency list is complete; do not silence the hooks lint rule (rule B3).
4. Keep state minimal and where it is used: store an id, not a copy of the object; lift it only when two components need it. Never mutate state or props.
5. List keys are stable ids from the data, not the array index, when items can move, be added or removed.
6. Server data goes through the repo's data layer, not a new ad-hoc fetch inside an effect.
7. Type props explicitly. Do not define a component inside another component.
8. Add `useMemo`, `useCallback` or `memo` for a measured problem or an existing repo convention, not by reflex.
9. Test what the user sees and does with the repo's testing library; do not assert on internal state.
