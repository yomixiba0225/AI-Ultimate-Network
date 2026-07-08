# ADR-0001: Claude routes to a fixed Taiwan node, Select-only

- **Status:** Accepted
- **Date:** 2026-07-08
- **Deciders:** Project owner (yomixiba0225)

## Context
Anthropic/Claude behaves best behind a **stable IP in an eligible region**. Auto-speed-testing
rotates IPs, which can trigger re-verification, degraded sessions, or region flaps. The user's
preferred line is Taiwan (Berry Hinet), with ToLink Taiwan as backup.

## Decision
- Create a dedicated **`Claude`** strategy group of type **`select`** (manual).
- Populate it by **region regex** `(?i)(\bTW\b|Taiwan|台湾|台灣)` — no hardcoded node names.
- Default = first matching Taiwan node; optional `policy-select-name=` pins Berry Hinet when the
  exact node name is known.
- Route `rules/anthropic.list` (claude.ai, anthropic.com, …) to this group.

## Consequences
- ✅ Claude stays on one Taiwan IP until the user changes it manually.
- ✅ Adding/removing TW nodes needs no config change.
- ⚠️ If the user's airport has **no** TW node, the group is empty — documented in README; the
  user must add a TW node or pin another region.
- 🔗 Enforced Select-only by [ADR-0004](ADR-0004-select-only-ai.md) and `scripts/validate.py`.
