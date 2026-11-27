---
description: React Native rules - native components, lists, platform differences, secrets, native projects, verification.
paths:
  - "**/*.tsx"
  - "**/*.ios.ts"
  - "**/*.android.ts"
  - "**/app.json"
  - "**/app.config.*"
  - "**/metro.config.*"
---

# React Native rules

These add to `ts-core.md` and the React rules. Follow the repo's navigation, styling and state patterns first (rules D1, D2).

1. Use native components: no HTML elements, and every string is inside a `<Text>`.
2. Long or unbounded lists use `FlatList` / `SectionList` (or the repo's list component) with a stable `keyExtractor`, not `map` inside a `ScrollView`.
3. Platform differences go through `Platform` or `.ios.` / `.android.` files; check the change on every platform the repo ships, and say which you could not (rule B2).
4. Respect safe areas and the keyboard the way neighbouring screens do.
5. **The app bundle is public.** No secrets in code or in bundled environment variables; tokens go to the repo's secure storage, not plain async storage (rule A6).
6. Generated `ios/` and `android/` folders are not hand-edited when the repo generates them from config; change the config and regenerate (rule C3). A new native dependency needs approval and a rebuild (rule C2).
7. Do not block the JavaScript thread: heavy work is deferred or moved off it, following the repo's approach.
8. Store submissions and over-the-air updates are human actions (rule C4).
