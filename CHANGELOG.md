# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-08

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

[1.0.0]: https://github.com/yomixiba0225/AI-Ultimate-Network/releases/tag/v1.0.0
