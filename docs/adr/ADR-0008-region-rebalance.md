# ADR-0008: Region rebalance + TikTok group (v0.3.0)

- **Status:** Accepted (supersedes the region specifics in ADR-0002 for ChatGPT and the
  "avoid HK for Google" note in the DESIGN region table)
- **Date:** 2026-07-08
- **Deciders:** Project owner (yomixiba0225)

## Context
After real use across a Taiwan/HK/JP/SG airport (蓝莓桥 + ToLink), the owner refined which
regions each service should draw from. The earlier defaults (ChatGPT US/SG, GitHub US/JP,
Google JP/SG, no HK) didn't match the available high-quality nodes.

## Decision
Region assignments (region regex, all groups Select-only):

| Group | Regions | Note |
|---|---|---|
| Claude | TW | unchanged |
| ChatGPT | US, SG, JP, HK | **one group covering Codex + ChatGPT** (all OpenAI) |
| GitHub | HK | |
| Google | HK, JP, SG, US | HK now allowed |
| **TikTok** (new) | JP, TW, SG | region-sensitive; keep a stable exit |
| Proxy / Auto | all | |
| Apple | DIRECT / Proxy | unchanged |

New region **HK** added: `\bHK\b | Hong ?Kong | 香港`. TikTok routing seeded in
`rules/tiktok.list` (+ `GEOSITE,tiktok` on Clash). Total groups = 9 (≤10, ARCH §7).

## Consequences
- ✅ Matches the owner's actual node pool; ChatGPT/Codex unified as requested.
- ✅ Generated identically for Shadowrocket, Clash (yaml/merge/script) and Surge from
  `strategy.py`; cross-client parity tests updated.
- ⚠️ HK for Google/GitHub is a deliberate owner choice; HK is generally fine for these but not
  for Anthropic (Claude stays TW-only). Revisit per-service if a region degrades.
- 🔗 Builds on [[ADR-0004]] (AI Select-only) and [[ADR-0007]] (multi-client generation).
