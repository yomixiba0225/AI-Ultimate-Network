# DESIGN.md

**Phase:** 4 — Design
**Project:** AI-Ultimate-Network
**Status:** Design specification. **No code written, no config modified.**
**Inputs:** CONFIG_ANALYSIS.md, LAZY_ANALYSIS.md, GAP_ANALYSIS.md, Charter/PRD/Architecture.

> This document defines *what* will be built and *why*. Config snippets are **illustrative
> design specifications**, not the final implementation — actual editing happens in Phase 6 and
> only after user approval. Snippet syntax targets Shadowrocket; portability notes cover Clash.

---

## 1. Design goals recap (binding constraints)

1. **AI-First** — every AI service has an independent policy; never mixed into generic Proxy.
2. **Stable IP first** — AI groups are **Select-only** (no url-test / fallback / load-balance).
3. **≤10 strategy groups** — bounded, human-readable.
4. **Regex node selection** — adding a node requires **zero** config changes.
5. **Airports are Providers, not user-facing** — users see *use-cases* (Claude, ChatGPT…).
6. **Prefer Extension over Replacement** — keep the working China-bypass skeleton; add layers.
7. **100% import compatibility** — never emit invalid Shadowrocket syntax.

---

## 2. Strategy Group design

### 2.1 The group set (exactly 8 functional + 2 reject/direct = within ≤10)

| # | Group | Type | Node filter (regex intent) | Default selection | Rationale |
|---|---|---|---|---|---|
| 1 | **Claude** | `select` | `(TW\|Taiwan\|台湾\|台灣)` | Berry Hinet TW → ToLink TW | PRD§9; Anthropic prefers stable TW IP |
| 2 | **ChatGPT** | `select` | `(US\|USA\|美国\|美國)` + `(SG\|Singapore\|新加坡)` | ToLink ChatGPT US → SG | PRD§10; OpenAI region-locked, US primary |
| 3 | **GitHub** | `select` | `(US\|USA\|美国)` + `(JP\|Japan\|日本)` | US residential → JP | PRD§11; stability, prefer home-broadband |
| 4 | **Google** | `select` | `(JP\|Japan\|日本)` + `(SG\|Singapore\|新加坡)` | JP → SG | PRD§12; avoid HK for Google |
| 5 | **Apple** | `select` | — (policy list: DIRECT, Proxy) | **DIRECT** | PRD§13; Apple always direct unless user overrides |
| 6 | **Proxy** | `select` (may contain a url-test child) | `.*` (all nodes) | Auto/manual | Generic foreign sites |
| 7 | **Auto** *(child of Proxy)* | `url-test` | `.*` | lowest latency | Only for **non-AI** generic traffic |
| 8 | **Final** | `select` | → Proxy / DIRECT | Proxy | Backs `FINAL` rule |
| 9 | **DIRECT** | built-in | — | — | China + LAN |
| 10 | **REJECT** | built-in | — | — | Ads/blocking (future) |

**Count check:** user-facing custom groups = Claude, ChatGPT, GitHub, Google, Apple, Proxy,
Auto, Final = **8** (≤10 ✔). DIRECT/REJECT are built-ins, not custom groups.

### 2.2 Strategy-type rules (hard constraints)

- **AI groups (Claude, ChatGPT, GitHub, Google) MUST be `select`.** No `url-test`, no
  `fallback`, no `load-balance`, no `random`. (Charter §Strategy Philosophy, ARCH §13.)
- **Only the generic `Auto` child of `Proxy`** may be `url-test`. AI traffic never enters it.
- **Apple** is `select` with DIRECT as position 0 so a user *can* override, but default DIRECT.

### 2.3 Illustrative group spec (design, not final)

```ini
[Proxy Group]
# AI groups: SELECT ONLY. Node lists auto-populated by regex.
Claude   = select, policy-regex-filter=(TW|Taiwan|台湾|台灣), select=0
ChatGPT  = select, policy-regex-filter=(US|USA|美国|美國|SG|Singapore|新加坡), select=0
GitHub   = select, policy-regex-filter=(US|USA|美国|JP|Japan|日本), select=0
Google   = select, policy-regex-filter=(JP|Japan|日本|SG|Singapore|新加坡), select=0
Apple    = select, DIRECT, Proxy, select=0
Proxy    = select, Auto, policy-regex-filter=.*, select=0
Auto     = url-test, policy-regex-filter=.*, interval=300, tolerance=50, url=http://www.gstatic.com/generate_204
Final    = select, Proxy, DIRECT, select=0
```

> Exact `select=`/default indices and the interplay of `policy-regex-filter` with subscription
> `use=true` will be finalized in Phase 5/6 against the user's real node names.

---

## 3. Rule Provider design

### 3.1 Local provider files (`rules/`)

Split the bundled `AI.txt` and consolidate per the canonical order. One file per responsibility
(ARCH §6):

| Provider file | Contents (seed) | Group target |
|---|---|---|
| `rules/anthropic.list` | `claude.ai`, `anthropic.com`, Claude assets/CDN, `claude.com` | Claude |
| `rules/openai.list` | `openai.com`, `chatgpt.com`, `chat.com`, `sora.com`, `oaistatic.com`, `oaiusercontent.com`, `livekit.cloud`, statsig/intercom/sentry endpoints, keywords `openaiapi`/`openaicom` | ChatGPT |
| `rules/github.list` | `github.com`, `githubusercontent.com`, `githubcopilot.com`, ghcr, codeload | GitHub |
| `rules/google.list` | `google.com`, `gstatic.com`, `googleapis.com`, `gemini.google.com`, `aistudio.google.com`, `ai.google.dev`, `deepmind`, `notebooklm`, YouTube (optional split) | Google |
| `rules/apple.list` | Apple + **Apple Intelligence** domains (moved out of AI bundle) | Apple → DIRECT |
| `rules/ai-extra.list` | Perplexity, Grok/x.ai, OpenRouter, DeepSeek, Mistral (future) | Proxy (or own group later) |
| `rules/china.list` | keep referencing CN lists (BiliBili, WeChat, Baidu…) | DIRECT |
| `rules/proxy.list` | generic foreign (Global-style) | Proxy |

**Extension provenance:** seed domains come from the existing `AI.txt` (already audited, 46
rules) plus the commented granular block in `lazy.conf` (Claude.list/OpenAI.list/Gemini.list/
Copilot.list references). We reuse upstream `blackmatrix7` lists where they are already correct
(GitHub, Google, Apple, China) and only **author local files where per-vendor separation is
required** (anthropic, openai).

### 3.2 Remote vs local policy

- **Keep remote** for large, well-maintained, non-AI lists (China services, Apple base, Google
  base) — low drift risk, high maintenance value.
- **Author local** for AI vendors that must be split and pinned (Anthropic, OpenAI) — these are
  small and stability-critical.
- Optionally **pin** remote lists to a commit rather than `master` (G13) — decided in Phase 5.

---

## 4. Rule Order design (canonical)

Final `[Rule]` order (ARCH §12), most-specific AI first, China bypass, then generic:

```
1.  Anthropic  → Claude          (local anthropic.list)
2.  OpenAI     → ChatGPT         (local openai.list)
3.  GitHub     → GitHub          (github.list)
4.  Google     → Google          (google.list)   # Gemini/AI Studio included here
5.  Apple      → DIRECT          (apple.list, incl. Apple Intelligence)  # fixes G8
6.  AI-extra   → Proxy           (Perplexity/Grok/OpenRouter; own group later)
7.  China svc  → DIRECT          (BiliBili/WeChat/Baidu/… + China.list)
8.  Generic    → Proxy           (Global/proxy.list, streaming, social)
9.  LAN        → DIRECT          (Lan.list)
10. GEOIP,CN   → DIRECT
11. FINAL      → Final(=Proxy)
```

**Key corrections vs baseline (from GAP_ANALYSIS):**
- Apple moved **above** any AI/generic proxy rule and pinned DIRECT → fixes Apple-Intelligence
  leak (G8, G12).
- Claude/OpenAI/GitHub/Google become **distinct tiers** routing to their own groups (G2, G3,
  G6, G7, G11).
- FINAL now targets the **Final group** (→ Proxy), not a bare literal, so it is user-steerable.

**Order is contractual:** any future reordering requires a synchronized doc + CHANGELOG update
(ARCH §12).

---

## 5. Regex / Node-Selection design

### 5.1 Region regexes (canonical)

| Region | Regex | Used by |
|---|---|---|
| Taiwan | `(TW\|Taiwan\|台湾\|台灣)` | Claude |
| United States | `(US\|USA\|美国\|美國\|United States)` | ChatGPT, GitHub |
| Singapore | `(SG\|Singapore\|新加坡\|狮城)` | ChatGPT, Google |
| Japan | `(JP\|Japan\|日本)` | GitHub, Google |
| Any | `.*` | Proxy / Auto |

### 5.2 Rules for regex

- Node names are **never hardcoded** into groups (Charter §P5, PRD §16). Groups declare a
  **filter**, Shadowrocket populates matching nodes at runtime.
- **Adding node "台湾107"** → automatically appears in Claude group, **zero config change** (the
  acceptance test in PRD §16).
- Filters are **broad enough** to catch bilingual naming (EN + zh-Hans + zh-Hant) but **narrow
  enough** to avoid cross-region bleed (e.g., ensure "US" doesn't match "AUS/澳洲"; refine to
  word-boundary or exclude-lists in Phase 5 if a user's airport uses ambiguous names).

### 5.3 Ambiguity handling (design-time risk control)

- **"US" vs "AUS"/"Austria"**: if a provider names Australia "AUS", tighten to
  `(\bUS\b|USA|美国)` or add negative lookahead. Decided against the **real** node list in M4.
- **Preferred-node pinning**: Charter wants Claude default = *Berry Hinet TW*. Since names vary
  per airport, use `policy-select-name=` (Shadowrocket) to pin a preferred default *when the
  exact name is known*, otherwise default to the first regex match. This preserves "zero-config"
  while honoring the preferred-line intent.

---

## 6. Airport Integration design

### 6.1 Principle: airports = Providers, use-cases = Groups (ARCH §9)

Users never select "Berry" or "ToLink." They select **Claude / ChatGPT / Google / GitHub**.
Airports are just the *pool of nodes* that regex filters draw from.

### 6.2 Multi-airport model

```
Airports (subscriptions)          Groups (use-cases, user-facing)
──────────────────────            ───────────────────────────────
 Berry   ─┐                        Claude   ← regex TW  ─ draws from all airports
 ToLink  ─┼─► one merged node ───► ChatGPT  ← regex US/SG
 (future)─┘   pool by name         GitHub   ← regex US/JP
                                    Google   ← regex JP/SG
                                    Proxy    ← regex .*
```

- Nodes from **all** subscriptions are matched purely by **name regex**; the group does not care
  which airport a node came from.
- To make regex reliable across airports, Phase 5 will document a **naming expectation** (nodes
  should contain a region token). If an airport violates it, we add per-airport alias rules —
  contained, not architectural.

### 6.3 Preferred vs backup within a group

Within Claude: default = first TW match (ideally Berry Hinet via `policy-select-name`), user can
manually switch to any other TW node (ToLink TW backups) — all **Select**, never automatic
(honors "manual switch only", PRD §9).

---

## 7. DNS design (addresses G17)

**Split-DNS**, minimally invasive (keep current domestic DNS for direct traffic):

- **DIRECT domains** → keep `doh.pub, alidns, 223.5.5.5, 119.29.29.29` (fast, domestic).
- **Proxied / AI domains** → add a **`dns over proxy`** resolver so CDN geo-resolution happens at
  the exit region, e.g. (design intent):
  ```
  dns-server = https://doh.pub/dns-query, https://dns.alidns.com/dns-query, 223.5.5.5
  # design: route AI/proxy name resolution through proxy to prevent geo-leak
  # e.g. https://dns.google/dns-query#proxy=Proxy  (finalized in M5)
  ```
- Keep `fallback-dns-server = system`, `private-ip-answer = true`, `dns-direct-fallback-proxy =
  true`, `block-quic = all-proxy`, `[Host]` Apple/iCloud → system.
- **IPv6 (G18):** evaluate `ipv6=false` for AI stability in M5; not changed blindly.

DNS changes are **P2** and will be gated behind validation to avoid regressions.

---

## 8. Backward-compatibility & what is preserved

Per Charter Goal 2 (Prefer Extension over Replacement), the following are **kept unchanged**:

- China-bypass skeleton, `GEOIP,CN,DIRECT`, CN service DIRECT lists, LAN, `[Host]`,
  `[URL Rewrite]`, `skip-proxy`, `hijack-dns`, `block-quic`, `tun-excluded-routes`.
- All existing rule-sets that are already correct (Apple base, Google base, China, GitHub) —
  we **re-point** them to groups rather than rewrite them.

**Net structural change** = introduce `[Proxy Group]` content + split AI provider + reorder
rules + retarget policies from literals to groups. This is *additive + retargeting*, not a
rewrite (satisfies ARCH §15 "≥95% compatible").

---

## 9. Migration Plan (design-level; executable milestones are Phase 5)

| Step | Action | Reversible? | Gate |
|---|---|---|---|
| M0 | **Fork** `lazy.conf` → `config/AI-Ultimate.conf`; decouple from `update-url` overwrite; init git; commit baseline verbatim | ✅ (git) | User confirms fork |
| M1 | Create `rules/` local providers (anthropic, openai, …) from audited seeds | ✅ | Validate lists parse |
| M2 | Add `[Proxy Group]` with 8 groups + regex (AI = select) | ✅ | Import test in Shadowrocket |
| M3 | Retarget `[Rule]` to groups + apply canonical order + Apple DIRECT fix | ✅ | Diff-review + import test |
| M4 | Tune regex against real node names; set preferred defaults | ✅ | Node auto-join test (add fake TW node) |
| M5 | DNS split + validation scripts + tests | ✅ | Validation suite green |
| M6 | README/CHANGELOG/ADR/Roadmap | ✅ | Docs review |
| M7 | Version tag + release notes (**push requires confirmation**) | ✅ | User confirms push |

**Guiding rules:** small readable commits; document every change; never a large rewrite; each
milestone independently importable and revertible.

---

## 10. Rollback Plan

**Every layer has an escape hatch:**

1. **Git baseline commit** — M0 commits the untouched `lazy.conf` verbatim. `git revert`/checkout
   restores the exact original at any time.
2. **Keep original file** — `lazy.conf` remains in-repo as the reference baseline; the built
   artifact is a *separate* `config/AI-Ultimate.conf`, so the original is never destroyed.
3. **Per-milestone revert** — each milestone is one (or few) commits; revert a single milestone
   without unwinding others (e.g., roll back DNS in M5 while keeping groups from M2).
4. **In-app fallback** — because groups are additive and rules degrade gracefully, a user can set
   every group's selection to the single global node to reproduce baseline behavior instantly.
5. **Subscription restore** — if all else fails, re-adding the original `update-url` subscription
   re-fetches the upstream `lazy.conf`.

**Rollback trigger conditions:** failed import, broken AI routing, node regex mis-match causing
empty groups, or DNS-induced resolution failures. Any one → revert the offending milestone.

---

## 11. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Regex bleed** (e.g. "US" matches "AUS", empty TW group) | Med | High (wrong region for AI) | Tighten regex with word boundaries / exclude-lists against real node names in M4; validation asserts each AI group is non-empty |
| **Airport naming lacks region token** | Med | High | Document naming expectation; add per-airport alias rules; fall back to `policy-select-name` pins |
| **Claude/OpenAI domain coverage incomplete** (assets/CDN missing) | Med | Med | Seed from audited AI.txt + commented granular block; expand via observed traffic; ADR to track additions |
| **`update-url` overwrites local edits** | High (if not decoupled) | Critical | M0 forks to a separate owned file and drops/neutralizes `update-url`; never edit the subscription in place |
| **DNS split misconfig → resolution failure** | Low-Med | High | Gate DNS behind M5 validation; keep domestic DNS for DIRECT; easy single-milestone rollback |
| **First-match-wins ordering regressions** | Med | Med | Canonical order documented + validation checks FINAL-last, no unreachable rules |
| **Provider (remote) upstream drift** | Low | Med | Optionally pin to commit (G13); local files for critical AI vendors |
| **Import syntax error breaks whole config** | Low | Critical | Validation before every commit (syntax, dup, refs, FINAL position); import test each milestone |
| **Group count creep >10** | Low | Low (maintainability) | Hard cap enforced in validation; AI-extra shares Proxy until justified |
| **IPv6 instability for AI** | Low-Med | Med | Evaluate `ipv6=false` in M5 with A/B check; reversible |

**Residual risk after mitigations:** **Low–Moderate**, concentrated in (a) region-regex accuracy
against real node names and (b) Anthropic/OpenAI domain completeness — both empirical and
iteratively correctable without architectural change.

---

## 12. Design acceptance criteria (maps to PRD §20 / Master §Success)

- [ ] Claude group exists, **Select-only**, default Taiwan, auto-includes new TW nodes.
- [ ] ChatGPT group exists, **Select-only**, default US, SG backup.
- [ ] GitHub, Google groups independent with correct region preference.
- [ ] Apple → **DIRECT** (Apple Intelligence no longer proxied).
- [ ] ≤10 groups total; no AI group uses url-test/fallback/load-balance.
- [ ] Adding a node requires **zero** config edits (regex auto-join).
- [ ] Canonical rule order enforced; FINAL last.
- [ ] China-bypass + existing DIRECT behavior preserved (≥95% compat).
- [ ] Config imports into Shadowrocket with **no syntax error**.
- [ ] Original baseline preserved and revertible.

---

## 13. Out of scope for this phase

- Actual file edits (Phase 6).
- Build/validation script implementation (Phase 5 plan → Phase 6 code).
- Clash Meta/Verge/Surge generation (long-term; ARCH §Long-term).

**End of Phase 4.** Awaiting user confirmation before Phase 5 (Implementation Plan / milestones).
