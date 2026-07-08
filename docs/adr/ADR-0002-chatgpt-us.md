# ADR-0002: ChatGPT routes to US (Singapore backup), Select-only

- **Status:** Accepted
- **Date:** 2026-07-08

## Context
OpenAI/ChatGPT is region-gated and sensitive to IP reputation. The user wants a **stable US**
exit (ToLink ChatGPT US line) with **Singapore** as a manual backup, never automatic switching.

## Decision
- Dedicated **`ChatGPT`** group, type **`select`**.
- Region regex `(?i)(\bUS\b|USA|美国|美國|\bSG\b|Singapore|新加坡|狮城)` — US primary intent,
  SG available as a manual alternative in the same group.
- Route `rules/openai.list` (openai.com, chatgpt.com, sora.com, oai* CDNs, keywords) here.

## Consequences
- ✅ ChatGPT pinned to a stable US IP; SG selectable without editing config.
- ✅ Distinct from Claude — the two never share a policy (core mission).
- ⚠️ `\bUS\b` avoids matching `AUS`/Austria; verified in `scripts/validate.py` regex check and
  `tests/`.
- 🔗 Select-only per [ADR-0004](ADR-0004-select-only-ai.md).
