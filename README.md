<div align="center">

# AI-Ultimate-Network

**An AI-first network config for developers who live in Claude, ChatGPT, GitHub & Gemini — on Shadowrocket, Clash Verge & Surge.**

Stable region-pinned routing for AI services · zero-config node management via regex · one source of truth, three clients · built, validated, and versioned like real software.

[![validate](https://github.com/yomixiba0225/AI-Ultimate-Network/actions/workflows/validate.yml/badge.svg)](https://github.com/yomixiba0225/AI-Ultimate-Network/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Shadowrocket](https://img.shields.io/badge/Shadowrocket-stable-blue)
![Clash Verge](https://img.shields.io/badge/Clash%20Verge-beta-orange)
![Surge](https://img.shields.io/badge/Surge-beta-orange)
![version](https://img.shields.io/badge/version-0.2.0-brightgreen)

</div>

---

## Why this exists

Most proxy configs dump every AI service into one generic `PROXY` policy pointed at whatever
node happens to be selected. That breaks AI workflows: Claude wants a **stable Taiwan IP**,
ChatGPT wants a **stable US IP**, and auto-speed-testing keeps changing both out from under you.

**AI-Ultimate** gives every AI service its own **Select-only** strategy group with a fixed
region, so:

- 🟣 **Claude → Taiwan** (never url-tests, never fails over, never load-balances)
- 🟢 **ChatGPT → US** (Singapore backup)
- ⚫ **GitHub → US / Japan**, 🔵 **Google/Gemini → Japan / Singapore**
- 🍎 **Apple → DIRECT** (App Store & iCloud always direct; Apple Intelligence toggleable)
- 🌐 **Everything else → Proxy**, 🇨🇳 **China → DIRECT**

And because groups pick nodes by **name regex**, adding a new airport node (e.g. `台湾107`)
means it *auto-joins the right group* — **zero config edits**.

> This is not a fork of `lazy.conf` with a few lines changed. It reverse-engineers the stock
> config (see [`docs/LAZY_ANALYSIS.md`](docs/LAZY_ANALYSIS.md)) and rebuilds the strategy /
> provider / regex layers it was missing.

---

## Supported clients

| Client | File | Platform | Status |
|---|---|---|---|
| **Shadowrocket** | [`config/AI-Ultimate.conf`](config/AI-Ultimate.conf) | iOS | ✅ stable |
| **Clash Verge** (Clash Meta core) | [`config/AI-Ultimate.clash.yaml`](config/AI-Ultimate.clash.yaml) | Windows / macOS / Linux | 🧪 beta |
| **Surge** | [`config/AI-Ultimate.surge.conf`](config/AI-Ultimate.surge.conf) | macOS / iOS | 🧪 beta |

All three are generated from the **same** `rules/*.list` + `scripts/strategy.py`, so the AI
strategy (separation, region pinning, regex node selection) is identical on every client — a
cross-client test guarantees they can't drift. Full per-client setup: **[`docs/USAGE.md`](docs/USAGE.md)**.

## Quick start (Shadowrocket)

1. **Add your airport subscription** in Shadowrocket (this is where your nodes come from).
   Make sure node names contain a region token — `TW / US / SG / JP` or `台湾 / 美国 / 新加坡 / 日本`.
2. **Import the config.** In Shadowrocket → Config → add from URL:
   ```
   https://raw.githubusercontent.com/yomixiba0225/AI-Ultimate-Network/main/config/AI-Ultimate.conf
   ```
3. **Pick your nodes once** in the `Claude`, `ChatGPT`, `GitHub`, `Google` groups. They stay put.
4. Done. New nodes you add later show up automatically in the matching groups.

> **Clash Verge / Surge users:** see **[`docs/USAGE.md`](docs/USAGE.md)** — one line to point at
> your airport subscription, then pick nodes in the same four groups.

---

## Strategy at a glance

| Group | Type | Region regex | Default | Rationale |
|---|---|---|---|---|
| **Claude** | `select` | `TW / Taiwan / 台湾` | Taiwan | Anthropic needs a stable IP; ADR-0001 |
| **ChatGPT** | `select` | `US / SG` | US | OpenAI region-gated; ADR-0002 |
| **GitHub** | `select` | `US / JP` | US residential | Stability; ADR |
| **Google** | `select` | `JP / SG` | Japan | Gemini/AI Studio; avoid HK; ADR |
| **Apple** | `select` | — | **DIRECT** | Apple Intelligence toggle; ADR-0003 |
| **Proxy** | `select` | `.*` | any node | Generic foreign sites |
| **Auto** | `url-test` | `.*` | lowest latency | Non-AI convenience only |
| **Final** | `select` | → Proxy/DIRECT | Proxy | Backs `FINAL` |

**AI groups are Select-only by design** — no `url-test`, `fallback`, or `load-balance`
(enforced by `scripts/validate.py`). See [ADR-0004](docs/adr/ADR-0004-select-only-ai.md).

**Rule order is a contract** (never reordered without a docs + CHANGELOG update):

```
Anthropic → OpenAI → GitHub → Google → Apple → China → Proxy → Final
```

---

## How it's built (configuration-as-code)

You never hand-edit the shipped configs. You edit the **rule providers** + **strategy**, then
one build emits all three clients:

```
scripts/strategy.py   ─┐                         ┌─▶ config/AI-Ultimate.conf         (Shadowrocket)
rules/anthropic.list   │   python3 scripts/build.py ─┼─▶ config/AI-Ultimate.clash.yaml   (Clash Verge)
rules/openai.list      ├────────────────────────▶ └─▶ config/AI-Ultimate.surge.conf   (Surge)
rules/*.list          ─┘   (Shadowrocket also uses config/AI-Ultimate.template.conf)
```

```bash
python3 scripts/build.py            # regenerate ALL client configs
python3 scripts/build.py --target clash   # or just one
python3 scripts/validate.py         # ≤10 groups, AI=select-only, refs, order, FINAL/MATCH-last — all clients
python3 -m unittest discover -s tests   # acceptance + cross-client consistency tests
```

CI runs build → freshness → validate → tests on every push/PR ([`.github/workflows/validate.yml`](.github/workflows/validate.yml)).

### Add an AI service in 30 seconds

1. Add its domains to the right `rules/*.list` (or create a new one).
2. `python3 scripts/build.py && python3 scripts/validate.py`
3. Commit. Done — no architectural change (see [`docs/DESIGN.md`](docs/DESIGN.md) §3).

---

## Project structure

```
AI-Ultimate-Network/
├── config/
│   ├── AI-Ultimate.conf            # ← GENERATED — Shadowrocket
│   ├── AI-Ultimate.clash.yaml      # ← GENERATED — Clash Verge / Meta
│   ├── AI-Ultimate.surge.conf      # ← GENERATED — Surge
│   ├── AI-Ultimate.template.conf   # Shadowrocket template (edit this)
│   └── lazy.conf                   # original baseline, kept for reference/rollback
├── rules/                          # per-vendor rule providers (shared source of truth)
│   ├── anthropic.list  openai.list  github.list  google.list
│   ├── apple.list  ai-extra.list  china.list  proxy.list
├── scripts/
│   ├── strategy.py                 # client-agnostic strategy (groups/regions/order)
│   ├── build.py                    # strategy + rules → all 3 client configs
│   └── validate.py                 # quality gate (all clients)
├── tests/test_config.py            # acceptance + cross-client consistency tests
├── docs/
│   ├── 01_PROJECT_CHARTER.md  02_PRD.md.md  03_ARCHITECTURE.md
│   ├── CONFIG_ANALYSIS.md  LAZY_ANALYSIS.md  GAP_ANALYSIS.md  DESIGN.md
│   ├── USAGE.md  IMPLEMENTATION_PLAN.md  ROADMAP.md
│   └── adr/                        # architecture decision records (ADR-0001…0007)
├── .github/                        # CI + issue/PR templates
├── CHANGELOG.md   LICENSE   .gitignore
```

---

## Compatibility & safety

- ✅ Imports into Shadowrocket with no syntax errors (validated).
- ✅ Preserves the baseline China-bypass behavior (Prefer Extension over Replacement).
- ♻️ **Rollback:** the original `config/lazy.conf` is kept intact; every change is a small
  commit; see [`docs/DESIGN.md`](docs/DESIGN.md) §10.
- 🔒 Your airport URLs and node lists are **never** committed (see `.gitignore`).

> `dns over proxy` for AI domains and `ipv6=false` are provided as **optional** P2 tweaks
> (commented in the template) — enable after validating against your own nodes.

---

## Roadmap

Multi-client generation (Shadowrocket / Clash Verge / Surge) shipped in v0.2.0. Next: richer
non-AI coverage for Clash/Surge, provider pinning, and device-verified promotion of the beta
clients to stable — see [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Documentation

Start with [`docs/DESIGN.md`](docs/DESIGN.md) for the architecture, then the ADRs in
[`docs/adr/`](docs/adr) for *why* each routing decision was made.

## Credits

Baseline rule-sets from [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
and the stock [Shadowrocket-ADBlock-Rules-Forever](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever)
`lazy.conf`. Strategy design, AI separation, regex node model, and tooling are original to this project.

## License

[MIT](LICENSE) © 2026 yomixiba0225
