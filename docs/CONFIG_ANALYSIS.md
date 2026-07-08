# CONFIG_ANALYSIS.md

**Phase:** 1 — Repository Analysis
**Project:** AI-Ultimate-Shadowrocket
**Baseline analyzed:** `lazy.conf` (336 lines, 24,332 bytes)
**Date:** 2026-07-08
**Status:** Analysis only — **no files were modified**

---

## 0. How to read this document

This is a *reverse-engineering* report of the repository **as it exists today**, before any
AI-Ultimate work begins. It intentionally does **not** propose the new design (that is
`DESIGN.md`, Phase 4) and does **not** rank the current-vs-target deltas (that is
`GAP_ANALYSIS.md`, Phase 3). It describes what is here, how it works, and where it is weak.

---

## 1. Project summary

### 1.1 What this repository currently *is*

At this moment the repository is a **documentation-and-baseline** stage of a project, not yet
an implemented product. It contains:

| Layer | Present? | Notes |
|---|---|---|
| Vision / requirements docs | ✅ | `01_PROJECT_CHARTER.md`, `02_PRD.md.md`, `03_ARCHITECTURE.md` |
| Execution spec | ✅ | `prompts/CLAUDE_CODE_MASTER_TASK.md` |
| Baseline configuration | ✅ | `lazy.conf` (a stock third-party config) |
| `config/` directory | ❌ | Spec expects `config/lazy.conf`; file is at repo root |
| `rules/` (rule providers) | ❌ | None — no local `.list` files |
| `scripts/` (build/validate) | ❌ | None |
| `tests/` | ❌ | None |
| `.github/` (CI, templates) | ❌ | None |
| `README` / `CHANGELOG` / `LICENSE` | ❌ | None |
| Git repository | ❌ | Not initialized (`Is a git repository: false`) |

**Conclusion:** The intended architecture (`03_ARCHITECTURE.md`, §4 "Directory Layout")
describes a mature multi-layer project. The repository today implements **Layer 1
(Documentation)** and provides a raw input for Layer 2. Layers 2–7 (Configuration, Strategy
Groups, Rule Providers, Rules, Validation, Build) do **not yet exist as project artifacts** —
they exist only inside the borrowed `lazy.conf`.

### 1.2 What `lazy.conf` actually is

`lazy.conf` is **not an author-written configuration**. It is a stock, auto-generated config
from a well-known public ad-block/rules project:

- `update-url = https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/lazy.conf`
  (line 122)
- Header timestamp: `# Shadowrocket: 2026-07-08 09:02:42` (line 1)

This matters enormously for the whole project: **the baseline is a generic, remotely-updated,
third-party file.** It was never designed around AI workflows, has no proxy groups, and will
be *overwritten on every subscription refresh* if used as-is. Treating it as "the current
config to extend" is only safe once it is forked into a locally-owned, version-controlled
artifact.

---

## 2. Architecture (as-found)

### 2.1 Section inventory of `lazy.conf`

Shadowrocket configs are INI-style with named sections. Present sections and their real
(non-comment) content:

| Section | Lines | Real payload | Empty? |
|---|---|---|---|
| `[General]` | 2–122 | ~15 active keys (DNS, TUN, IPv6, QUIC, update-url) | No |
| `[Proxy]` | 124–161 | **0 nodes** — only format documentation comments | **Empty** |
| `[Proxy Group]` | 163–194 | **0 groups** — only format documentation comments | **Empty** |
| `[Rule]` | 196–311 | ~40 active rules (mostly `RULE-SET`) + `GEOIP` + `FINAL` | No |
| `[Host]` | 313–325 | 3 host mappings | No |
| `[URL Rewrite]` | 327–330 | 2 Google-anti-redirect rewrites | No |
| `[MITM]` | 332–336 | `hostname = *.google.cn` only | Minimal |

### 2.2 The single most important structural fact

**There are zero proxy groups.** `[Proxy Group]` contains only the template comments that ship
with every Shadowrocket config. Every rule therefore terminates in a **literal policy token** —
`PROXY`, `DIRECT`, or `REJECT` — never in a named group.

Consequences:
- `PROXY` resolves to **whichever single node the user has selected on the app home screen**
  (Shadowrocket's global proxy). There is no per-service routing.
- Claude, ChatGPT, Google, GitHub, YouTube, Netflix, Twitter… **all resolve to the same one
  node.** There is no way to pin Claude→Taiwan while ChatGPT→US without manually swapping the
  single global node.
- None of the project's AI-First requirements (Charter Principle 2, PRD §8–13) are expressible
  in this structure. They *require* proxy groups, which do not exist.

### 2.3 Data-flow of a request (as-found)

```
request
  │
  ▼
[Rule] evaluated top-to-bottom
  │   ├─ matches a RULE-SET / GEOIP / domain rule ─▶ literal PROXY | DIRECT | REJECT
  │   └─ no match ─▶ FINAL,PROXY
  ▼
literal "PROXY" ─▶ the ONE globally-selected node
literal "DIRECT" ─▶ no proxy
```

No group layer, no regex node filter, no region pinning, no airport abstraction.

---

## 3. Rule providers (as-found)

The config relies almost entirely on **remote `RULE-SET` references** (blackmatrix7's
`ios_rule_script` and `iab0x00/ProxyRules`). There are **no local rule files** in the repo.

### 3.1 Active remote rule-sets → `PROXY`

| # | Rule-set | Source | Purpose |
|---|---|---|---|
| 1 | `AI.txt` | iab0x00/ProxyRules | **All AI services bundled** (see §3.4) |
| 2 | YouTube | blackmatrix7 | Video |
| 3 | Netflix | blackmatrix7 | Video |
| 4 | Disney | blackmatrix7 | Video |
| 5 | HBO | blackmatrix7 | Video |
| 6 | Spotify | blackmatrix7 | Music |
| 7 | Telegram | blackmatrix7 | Messaging |
| 8 | PayPal | blackmatrix7 | Payments |
| 9 | Twitter | blackmatrix7 | Social |
| 10 | Facebook | blackmatrix7 | Social |
| 11 | Amazon | blackmatrix7 | Shopping |
| 12 | Sony / Nintendo / Epic / Steam / Game | blackmatrix7 | Gaming |
| 13 | GitHub | blackmatrix7 | Dev |
| 14 | Microsoft | blackmatrix7 | Microsoft |
| 15 | Google | blackmatrix7 | Google |
| 16 | TikTok | blackmatrix7 | Social |
| 17 | Global | QuantumultX | Generic "needs proxy" list |

### 3.2 Active remote rule-sets → `DIRECT`

Apple (QuantumultX), BiliBili, NetEaseMusic, Baidu, DouBan, WeChat, Sina, Zhihu, XiaoHongShu,
DouYin, SteamCN, China (QuantumultX), Lan.

### 3.3 Non-rule-set terminal rules

- `DOMAIN-SUFFIX,litix.io / discomax.com / brightline.tv,PROXY` (streaming CDNs)
- `GEOIP,CN,DIRECT` (line 308)
- `FINAL,PROXY` (line 311)

### 3.4 The bundled AI rule (critical)

Line 267: `RULE-SET,…/iab0x00/ProxyRules/main/Rule/AI.txt,PROXY`

This single file (fetched and inspected, 46 rules) contains **all** AI vendors mixed together:

| Vendor | Rules in AI.txt | Separated? |
|---|---|---|
| Claude / Anthropic | 2 (`claude.ai`, `anthropic.com`) | ❌ bundled |
| OpenAI / ChatGPT | 12 | ❌ bundled |
| Google / Gemini / AI Studio / NotebookLM | 15 | ❌ bundled |
| Microsoft Copilot | 3 | ❌ bundled |
| GitHub Copilot | 1 | ❌ bundled |
| xAI / Grok | 2 | ❌ bundled |
| Perplexity | 3 | ❌ bundled |
| Apple Intelligence | 7 | ❌ bundled (→ PROXY!) |
| OpenRouter | 1 | ❌ bundled |

All 46 → the same `PROXY` policy. Immediately above (lines 243–265) there is a **commented-out,
more granular AI block** (separate Claude.list, OpenAI.list, Gemini.list, Copilot.list) that the
config author disabled in favor of the single bundle. This tells us the upstream project is
aware of granular AI routing but the active baseline does not use it.

> Note: because Anthropic's granular rule-set (`anthropic.com`, `claude.ai`) is thin, real-world
> Claude coverage also depends on assets/CDN domains not present here. This is relevant to
> Phase 4 provider design but is out of scope for Phase 1.

---

## 4. Strategy groups (as-found)

**None.** See §2.2. This is the defining weakness of the baseline relative to the project's
goals. All eight requirements FR-001…FR-007 in the PRD assume named groups; none can be met
without introducing the group layer.

---

## 5. `[General]` behavior worth noting

| Key | Value | Assessment |
|---|---|---|
| `dns-server` | doh.pub, alidns, 223.5.5.5, 119.29.29.29 | China-optimized DoH; fine for DIRECT, but AI/proxy traffic risks DNS-based geo-leak (see LAZY_ANALYSIS) |
| `fallback-dns-server` | system | OK |
| `ipv6` | true | Can cause instability for some proxy nodes / AI endpoints |
| `prefer-ipv6` | false | Reasonable |
| `dns-direct-fallback-proxy` | true | Good for censored-DNS resilience |
| `private-ip-answer` | true | Good |
| `block-quic` | all-proxy | Sensible (forces HTTP/2 over proxy) |
| `hijack-dns` | 8.8.8.8:53,8.8.4.4:53 | Captures hardcoded-DNS apps |
| `udp-policy-not-supported-behaviour` | REJECT | Reasonable default |
| `update-url` | johnshall lazy.conf | **Overwrite risk** — subscription refresh replaces the whole file |
| `skip-proxy` | LAN + bank/baidu/163 domains | Standard |

---

## 6. Weaknesses (as-found)

Ordered by impact on the project's stated mission.

1. **No proxy groups → no per-service routing.** (Blocks the entire AI-First mission.)
2. **AI vendors are bundled into one rule-set → one policy.** Claude cannot be pinned to Taiwan
   independently of ChatGPT→US. (Blocks PRD §9–13.)
3. **Baseline is a remote, auto-updating third-party file.** `update-url` will overwrite any
   local edits on refresh; not locally owned or versioned. (Blocks Charter Goal 4 / engineering.)
4. **No regex node selection.** Adding a node cannot "auto-join" a service group because groups
   don't exist yet. (Blocks Charter Principle 5, PRD §16.)
5. **Apple is partially wrong.** Apple Intelligence domains inside `AI.txt` go to **PROXY**,
   while the Apple rule-set goes DIRECT — the project wants Apple → DIRECT (PRD §13, FR-005).
6. **No airport/provider abstraction.** Nodes and airports are not modeled at all (`[Proxy]`
   empty; user adds nodes via subscription in-app). (Blocks Charter "Airport Strategy".)
7. **Rule order is not the project's canonical order.** Current order is
   AI→streaming→social→gaming→dev→Google→Apple→CN domains→GEOIP→FINAL; the project mandates
   Anthropic→OpenAI→GitHub→Google→Apple→China→Proxy→Final (ARCHITECTURE §12).
8. **Google is duplicated / order-ambiguous.** Google domains appear both inside `AI.txt`
   (Gemini etc.) and in the standalone Google rule-set — first match wins, so intent is unclear.
9. **No documentation, changelog, license, tests, CI, or build.** (Blocks Charter Goal 4.)
10. **Path mismatch vs spec.** Master task expects `config/lazy.conf`; file is at repo root.
11. **`ipv6 = true`** may reduce AI-endpoint stability; worth revisiting in design.

---

## 7. Improvement opportunities (pointers only — detailed in DESIGN.md)

- Fork `lazy.conf` → locally-owned `config/AI-Ultimate.conf`, decouple from `update-url`
  overwrite, and version it.
- Introduce ≤10 **named proxy groups** (Claude, ChatGPT, GitHub, Google, Apple, Proxy, DIRECT,
  REJECT…), all AI groups `select`-only.
- Split the AI bundle into per-vendor **local rule providers** (`anthropic.list`, `openai.list`,
  …) so Claude/ChatGPT route independently.
- Add **regex `policy-regex-filter`** node selection so new nodes auto-join by name (TW/US/SG/JP).
- Re-establish the **canonical rule order** with Apple pinned DIRECT.
- Add `scripts/` validation + `tests/` + `.github/` + README/CHANGELOG to reach the intended
  7-layer architecture.

---

## 8. Estimated complexity

| Work area | Complexity | Rationale |
|---|---|---|
| Fork baseline into owned config | **Low** | Copy + edit `update-url` handling |
| Design ≤10 proxy groups | **Low–Med** | Bounded by spec; main effort is regex + defaults |
| Split AI bundle into providers | **Medium** | Per-vendor domain curation, ongoing maintenance |
| Regex node auto-selection | **Medium** | Regex correctness + airport-naming variance |
| Canonical rule order + Apple fix | **Low–Med** | Mechanical but must be validated for regressions |
| Validation scripts + tests | **Medium** | New tooling from scratch (syntax, dup, order checks) |
| Docs / CHANGELOG / CI / release | **Medium** | Volume, not difficulty |
| **Overall project** | **Medium** | No hard technical blockers; effort is breadth + discipline. Risk concentrated in node-name regex and Claude/OpenAI domain coverage. |

**Overall assessment:** The baseline is *structurally simple but strategically empty* for this
project's purpose. The work is not a "fix" of `lazy.conf` — it is building the missing group /
provider / regex / tooling layers on top of a forked baseline, exactly as the Charter intends
("create AI-Ultimate, not simply modify lazy.conf").

---

## 9. STOP

Per Phase 1 instructions: analysis complete, **nothing modified**. Proceed to Phase 2
(`LAZY_ANALYSIS.md`).
