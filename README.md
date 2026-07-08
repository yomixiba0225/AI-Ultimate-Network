<div align="center">

# AI-Ultimate-Shadowrocket

**An AI-first Shadowrocket configuration for developers who live in Claude, ChatGPT, GitHub & Gemini.**

Stable region-pinned routing for AI services · zero-config node management via regex · built, validated, and versioned like real software.

[![validate](https://github.com/yomixiba0225/AI-Ultimate-Shadowrocket/actions/workflows/validate.yml/badge.svg)](https://github.com/yomixiba0225/AI-Ultimate-Shadowrocket/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Shadowrocket](https://img.shields.io/badge/Shadowrocket-compatible-blue)
![version](https://img.shields.io/badge/version-1.0.0-brightgreen)

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

## Quick start

1. **Add your airport subscription** in Shadowrocket as usual (this is where your nodes come from).
   Make sure node names contain a region token — `TW / US / SG / JP` or `台湾 / 美国 / 新加坡 / 日本`.
2. **Import the config.** In Shadowrocket → Config → add from URL:
   ```
   https://raw.githubusercontent.com/yomixiba0225/AI-Ultimate-Shadowrocket/main/config/AI-Ultimate.conf
   ```
   (or download [`config/AI-Ultimate.conf`](config/AI-Ultimate.conf) and import the file).
3. **Pick your nodes once.** Open the `Claude`, `ChatGPT`, `GitHub`, `Google` groups and select a
   node in each. They stay put — no auto-switching.
4. Done. New nodes you add later show up automatically in the matching groups.

> **Optional — pin a preferred node.** To make a group default to a specific node (e.g. Berry
> Hinet for Claude), add one line in `config/AI-Ultimate.template.conf`:
> `Claude = select, policy-regex-filter=..., policy-select-name=<exact node name>` then rebuild.

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

You never hand-edit the shipped config. You edit the **template** and the **rule providers**,
then run the build:

```
config/AI-Ultimate.template.conf   ─┐
rules/anthropic.list                │   python3 scripts/build.py
rules/openai.list                   ├──────────────────────────▶  config/AI-Ultimate.conf
rules/github.list  ...              │   (expands #!INCLUDE markers)
rules/*.list                       ─┘
```

```bash
python3 scripts/build.py            # regenerate config/AI-Ultimate.conf
python3 scripts/validate.py         # syntax, ≤10 groups, AI=select-only, refs, order, FINAL-last
python3 -m unittest discover -s tests   # acceptance tests
```

CI runs all three on every push/PR ([`.github/workflows/validate.yml`](.github/workflows/validate.yml)).

### Add an AI service in 30 seconds

1. Add its domains to the right `rules/*.list` (or create a new one).
2. `python3 scripts/build.py && python3 scripts/validate.py`
3. Commit. Done — no architectural change (see [`docs/DESIGN.md`](docs/DESIGN.md) §3).

---

## Project structure

```
AI-Ultimate-Shadowrocket/
├── config/
│   ├── AI-Ultimate.conf            # ← GENERATED, import this
│   ├── AI-Ultimate.template.conf   # ← edit this
│   └── lazy.conf                   # original baseline, kept for reference/rollback
├── rules/                          # per-vendor rule providers (source of truth)
│   ├── anthropic.list  openai.list  github.list  google.list
│   ├── apple.list  ai-extra.list  china.list  proxy.list
├── scripts/
│   ├── build.py                    # template + rules  → config
│   └── validate.py                 # quality gate
├── tests/test_config.py            # acceptance tests (stdlib unittest)
├── docs/
│   ├── 01_PROJECT_CHARTER.md  02_PRD.md.md  03_ARCHITECTURE.md
│   ├── CONFIG_ANALYSIS.md  LAZY_ANALYSIS.md  GAP_ANALYSIS.md  DESIGN.md
│   ├── IMPLEMENTATION_PLAN.md  ROADMAP.md
│   └── adr/                        # architecture decision records
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

Multi-client generation (Clash Meta / Verge / Surge) from the same providers is planned — see
[`docs/ROADMAP.md`](docs/ROADMAP.md).

## Documentation

Start with [`docs/DESIGN.md`](docs/DESIGN.md) for the architecture, then the ADRs in
[`docs/adr/`](docs/adr) for *why* each routing decision was made.

## Credits

Baseline rule-sets from [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
and the stock [Shadowrocket-ADBlock-Rules-Forever](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever)
`lazy.conf`. Strategy design, AI separation, regex node model, and tooling are original to this project.

## License

[MIT](LICENSE) © 2026 yomixiba0225
