# ROADMAP.md

**Project:** AI-Ultimate-Network
Semantic Versioning. Dates are targets, not commitments.

---

## v0.1.0 — AI-first Shadowrocket ✅ (2026-07-08)

- 8 strategy groups, AI Select-only, regex node selection.
- Per-vendor rule providers; build + validate + tests + CI.
- Full docs + ADRs. See `CHANGELOG.md`.

## v0.2.0 — Multi-client generation ✅ (2026-07-08)

- **Clash Meta / Clash Verge** and **Surge** configs generated from the same
  `scripts/strategy.py` + `rules/` providers (per-client emitters, GEOSITE/GEOIP native).
- `scripts/build.py --target {shadowrocket,clash,surge}`; cross-client consistency tests.
- `docs/USAGE.md`, ADR-0007. Shared design, one source of truth — no divergent hand files.

---

## v0.3.0 — Promote beta clients to stable (next)

- **Device-verify** Clash Verge (Windows) and Surge on real airports; fix regex/geo edge cases.
- Richer non-AI coverage for Clash/Surge (optional per-service rule-providers behind a flag).
- Region regex hardening + a `scripts/` helper that lints a pasted node list against the regexes.

## v0.4.0 — Coverage & robustness

- Expand Anthropic/OpenAI domain coverage (assets/CDN) from observed traffic.
- Optional **dns-over-proxy** profile enabled + validated for AI domains (currently commented).
- Continue the Shadowrocket `ipv6=false` A/B; Clash delivery modes now default IPv6 off.
- Optional dedicated groups for Perplexity / Grok if usage justifies (still ≤10).

## v0.5.0 — Provider hygiene

- Pin remote rule-sets to commits (reduce upstream drift; GAP G13).
- `scripts/update-rulesets.py` to refresh/pin remote lists reproducibly.
- Ad-block / REJECT group (optional, off by default).

## v1.0.0 — Stable, device-verified across all three clients

- All clients device-verified and promoted to stable; API/coverage frozen for a major line.

## Later

- GitHub Release automation (tag → notes from CHANGELOG).
- Screenshots / GIF of group selection in `assets/`.
- Per-region latency notes and recommended node picks.
