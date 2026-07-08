# ADR-0003: Apple is DIRECT; Apple Intelligence is a toggle, not proxied by default

- **Status:** Accepted
- **Date:** 2026-07-08

## Context
The stock baseline bundled Apple Intelligence / Private-Relay / Siri domains
(`guzzoni.apple.com`, `apple-relay.*`, `smoot.apple.com`, …) into `AI.txt` → **PROXY**. The
project mandates **Apple → DIRECT** (PRD §13, FR-005). But Apple Intelligence is geo-gated and
some users *do* want it proxied. Proxying **all** of Apple (App Store, iCloud) would be wrong
and can break Apple services / Private Relay.

## Decision
- **App Store / iCloud / general Apple** → hardcoded **DIRECT** (remote Apple rule-set targets
  `DIRECT` literally; `[Host]` keeps `*.apple.com`/`*.icloud.com` on system DNS).
- **Apple Intelligence / Private-Relay** domains (`rules/apple.list`) → the **`Apple`** group,
  defined as `select, DIRECT, Proxy` with **DIRECT as default**.
- Result: default behavior = everything Apple direct (spec-compliant). A user who wants Apple
  Intelligence flips just the `Apple` group to `Proxy` — one tap, no config edit, and it does
  **not** affect the App Store.

## Consequences
- ✅ Spec-compliant default (Apple direct) while preserving the geo-gated-AI escape hatch.
- ✅ Flipping the toggle can't accidentally proxy the App Store.
- ⚠️ The group name "Apple" governs only the Intelligence/Relay subset; documented in README and
  `rules/apple.list`.
