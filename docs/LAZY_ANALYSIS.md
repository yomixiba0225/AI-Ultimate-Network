# LAZY_ANALYSIS.md

**Phase:** 2 — Reverse Engineering of `lazy.conf`
**Project:** AI-Ultimate-Shadowrocket
**Scope:** Understand only. **Do not optimize.** No files modified.
**Baseline:** `lazy.conf`, 336 lines. Origin: `johnshall/Shadowrocket-ADBlock-Rules-Forever`.

---

## 0. Method

`lazy.conf` is parsed section by section exactly as Shadowrocket would read it. For each
section this document records: (a) what is actually active (non-comment), (b) what it means,
(c) compatibility notes, (d) potential issues, (e) potential improvements. Improvements are
listed for completeness but are **not applied** in this phase.

A large fraction of the file (roughly 60%) is **template/comment text** shipped by Shadowrocket
and the upstream project. Those comments are documentation of the format, not active config, and
are called out where relevant.

---

## 1. General

### 1.1 Active keys

| Line | Key | Value |
|---|---|---|
| 21 | `skip-proxy` | LAN ranges + `captive.apple.com`, `*.local`, bank domains (`*.ccb.com`, `*.abchina.com.cn`, `*.psbc.com`), `www.baidu.com`, `www.163.com` |
| 24 | `tun-excluded-routes` | Standard reserved/multicast IPv4+IPv6 ranges |
| 50 | `dns-server` | `https://doh.pub/dns-query, https://dns.alidns.com/dns-query, 223.5.5.5, 119.29.29.29` |
| 53 | `fallback-dns-server` | `system` |
| 56 | `ipv6` | `true` |
| 59 | `prefer-ipv6` | `false` |
| 62 | `dns-direct-system` | `false` |
| 65 | `icmp-auto-reply` | `true` |
| 68 | `always-reject-url-rewrite` | `false` |
| 71 | `private-ip-answer` | `true` |
| 74 | `dns-direct-fallback-proxy` | `true` |
| 83 | `hijack-dns` | `8.8.8.8:53, 8.8.4.4:53` |
| 86 | `udp-policy-not-supported-behaviour` | `REJECT` |
| 111 | `block-quic` | `all-proxy` |
| 122 | `update-url` | johnshall lazy.conf |

### 1.2 Interpretation

- **DNS is China-first.** Both DoH endpoints (doh.pub, alidns) and both plain resolvers
  (223.5.5.5 AliDNS, 119.29.29.29 DNSPod) are domestic. Good latency for DIRECT domains; but for
  proxied/AI domains, resolving via a domestic resolver can return **CN-geolocated CDN IPs** or
  be subject to poisoning — see §2.
- **`dns-direct-fallback-proxy = true`** is a resilience feature: if a direct-rule domain fails
  to resolve locally, it retries through proxy. Sensible in a censored environment.
- **`hijack-dns`** intercepts apps that hardcode Google DNS (e.g., some smart-TV / Netflix
  clients), forcing them through Shadowrocket's resolver.
- **`block-quic = all-proxy`** blocks QUIC/HTTP-3 only on proxied connections, forcing a fallback
  to HTTP/2. This improves stability of proxied traffic (UDP/443 over proxies is often poor) while
  leaving direct QUIC intact. Consistent with the project's stability-first stance.
- **`update-url`** is the defining compatibility hazard: the file is a **subscription**. On
  refresh, Shadowrocket replaces the entire file with the upstream version, discarding any local
  groups/rules. Any AI-Ultimate work must first break this coupling.

---

## 2. DNS

Reproduced from General because it deserves standalone analysis.

- **Active resolvers:** DoH `doh.pub`, DoH `dns.alidns.com`, plain `223.5.5.5`, `119.29.29.29`.
- **Fallback:** `system`.
- **IPv6:** enabled (`ipv6=true`, `prefer-ipv6=false`) → queries both A and AAAA, prefers A.
- **Fake-IP / TUN:** implied by Shadowrocket TUN defaults; `private-ip-answer=true` means a
  private-IP answer is trusted rather than treated as hijack.

**Potential issues**
1. **Geo-leak for proxied domains.** AI and proxy traffic ideally resolves *at the exit node*
   (or via an uncensored resolver) so the CDN returns an IP near the exit region. Resolving Claude
   / OpenAI / Google via AliDNS/DNSPod may hand back suboptimal or CN-edge IPs, undermining the
   "fixed region" goal even when the node is correct. There is **no `dns over proxy`** entry
   (e.g. `https://dns.google/dns-query#proxy=…`) for proxied domains.
2. **IPv6 enabled globally.** Some proxy nodes and some AI endpoints behave inconsistently over
   IPv6; `ipv6=true` can introduce hard-to-diagnose instability. (Not wrong, just a risk.)
3. **No DoH for the uncensored path.** Everything trusts domestic DNS; a poisoned answer for a
   proxied domain could still mis-route.

**Potential improvements (not applied)**
- Consider a split-DNS design: domestic DoH for DIRECT domains, `dns over proxy` (e.g. Google/
  Cloudflare DoH through a proxy) for AI/proxy domains.
- Consider `prefer-ipv6=false` remains, but evaluate `ipv6=false` for AI-endpoint stability.

---

## 3. Rules

### 3.1 Active rule order (top → bottom, as Shadowrocket evaluates)

1. **AI bundle** → `AI.txt` → **PROXY** (line 267)
2. **Streaming/social/commerce/gaming (proxy):** YouTube, Netflix, Disney, +3 CDN domains, HBO,
   Spotify, Telegram, PayPal, Twitter, Facebook, Amazon, Sony, Nintendo, Epic, SteamCN(?),
   Steam, Game → **PROXY** (lines 268–286)
3. **Dev/MS/Google (proxy):** GitHub, Microsoft, Google → **PROXY** (lines 287–289)
4. **Apple → DIRECT** (QuantumultX Apple list, line 290)
5. **CN services → DIRECT:** BiliBili, NetEaseMusic, Baidu, DouBan, WeChat, Sina, Zhihu,
   XiaoHongShu, DouYin (lines 291–299)
6. **TikTok → PROXY** (line 300)
7. **Global → PROXY** (QuantumultX Global, line 301)
8. **China → DIRECT** (QuantumultX China, line 302)
9. **Lan → DIRECT** (line 305)
10. **GEOIP,CN → DIRECT** (line 308)
11. **FINAL → PROXY** (line 311)

### 3.2 Interpretation of routing intent

- **Everything "foreign and interesting" → PROXY**, everything "Chinese" → DIRECT, unknown →
  PROXY. This is a classic "global mode with China bypass" topology.
- **All PROXY rules collapse to one node** (no groups; see CONFIG_ANALYSIS §2.2).
- **SteamCN** appears in the PROXY block (line 284) but semantically is a CN community; upstream
  places it before Steam so Steam-CN domains stay proxied with Steam — an upstream quirk, noted
  not judged.

### 3.3 Rule-type usage

- Overwhelmingly `RULE-SET` (remote lists). A handful of literal `DOMAIN-SUFFIX` (litix.io,
  discomax.com, brightline.tv, x.ai, grok.com in the *commented* block). One `GEOIP`. One
  `FINAL`. No `IP-CIDR`, `AND/OR/NOT`, `USER-AGENT`, `SCRIPT`, or `DST-PORT` rules are active.
- The `AND,((PROTOCOL,UDP),(DST-PORT,443)),REJECT-NO-DROP` QUIC-block rule (line 237) is
  **commented out** — QUIC is instead handled by `block-quic=all-proxy` in General.

### 3.4 Compatibility

- All active rules use valid Shadowrocket syntax and rule types (`RULE-SET`, `DOMAIN-SUFFIX`,
  `DOMAIN`, `GEOIP`, `FINAL`). The config **imports cleanly**.
- All policy tokens used (`PROXY`, `DIRECT`) are built-in and valid even with an empty
  `[Proxy Group]`. (Had any rule referenced a group name, it would dangle — but none do.)

### 3.5 Potential issues

1. **AI bundle precedence hides intent.** Because `AI.txt` is first and contains Google/Gemini
   *and* Apple Intelligence domains, some Google and Apple traffic is decided by line 267 (PROXY)
   **before** the dedicated Google (289) and Apple (290) rules are ever reached. First-match-wins
   makes the effective policy for those domains PROXY, not what lines 289–290 imply.
2. **Apple Intelligence → PROXY (unintended vs project).** Via `AI.txt`, 7 Apple domains proxy.
   Project wants Apple → DIRECT.
3. **No independent AI routing** (the central project gap): Claude, ChatGPT, Gemini, Copilot,
   Grok, Perplexity all share one policy.
4. **Order is not the project's canonical order** (Anthropic→OpenAI→GitHub→Google→Apple→China→
   Proxy→Final). Current order interleaves entertainment and social before dev/AI granularity.
5. **`GEOIP,CN` triggers DNS resolution** for otherwise-unmatched domains (no `no-resolve`),
   adding a resolve step at the bottom of the chain. Acceptable but worth noting.

### 3.6 Potential improvements (not applied)

- Split `AI.txt` into per-vendor providers and route each to its own group.
- Move Apple above the AI/PROXY rules and pin DIRECT.
- Adopt the canonical order and document any deviation.

---

## 4. Providers (Rule-Sets)

- **All providers are remote** (GitHub raw URLs). There are **no local providers** and no
  `rules/` directory.
- **Two upstreams:** `blackmatrix7/ios_rule_script` (most lists) and `iab0x00/ProxyRules`
  (the AI bundle). Also QuantumultX-format lists (Apple, WeChat, Global, China) — Shadowrocket
  accepts these via `RULE-SET`.
- **Availability risk:** every provider is a `raw.githubusercontent.com` URL — subject to GitHub
  availability and, in-region, to reachability. If the resolver/route to GitHub is blocked, rule
  refresh fails and stale/partial rules apply.
- **No pinning / no integrity:** rule-sets track `master` (moving target). Content can change
  under the config without notice.
- **Duplication across providers:** Google domains exist in both `AI.txt` and `Google.list`;
  Steam vs SteamCN overlap; `Global.list` is broad and may overlap many others. First-match-wins
  resolves conflicts by *position*, not by intent.

---

## 5. Strategy Groups

**Empty.** `[Proxy Group]` (lines 163–194) contains only Shadowrocket's format-documentation
comments (select / url-test / fallback / load-balance / random explanations and
`policy-regex-filter` recipes). **No group is defined.**

Implications (see CONFIG_ANALYSIS §2.2 for the full chain):
- No `select`, no `url-test`, no regex node filter is in effect.
- `PROXY` = the single home-screen node. `DIRECT` = bypass.
- The project's requirement that AI groups be **`select`-only** (Charter §Strategy Philosophy,
  ARCHITECTURE §13) is neither satisfied nor violated — the layer simply does not exist yet.

---

## 6. Order (canonical-order compliance)

| Project canonical order (ARCHITECTURE §12) | Present in baseline? | Position today |
|---|---|---|
| Anthropic | ❌ (inside AI bundle) | line 267 (mixed) |
| OpenAI | ❌ (inside AI bundle) | line 267 (mixed) |
| GitHub | ⚠️ present | line 287 (after entertainment) |
| Google | ⚠️ present but preempted by AI bundle | line 289 |
| Apple | ⚠️ present but preempted by AI bundle | line 290 |
| China | ✅ present | lines 291–302, 308 |
| Proxy | ✅ (Global + FINAL) | 301 / 311 |
| Final | ✅ `FINAL,PROXY` | line 311 |

**Verdict:** The high-level *China-bypass* skeleton matches, but the **AI/Google/Apple ordering
does not** meet the canonical order, and the AI tiers are not separated at all.

---

## 7. Compatibility summary

| Aspect | Status |
|---|---|
| Imports into Shadowrocket without error | ✅ Yes |
| Valid section headers / syntax | ✅ Yes |
| Valid rule types & policies | ✅ Yes |
| Dangling group references | ✅ None (no groups referenced) |
| Backward-compat with project intent | ⚠️ Skeleton only; AI/Apple/order diverge |
| Locally owned / safe to edit | ❌ No — `update-url` subscription will overwrite |

---

## 8. `[Host]`, `[URL Rewrite]`, `[MITM]`

- **`[Host]`** (313–325): `*.apple.com → server:system`, `*.icloud.com → server:system`,
  `localhost → 127.0.0.1`. Forces Apple/iCloud name resolution through system DNS (avoids
  breaking Apple services / private relay). Reasonable; keep.
- **`[URL Rewrite]`** (327–330): two 302 rewrites redirecting `g.cn` / `google.cn` →
  `www.google.com`. Anti-redirect convenience. Harmless.
- **`[MITM]`** (332–336): `hostname = *.google.cn` only, no CA content in-file. Effectively a
  no-op decrypt scope; no active MITM of substance. Low relevance to this project.

---

## 9. Consolidated findings (understand-only)

1. The baseline is a **stock, remotely-updated, third-party** China-bypass config with a valid
   but **group-less** structure.
2. **All proxied traffic funnels to one node**; there is no per-service or per-region routing.
3. **AI is one undifferentiated bundle** including Google and Apple Intelligence domains, which
   also **preempts** the dedicated Google/Apple rules by position.
4. **DNS is entirely domestic**, creating geo-leak risk for proxied/AI domains and offering no
   `dns over proxy` path.
5. **Rule order** matches the project only at the coarse China-bypass level; the AI/Google/Apple
   tiers diverge from the canonical order.
6. **Nothing is locally owned** — the `update-url` subscription is an overwrite hazard that must
   be decoupled before any edits are durable.

These findings feed directly into `GAP_ANALYSIS.md` (Phase 3) and `DESIGN.md` (Phase 4). No
optimization was performed in this phase.
