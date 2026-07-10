# ADR-0009: WeChat-safe DNS under TUN (fake-ip-filter + IM process rules)

- **Status:** Accepted
- **Date:** 2026-07-10
- **Deciders:** Project owner (yomixiba0225)

## Context
With Clash Verge TUN mode on (macOS), WeChat hung at "收取中" for 3–5 minutes before logging
in. A prior attempt only disabled IPv6 (kernel + AAAA), which helps but does not fix it.

Root cause (also recorded in the owner's ops playbook): under **fake-ip** DNS mode, IM apps —
WeChat especially — receive fake IPs for their domains. WeChat's own connection stack (hardcoded
endpoints, MMTLS, long-lived direct sockets) misbehaves on fake answers and enters multi-minute
retry loops. The base airport subscription's `dns:` section is unmanaged: it may enable fake-ip
with **no** `fake-ip-filter`, and Verge's "DNS 覆写" toggle was off, so nothing corrected it.

## Decision
The Clash deliverables (`clash.yaml`, `clash-script.js`) now **own the DNS section** and add an
**IM-first rule tier**:

1. **Deterministic `dns:` block** — `enhanced-mode: fake-ip` *with* a `fake-ip-filter` that
   excludes IM (qq/weixin/wechat/weixinbridge/qpic/qlogo/gtimg/tencent, dingtalk, feishu,
   larksuite, netease/163/126), NTP/STUN, and captive-portal probes. Domestic DoH
   (doh.pub/alidns) as nameserver + `geosite:cn` policy; foreign DoH fallback gated by
   `fallback-filter geoip CN`. `ipv6: false` throughout (keeps the earlier fix).
2. **`PROCESS-NAME` rules first** (TUN supports process matching): `WeChat`, `QQ`, `DingTalk`,
   `Lark` → DIRECT before any other rule — the whole app bypasses proxy logic regardless of
   domain/IP/UDP. Plus explicit `weixin.qq.com`/`wechat.com`/`qq.com`/`qpic.cn`/`qlogo.cn`
   DOMAIN-SUFFIX → DIRECT for non-TUN modes where process matching is unavailable.
3. The Global Script variant applies the same DNS even when the airport profile ships a
   hostile/absent dns section (verified by simulation), so it works across all subscriptions.

## Consequences
- ✅ WeChat/QQ/DingTalk/Feishu get real IPs and direct sockets instantly under TUN.
- ✅ Verge's "DNS 覆写" can stay OFF — the config is self-sufficient.
- ⚠️ IM-first DIRECT sits *above* the canonical AI tier in the Clash rule order. This is a
  deliberate, documented deviation (ARCH §12): process rules are app-scoped and cannot collide
  with AI domains.
- ⚠️ `+.qq.com`/`+.163.com` in fake-ip-filter also cover Tencent/NetEase web properties —
  acceptable; they are CN-direct anyway.
- 🔗 Supersedes the IPv6-only mitigation; complements [[ADR-0007]] delivery paths.
