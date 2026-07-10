# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Shadowrocket TUN: WeChat could stall at “获取消息中”.** Shadowrocket now defaults to
  `ipv6=false`, avoiding unstable carrier/router IPv6 paths while keeping WeChat `DIRECT`.
- Replaced the accepted-but-cross-client Quantumult X WeChat source with the native Shadowrocket
  rule-set so the provider syntax matches the consuming client.

## [0.3.0] - 2026-07-08

Strategy rebalance (user request). Region assignments changed and a new group added; still
9 groups (≤10). All clients regenerated from `strategy.py`; cross-client parity tests updated.

### Added
- **TikTok** strategy group (Select-only) → Japan / Taiwan / Singapore. New `rules/tiktok.list`
  + `GEOSITE,tiktok` routing on Clash; the Shadowrocket TikTok rule-set moved from `Proxy` to
  the TikTok group. New region **HK** (Hong Kong) added to the region regex table.

### Changed
- **ChatGPT** (covers Codex — one group): US → **US / SG / JP / HK**.
- **GitHub**: US/JP → **HK**.
- **Google**: JP/SG → **HK / JP / SG / US** (HK now allowed, superseding the earlier avoid-HK note).
- Claude unchanged (Taiwan). See `docs/adr/ADR-0008-region-rebalance.md`.

## [0.2.4] - 2026-07-08

### Changed
- **Global Script is now multi-airport-fusion ready.** The AI groups in
  `config/AI-Ultimate.clash-script.js` build with `include-all: true` + `filter` instead of a
  list derived from `config.proxies`. Nodes fused in via `proxy-providers` (a second/third
  airport) live in the provider, not `config.proxies`, so the old approach missed them;
  `include-all` pulls from the main subscription **and** every fused provider. Each AI group keeps
  a `proxies: [Proxy]` fallback so a region with no node can't break the config. `docs/USAGE.md`
  gains a multi-airport fusion note.

## [0.2.3] - 2026-07-08

### Added
- **Clash Verge Global Script** delivery: `config/AI-Ultimate.clash-script.js` (`build.py
  --target clash-script`). Builds the AI groups from the live node list inside the enhance stage,
  so it is immune to the failure mode where an existing Global Script runs after the Merge and
  drops the merged proxy-groups. Recommended for multi-subscription users who already run a
  Global Script (e.g. an Adobe block). Empty region → falls back to `Proxy` (never DIRECT);
  `\bUS\b` guard verified to not match `AUS`. `docs/USAGE.md` §2A-Script documents it.

## [0.2.2] - 2026-07-08

### Fixed
- **Clash: empty region group could reject the whole config.** Mihomo refuses to load a config
  containing an empty proxy-group. On a single-region airport (e.g. a Taiwan-only accelerator),
  the `ChatGPT/GitHub/Google` groups matched no nodes → Mihomo dropped the entire config and
  Clash Verge silently fell back to the base profile (our groups never appeared). Each AI region
  group now carries a `proxies: [Proxy]` fallback so it is never empty; missing a region falls
  back to a working proxied node (never DIRECT). Applies to both `AI-Ultimate.clash.yaml` and the
  `AI-Ultimate.clash-merge.yaml` overlay.

## [0.2.1] - 2026-07-08

### Added
- **Clash Verge Global Merge overlay**: `config/AI-Ultimate.clash-merge.yaml`. Paste once into
  Clash Verge's *全局扩展覆写配置 (Global Merge)* and the AI groups + rules apply on top of
  **every** subscription profile automatically — ideal for users with **multiple subscriptions**
  on macOS and Windows. Groups use `include-all: true` (pull nodes from the active profile), so
  there are no node URLs and no per-subscription copy-paste. Prepends rules only; coexists with a
  Global Script (e.g. Adobe blocking) and leaves each profile's own final policy intact.
- `build.py --target clash-merge`; validation + tests for the overlay (no MATCH/FINAL allowed).
- `docs/USAGE.md` §2A documents the multi-subscription Global Merge workflow.

## [0.2.0] - 2026-07-08

Multi-client release. The same AI-first strategy now generates configs for three clients from
one source of truth.

### Added
- **Clash Meta / Clash Verge** config: `config/AI-Ultimate.clash.yaml` (Windows / macOS / Linux).
  Region-regex node selection via `proxy-providers` + group `filter`; AI routing inlined; bulk
  routing via built-in `GEOSITE` / `GEOIP` (no fragile external rule lists).
- **Surge** config: `config/AI-Ultimate.surge.conf` (macOS / iOS). `include-all-proxies` +
  `policy-regex-filter`; AI inlined; `GEOIP,CN` + `FINAL`.
- `scripts/strategy.py` — single client-agnostic source of truth (regions, groups, order) shared
  by all emitters.
- `scripts/build.py --target {shadowrocket,clash,surge}` multi-target build (default: all).
- Cross-client consistency tests: AI region filters and group set must be identical on every
  client (they can't silently drift).
- `docs/USAGE.md` (per-client setup) and `docs/adr/ADR-0007-multi-client-generation.md`.
- CI installs PyYAML and validates the Clash YAML parses.

### Changed
- `scripts/validate.py` now validates all three client configs (Shadowrocket, Clash, Surge).
- README documents supported clients and the one-source-three-clients build.

### Notes
- Shadowrocket config is **unchanged** (byte-identical) — existing users are unaffected.
- Clash Verge and Surge are **beta**: generated to spec and structurally validated, but not yet
  device-verified by the maintainer.

## [0.1.0] - 2026-07-08

First engineered release. Turns the stock `lazy.conf` into an AI-first, buildable,
validated configuration project.

### Added
- **8 strategy groups** (≤10 cap): `Claude`, `ChatGPT`, `GitHub`, `Google`, `Proxy`, `Auto`,
  `Apple`, `Final`. AI groups are **Select-only** (no url-test/fallback/load-balance).
- **Per-vendor rule providers** in `rules/` (`anthropic`, `openai`, `github`, `google`,
  `apple`, `ai-extra`, `china`, `proxy`), replacing the single bundled `AI.txt`.
- **Regex node selection** (`policy-regex-filter`) with `\bXX\b` region matching so new nodes
  auto-join the right group with zero config edits; US never matches AUS.
- **Configuration-as-code build**: `scripts/build.py` expands `#!INCLUDE` markers from a
  template + providers into `config/AI-Ultimate.conf`.
- **Validation gate**: `scripts/validate.py` (syntax, ≤10 groups, AI select-only, dangling
  refs, regex compile, duplicate rules, FINAL-last, canonical order).
- **Acceptance tests**: `tests/test_config.py` (stdlib unittest, 13 tests).
- **CI**: `.github/workflows/validate.yml` runs build → freshness check → validate → tests.
- **Docs**: `CONFIG_ANALYSIS`, `LAZY_ANALYSIS`, `GAP_ANALYSIS`, `DESIGN`, `IMPLEMENTATION_PLAN`,
  `ROADMAP`, ADR-0001…0006, README, LICENSE (MIT), issue/PR templates.

### Changed
- **Canonical rule order** enforced: Anthropic → OpenAI → GitHub → Google → Apple → China →
  Proxy → Final.
- **Claude and ChatGPT are now separated**: independent groups and providers (previously both
  went to the same global node via `AI.txt`).
- **Apple routing corrected**: App Store / iCloud stay `DIRECT`; only Apple Intelligence /
  Private-Relay domains route through the toggleable `Apple` group (default DIRECT).
  Previously these were proxied via `AI.txt`.
- **`FINAL`** now targets the `Final` group instead of a bare `PROXY` literal.
- **`update-url`** re-pointed from the upstream third-party `lazy.conf` to this repo's own
  built config, removing the overwrite-on-refresh hazard.

### Removed
- The bundled `iab0x00/ProxyRules/AI.txt` rule-set (superseded by per-vendor providers).

### Preserved
- Stock China-bypass behavior, CN service DIRECT lists, `[Host]`, `[URL Rewrite]`, `[MITM]`,
  `skip-proxy`, `hijack-dns`, `block-quic=all-proxy`. Original baseline kept at
  `config/lazy.conf` for reference and rollback.

[0.3.0]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.3.0
[0.2.4]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.2.4
[0.2.3]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.2.3
[0.2.2]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.2.2
[0.2.1]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.2.1
[0.2.0]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.2.0
[0.1.0]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v0.1.0
