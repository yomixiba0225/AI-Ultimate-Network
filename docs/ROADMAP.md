# ROADMAP.md

**Project:** AI-Ultimate-Network
Semantic Versioning. Dates are targets, not commitments.

---

## v0.1.0 — AI-first Shadowrocket ✅ (2026-07-08)

- 8 strategy groups, AI Select-only, regex node selection.
- Per-vendor rule providers; build + validate + tests + CI.
- Full docs + ADRs. See `CHANGELOG.md`.

---

## v1.1.0 — Coverage & robustness (next)

- Expand Anthropic/OpenAI domain coverage (assets/CDN) from observed traffic.
- Optional **dns-over-proxy** profile enabled + validated for AI domains (currently commented).
- `ipv6=false` A/B evaluation for AI-endpoint stability.
- Region regex hardening against more airport naming schemes; add a `scripts/` helper that
  lints a pasted node list against the region regexes.
- Optional dedicated groups for Perplexity / Grok if usage justifies (still ≤10).

## v1.2.0 — Provider hygiene

- Pin remote rule-sets to commits (reduce upstream drift; GAP G13).
- Add a `scripts/update-rulesets.py` to refresh/pin remote lists reproducibly.
- Ad-block / REJECT group (optional, off by default).

## v2.0.0 — Multi-client generation (AI-Ultimate Network Stack)

- Generate **Clash Meta / Clash Verge** configs from the same `rules/` providers via a
  `scripts/build.py --target clash` backend (proxy-groups + rule-providers mapping).
- **Surge** target (planned).
- Shared design, one source of truth, per-client emitters — no divergent hand-maintained files.

## Later

- GitHub Release automation (tag → notes from CHANGELOG).
- Screenshots / GIF of group selection in `assets/`.
- Per-region latency notes and recommended node picks.
