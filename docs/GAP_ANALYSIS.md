# GAP_ANALYSIS.md

**Phase:** 3 — Architecture Validation
**Project:** AI-Ultimate-Network
**Compares:** Current baseline (`lazy.conf`, per CONFIG_ANALYSIS + LAZY_ANALYSIS)
**Against:** `01_PROJECT_CHARTER.md`, `02_PRD.md.md`, `03_ARCHITECTURE.md`
**Status:** Analysis only. No files modified.

---

## 0. Legend

- **Priority:** P0 (blocks mission) · P1 (core requirement) · P2 (quality/maintainability) · P3 (nice-to-have)
- **Difficulty:** ★ trivial · ★★ small · ★★★ moderate · ★★★★ substantial
- **Source:** which spec section mandates the target (CH=Charter, PRD, ARCH=Architecture)

---

## 1. Executive summary

The baseline satisfies the project's **coarse China-bypass skeleton** and imports cleanly, but
it is missing every layer that makes the project "AI-Ultimate." The gaps cluster into four
themes, all rooted in one structural fact: **there are no proxy groups.**

1. **No per-service / per-region routing** (no groups, no regex) — the AI-First mission is
   currently *impossible to express*. (P0)
2. **AI vendors are bundled**, so Claude≠Taiwan and ChatGPT≠US independently. (P0)
3. **Baseline is a remote subscription** (`update-url`), not a locally-owned engineered project;
   edits are overwrite-prone and there is no docs/tests/CI/build. (P1)
4. **Rule order, Apple handling, and DNS** diverge from spec in specific, fixable ways. (P1–P2)

None of these are blocked by technical impossibility; the work is breadth + discipline (see
CONFIG_ANALYSIS §8). Overall migration difficulty: **moderate**.

---

## 2. Gap table — Strategy & Routing (the core)

| # | Dimension | Current | Target | Gap | Priority | Difficulty | Source |
|---|---|---|---|---|---|---|---|
| G1 | Proxy groups | **0 groups**; all rules → literal `PROXY`/`DIRECT` | ≤10 named groups (Claude, ChatGPT, GitHub, Google, Apple, Proxy, DIRECT, REJECT…) | Entire group layer missing | **P0** | ★★★ | CH§Strategy, PRD§8, ARCH§7 |
| G2 | Claude routing | Bundled in `AI.txt`→one node | Independent group, **Select-only**, default Taiwan (Berry Hinet → ToLink TW backup) | No independent Claude policy or region pin | **P0** | ★★★ | PRD§9, CH§Strategy, Master§AI |
| G3 | ChatGPT routing | Bundled in `AI.txt`→one node | Independent group, **Select-only**, default US (ToLink ChatGPT US → SG backup) | No independent ChatGPT policy or region pin | **P0** | ★★★ | PRD§10, Master§ChatGPT |
| G4 | Node selection | Manual single global node | **Regex** `policy-regex-filter` per group (TW/US/SG/JP); new nodes auto-join | No regex; adding nodes needs manual work | **P0** | ★★★ | CH§P5, PRD§16, ARCH§8 |
| G5 | AI strategy type | Implicit (global node) | AI groups **Select only** — no url-test/fallback/load-balance | Rule not encoded (no groups exist) | **P0** | ★★ | CH§Strategy, ARCH§13 |
| G6 | GitHub routing | `GitHub.list`→PROXY (shared node) | Independent group; prefer US residential, then Japan | No independent group / preference | **P1** | ★★ | PRD§11, Master§GitHub |
| G7 | Google routing | Split across `AI.txt`+`Google.list`→PROXY | Independent group; prefer Japan, then Singapore; avoid HK | No group; duplicated; no region preference | **P1** | ★★ | PRD§12, Master§Google |
| G8 | Apple routing | **Mixed**: Apple.list→DIRECT but Apple-Intelligence→PROXY via `AI.txt` | Apple always **DIRECT** | Apple Intelligence wrongly proxied; needs consolidation | **P1** | ★★ | PRD§13, FR-005, Master§Apple |
| G9 | Airport model | `[Proxy]` empty; airports = in-app subscriptions | Airports are **Providers**, users see *use-case* groups not airport names | No provider/airport abstraction | **P1** | ★★★ | CH§Airport, ARCH§9 |

---

## 3. Gap table — Rule Providers & Order

| # | Dimension | Current | Target | Gap | Priority | Difficulty | Source |
|---|---|---|---|---|---|---|---|
| G10 | Provider modularity | All remote; one bundled `AI.txt`; no local files | Per-vendor **local** providers: anthropic/openai/github/google/apple/china/proxy(+future) | AI bundle must be split; local `rules/` created | **P1** | ★★★ | ARCH§6, PRD§FR-001..007 |
| G11 | Rule order | AI→entertainment→dev→Google→Apple→CN→Global→GEOIP→FINAL | **Anthropic→OpenAI→GitHub→Google→Apple→China→Proxy→Final** | Order diverges; AI/Google/Apple not canonical | **P1** | ★★ | ARCH§12, PRD§15, Master§Rule |
| G12 | Rule preemption | `AI.txt` first → preempts Google/Apple rules | Each service resolved by its own tier in canonical order | Position-based conflicts | **P1** | ★★ | ARCH§12 |
| G13 | Provider pinning | Remote `master` (moving), no integrity | Owned/curated providers; predictable content | No control over upstream drift | **P2** | ★★ | ARCH§6, CH§Goal4 |
| G14 | AI extensibility | Adding Perplexity/Grok/DeepSeek = edit bundle | Add a provider + (maybe) reuse Proxy group; **no refactor** | Not structured for clean extension yet | **P2** | ★★ | PRD§19, ARCH§17 |

---

## 4. Gap table — Configuration Ownership, DNS, General

| # | Dimension | Current | Target | Gap | Priority | Difficulty | Source |
|---|---|---|---|---|---|---|---|
| G15 | Config ownership | Remote **subscription** via `update-url`; overwrites on refresh | Locally-owned, built artifact `config/AI-Ultimate.conf` | Edits not durable until decoupled | **P1** | ★★ | CH§Goal4, ARCH§5 |
| G16 | Config generation | Hand-imported single file | **Build** from template + rules + providers | No build pipeline | **P2** | ★★★ | ARCH§5, ARCH§10 |
| G17 | DNS for proxied domains | Domestic DoH/resolvers for everything | Split-DNS or `dns over proxy` for AI/proxy to avoid geo-leak | Geo-leak risk on AI domains | **P2** | ★★★ | (derived: CH§StableIP intent) |
| G18 | IPv6 | `ipv6=true` globally | Evaluate for AI-endpoint stability | Possible instability; unverified | **P3** | ★ | (derived: CH§P1 stability) |
| G19 | Input path | `lazy.conf` at repo root | Spec expects `config/lazy.conf` | Path mismatch vs Master Task | **P2** | ★ | Master§Inputs, ARCH§4 |

---

## 5. Gap table — Engineering / Project Maturity

| # | Dimension | Current | Target | Gap | Priority | Difficulty | Source |
|---|---|---|---|---|---|---|---|
| G20 | Directory layout | `docs/`, `prompts/`, root `lazy.conf` | `config/ docs/ rules/ scripts/ tests/ .github/ assets/` | Most dirs missing | **P2** | ★★ | ARCH§4 |
| G21 | Validation | None | Auto-checks: dup rules/providers/groups, regex, order, syntax, FINAL position, refs | No validation tooling | **P2** | ★★★ | ARCH§11, Master§Validation |
| G22 | Tests | None | Rule/Regex/Syntax/Duplicate tests | No tests | **P2** | ★★★ | ARCH§4 |
| G23 | Docs set | Charter/PRD/Arch only | + README, CHANGELOG, Roadmap, DESIGN, ADRs | Missing README/CHANGELOG/ADR/Roadmap | **P2** | ★★ | CH§Deliverables, Master§Docs |
| G24 | Versioning/Release | None | SemVer + release notes + tags | No release process | **P3** | ★★ | ARCH§14, Master§Release |
| G25 | CI / GitHub | Not a git repo; no `.github/` | Git repo + Actions + issue/PR templates | No VCS/CI at all | **P2** | ★★ | ARCH§4, Master§GitHub |
| G26 | License | None | LICENSE present | Missing | **P3** | ★ | ARCH§4 |
| G27 | Multi-platform | Shadowrocket only (implicit) | Shared design → Clash Meta/Verge/Surge (future) | Not designed for portability yet | **P3** | ★★★★ | CH§Vision, ARCH§Long-term |

---

## 6. Alignment — where the baseline already matches the spec

Not everything is a gap. These are **kept** (Prefer Extension over Replacement, CH§Goal2):

| Aspect | Status |
|---|---|
| China-bypass skeleton (foreign→proxy, CN→direct) | ✅ Matches intent |
| `GEOIP,CN,DIRECT` + `FINAL,PROXY` backbone | ✅ Keep (FINAL policy will point at Proxy group) |
| CN service lists → DIRECT (BiliBili, WeChat, Baidu…) | ✅ Keep |
| Apple base list → DIRECT | ✅ Keep (after removing Apple-Intelligence-via-AI proxy) |
| `[Host]` Apple/iCloud → system DNS | ✅ Keep |
| `block-quic=all-proxy`, `hijack-dns`, `skip-proxy` LAN/bank | ✅ Keep |
| Valid Shadowrocket syntax / clean import | ✅ Keep as compatibility bar |
| Claude & OpenAI already distinct *domains* in AI.txt | ✅ Reusable when splitting providers |

---

## 7. Gap clusters → recommended milestone mapping (preview of Phase 5)

This is a **preview only**; the milestone plan itself is Phase 5.

| Cluster | Gaps | Suggested milestone |
|---|---|---|
| Own the baseline | G15, G19, G20 | M1 Repository Cleanup |
| Split AI + providers | G10, G12, G13, G14 | M2 Rule Providers |
| Groups + region strategy | G1–G9 | M3 Strategy Groups |
| Regex node selection | G4, G5, G9 | M4 Regex |
| Validation/tests/DNS | G16, G17, G21, G22 | M5 Validation |
| Docs/ADR/Roadmap | G23, G26 | M6 Documentation |
| Versioning/CI/release | G24, G25, G27 | M7 Release |

---

## 8. Risk-weighted priority ranking

**Must-do to be "AI-Ultimate" at all (P0):** G1, G2, G3, G4, G5.
**Core feature completeness (P1):** G6, G7, G8, G9, G10, G11, G12, G15.
**Engineering maturity (P2):** G13, G14, G16, G17, G19, G20, G21, G22, G23, G25.
**Later (P3):** G18, G24, G26, G27.

**Single highest-leverage move:** introduce the proxy-group layer with regex (G1+G4). It
unblocks G2, G3, G5, G6, G7, G8, G9 simultaneously — nearly the entire AI-First mission depends
on it.

---

## 9. Conclusion

The baseline is **compatible but empty** with respect to the project's mission. There is no
architectural conflict to resolve — the spec's targets are *additive* to a valid skeleton, which
fits the Charter's "Prefer Extension over Replacement." The dominant gap is the **absent group +
regex + provider layers** (G1–G12), followed by **configuration ownership** (G15) and
**engineering maturity** (G20–G25). Detailed resolution is designed in `DESIGN.md` (Phase 4).
