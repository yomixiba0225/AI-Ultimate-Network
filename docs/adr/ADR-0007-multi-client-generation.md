# ADR-0007: Multi-client generation (Clash Meta / Verge, Surge) from one source

- **Status:** Accepted
- **Date:** 2026-07-08
- **Deciders:** Project owner (yomixiba0225)

## Context
v0.1.0 shipped Shadowrocket only. The Charter's long-term vision is an "AI-Ultimate Network
Stack" — one design, many clients (Clash Meta / Clash Verge on Windows/desktop, Surge). The
naive approach (hand-maintain a separate config per client) guarantees drift: a routing fix in
one client silently diverges from the others.

A second problem: the Shadowrocket config pulls per-service rule-sets from `blackmatrix7` remote
URLs. Those URLs differ per client (`/Shadowrocket/`, `/Clash/`, `/Surge/` folders), some lists
don't exist in every folder, and GitHub rate-limits verification. Depending on a fragile matrix
of ~30 per-client URLs would make Clash/Surge configs break unpredictably.

## Decision
1. **Single source of truth:** `scripts/strategy.py` holds the client-agnostic strategy (regions,
   groups, regex filters, canonical order). All three configs are generated from it +
   `rules/*.list` by `scripts/build.py`. A cross-client test asserts the AI region filters and
   group set are identical everywhere, so they cannot drift.
2. **Client-native geo mechanisms instead of remote URL matrices:**
   - **Clash Meta / Verge:** inline AI domains (precise Claude/ChatGPT separation) + `GEOSITE`
     (`github`, `apple`, `geolocation-cn`) + `GEOIP,CN` — all bundled with the core, no external
     rule-provider URLs to 404.
   - **Surge:** inline AI domains + `GEOIP,CN` + `FINAL`.
   The Shadowrocket config keeps its proven blackmatrix7 `RULE-SET` references (unchanged, in use).
3. **Node source per client:** Clash uses a `proxy-providers.airport` entry (user pastes their
   subscription URL once); Surge uses `include-all-proxies` over the user's Surge subscription;
   Shadowrocket uses its in-app subscription. All groups still select nodes by the same region
   regex.

## Consequences
- ✅ The **core value** (AI separation, region pinning, regex node selection) is byte-for-byte
  consistent across all three clients and cannot silently diverge (guarded by tests).
- ✅ Clash/Surge configs have **no fragile external rule-provider dependencies**; they rely on
  the client's built-in geodata.
- ⚠️ Clash/Surge have **coarser non-AI coverage** than Shadowrocket (GEOSITE/GEOIP vs curated
  per-service lists). Acceptable for v0.2.0; users can layer more rules. Tracked in ROADMAP.
- ⚠️ Clash/Surge are **beta**: generated to spec and structurally validated, but not yet
  device-verified by the maintainer. Documented in `docs/USAGE.md`.
- 🔗 Builds on [ADR-0005](ADR-0005-regex-node-selection.md) (regex nodes) and
  [ADR-0004](ADR-0004-select-only-ai.md) (AI select-only), now enforced on every client.
