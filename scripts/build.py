#!/usr/bin/env python3
"""
build.py — Generate every client config from one source of truth.

Targets:
  shadowrocket -> config/AI-Ultimate.conf         (template + rules/*.list)
  clash        -> config/AI-Ultimate.clash.yaml   (strategy.py + rules/*.list, GEOSITE/GEOIP)
  surge        -> config/AI-Ultimate.surge.conf   (strategy.py + rules/*.list, GEOIP)

The AI-separation / region-pinning / regex-node core is identical across clients
because all three read the same rules/*.list and scripts/strategy.py.

Usage:
    python3 scripts/build.py                 # build all targets
    python3 scripts/build.py --target clash  # one target
    python3 scripts/build.py --check         # build in memory, fail if any on-disk differs
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import strategy as S

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "config" / "AI-Ultimate.template.conf"
OUT = {
    "shadowrocket": ROOT / "config" / "AI-Ultimate.conf",
    "clash": ROOT / "config" / "AI-Ultimate.clash.yaml",
    "clash-merge": ROOT / "config" / "AI-Ultimate.clash-merge.yaml",
    "clash-script": ROOT / "config" / "AI-Ultimate.clash-script.js",
    "clash-script-adobe": ROOT / "config" / "AI-Ultimate.clash-script-adobe.js",
    "surge": ROOT / "config" / "AI-Ultimate.surge.conf",
}
INCLUDE = "#!INCLUDE"
AIRPORT_PLACEHOLDER = "YOUR_AIRPORT_SUBSCRIPTION_URL"


# ---------------------------------------------------------------- Shadowrocket -----
def build_shadowrocket() -> str:
    header = (
        "# ============================================================================\n"
        "#  AI-Ultimate.conf — GENERATED FILE. DO NOT EDIT BY HAND.\n"
        "#  Source: config/AI-Ultimate.template.conf + rules/*.list\n"
        "#  Rebuild: python3 scripts/build.py\n"
        "# ============================================================================\n"
    )
    out = [header]
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith(INCLUDE):
            parts = s.split()
            if len(parts) != 3:
                raise SystemExit(f"[build] bad INCLUDE: {line!r}")
            _, list_name, group = parts
            rules = S.read_list(list_name)
            out.append(f"# --- expanded from rules/{list_name} -> {group} ({len(rules)} rules) ---")
            out += [f"{r},{group}" for r in rules]
        else:
            out.append(line)
    text = "\n".join(out)
    return text if text.endswith("\n") else text + "\n"


# ------------------------------------------------------------------------ Clash -----
def build_clash() -> str:
    L: list[str] = []
    L.append("# ============================================================================")
    L.append("#  AI-Ultimate-Network — Clash Meta / Clash Verge config. GENERATED — DO NOT EDIT.")
    L.append("#  Rebuild: python3 scripts/build.py --target clash")
    L.append("#")
    L.append(f"#  SETUP: replace {AIRPORT_PLACEHOLDER} below with your airport subscription")
    L.append("#  URL. Groups auto-select nodes from it by region regex (see docs/USAGE.md).")
    L.append("# ============================================================================")
    L.append("mixed-port: 7890")
    L.append("mode: rule")
    L.append("log-level: info")
    L.append("ipv6: false")
    L.append("")
    L.append("# WeChat-safe DNS for TUN (ADR-0009): fake-ip, but IM/NTP/STUN domains get")
    L.append("# real IPs via fake-ip-filter; CN names use domestic DoH; rest falls back.")
    L.append("dns:")
    L.append("  enable: true")
    L.append("  ipv6: false")
    L.append("  enhanced-mode: fake-ip")
    L.append("  fake-ip-range: 198.18.0.1/16")
    L.append("  fake-ip-filter:")
    for pat in ["*.lan", "*.local", "*.localdomain",
                "+.msftconnecttest.com", "+.msftncsi.com",
                "+.stun.*.*", "+.stun.*.*.*",
                "time.*.com", "time.*.apple.com", "ntp.*.com", "+.pool.ntp.org",
                "+.qq.com", "+.weixin.qq.com", "+.wechat.com", "+.weixinbridge.com",
                "+.wechatapp.com", "+.qpic.cn", "+.qlogo.cn", "+.gtimg.cn", "+.tencent.com",
                "+.dingtalk.com", "+.feishu.cn", "+.larksuite.com",
                "+.163.com", "+.126.net", "+.netease.com"]:
        L.append(f"    - '{pat}'")
    L.append("  default-nameserver: [223.5.5.5, 119.29.29.29]")
    L.append("  nameserver: [https://doh.pub/dns-query, https://dns.alidns.com/dns-query]")
    L.append("  nameserver-policy:")
    L.append("    'geosite:cn': [https://doh.pub/dns-query, https://dns.alidns.com/dns-query]")
    L.append("  fallback: [https://dns.google/dns-query, https://cloudflare-dns.com/dns-query]")
    L.append("  fallback-filter: {geoip: true, geoip-code: CN, ipcidr: [240.0.0.0/4]}")
    L.append("")
    L.append("proxy-providers:")
    L.append("  airport:")
    L.append("    type: http")
    L.append(f"    url: \"{AIRPORT_PLACEHOLDER}\"")
    L.append("    interval: 3600")
    L.append("    path: ./providers/airport.yaml")
    L.append("    health-check:")
    L.append("      enable: true")
    L.append(f"      url: {S.HEALTH_URL}")
    L.append("      interval: 300")
    L.append("")
    L.append("proxy-groups:")
    for g in S.GROUPS:
        flt = S.group_filter(g)
        if flt is None:  # member-list group (Apple / Final)
            members = ", ".join(g["members"])
            L.append(f"  - {{name: {g['name']}, type: select, proxies: [{members}]}}")
        elif g["kind"] == "url-test":
            L.append(f"  - name: {g['name']}")
            L.append(f"    type: url-test")
            L.append(f"    use: [airport]")
            L.append(f"    filter: '{flt}'")
            L.append(f"    url: {S.HEALTH_URL}")
            L.append(f"    interval: 300")
            L.append(f"    tolerance: 50")
        else:  # select with region filter
            L.append(f"  - name: {g['name']}")
            L.append(f"    type: select")
            L.append(f"    use: [airport]")
            L.append(f"    filter: '{flt}'")
            if isinstance(g.get("regions"), list):  # AI group: never let an empty region
                L.append(f"    proxies: [Proxy]")   # break the whole config (Mihomo rejects empty groups)
    L.append("")
    L.append("rules:")
    # 0. IM first (TUN process matching): WeChat & friends bypass everything, instantly.
    for r in ["PROCESS-NAME,WeChat,DIRECT", "PROCESS-NAME,QQ,DIRECT",
              "PROCESS-NAME,DingTalk,DIRECT", "PROCESS-NAME,Lark,DIRECT",
              "DOMAIN-SUFFIX,weixin.qq.com,DIRECT", "DOMAIN-SUFFIX,wechat.com,DIRECT",
              "DOMAIN-SUFFIX,qq.com,DIRECT", "DOMAIN-SUFFIX,qpic.cn,DIRECT",
              "DOMAIN-SUFFIX,qlogo.cn,DIRECT"]:
        L.append(f"  - {r}")
    # 1. local provider inlines (precise AI routing), canonical order
    for list_name, policy in S.LOCAL_TIERS:
        for r in S.read_list(list_name):
            L.append(f"  - {r},{policy}")
    # 2. native GEOSITE/GEOIP tail (bundled with the core — no external URLs)
    L.append("  - GEOSITE,github,GitHub")
    L.append("  - GEOSITE,tiktok,TikTok")
    L.append("  - GEOSITE,apple,DIRECT")
    L.append("  - GEOSITE,geolocation-cn,DIRECT")
    L.append("  - GEOIP,CN,DIRECT,no-resolve")
    L.append("  - MATCH,Final")
    L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------------ Surge -----
def build_surge() -> str:
    L: list[str] = []
    L.append("# ============================================================================")
    L.append("#  AI-Ultimate-Network — Surge config. GENERATED — DO NOT EDIT BY HAND.")
    L.append("#  Rebuild: python3 scripts/build.py --target surge")
    L.append("#  SETUP: add your airport nodes via Surge's Subscription/Proxy, then the")
    L.append("#  groups below auto-select them by region regex (see docs/USAGE.md).")
    L.append("# ============================================================================")
    L.append("[General]")
    L.append("loglevel = notify")
    L.append("ipv6 = false")
    L.append("dns-server = 223.5.5.5, 119.29.29.29, system")
    L.append("skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local")
    L.append("")
    L.append("[Proxy]")
    L.append("# Add your nodes here or via Surge Subscription. Groups use include-all-proxies.")
    L.append("")
    L.append("[Proxy Group]")
    for g in S.GROUPS:
        flt = S.group_filter(g)
        if flt is None:
            members = ", ".join(g["members"])
            L.append(f"{g['name']} = select, {members}")
        elif g["kind"] == "url-test":
            L.append(f"{g['name']} = url-test, include-all-proxies=true, "
                     f"policy-regex-filter={flt}, url={S.HEALTH_URL}, interval=300, tolerance=50")
        else:
            L.append(f"{g['name']} = select, include-all-proxies=true, policy-regex-filter={flt}")
    L.append("")
    L.append("[Rule]")
    for list_name, policy in S.LOCAL_TIERS:
        for r in S.read_list(list_name):
            L.append(f"{r},{policy}")
    L.append("GEOIP,CN,DIRECT")
    L.append("FINAL,Final")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------- Clash Verge Global Merge -----
def build_clash_merge() -> str:
    """
    Overlay for Clash Verge's '全局扩展覆写配置 (Global Merge)'. Applies our AI strategy
    on TOP of ANY active subscription profile — works across multiple subscriptions on
    Mac and Windows with zero per-sub editing. Groups use include-all (pull nodes from
    whatever profile is active). Only AI/Apple/China are overridden; the airport's own
    rules + final policy still handle everything else. Coexists with a Global Script.
    """
    wanted = ["Claude", "ChatGPT", "GitHub", "Google", "TikTok", "Proxy", "Apple"]
    L: list[str] = []
    L.append("# ============================================================================")
    L.append("#  AI-Ultimate-Network — Clash Verge GLOBAL MERGE overlay. GENERATED — DO NOT EDIT.")
    L.append("#  Rebuild: python3 scripts/build.py --target clash-merge")
    L.append("#")
    L.append("#  Paste ALL of this into Clash Verge:  设置 → (选中订阅) 编辑 → 全局扩展覆写配置")
    L.append("#  (Settings → Merge / Global Extended Config). It overlays these groups + AI")
    L.append("#  rules onto EVERY subscription automatically. No node URLs needed.")
    L.append("# ============================================================================")
    L.append("prepend-proxy-groups:")
    for name in wanted:
        g = next(x for x in S.GROUPS if x["name"] == name)
        flt = S.group_filter(g)
        if flt is None:  # Apple -> member list
            members = ", ".join(g["members"])
            L.append(f"  - {{name: {name}, type: select, proxies: [{members}]}}")
        elif isinstance(g.get("regions"), list):  # AI group: fallback to Proxy so an empty
            L.append(f"  - {{name: {name}, type: select, include-all: true, filter: '{flt}', "
                     f"proxies: [Proxy]}}")       # region never breaks the whole config
        else:  # Proxy (matches all) — never empty, no fallback needed
            L.append(f"  - {{name: {name}, type: select, include-all: true, filter: '{flt}'}}")
    L.append("prepend-rules:")
    merge_tiers = [
        ("anthropic.list", "Claude"), ("openai.list", "ChatGPT"),
        ("github.list", "GitHub"), ("google.list", "Google"),
        ("apple.list", "Apple"), ("tiktok.list", "TikTok"),
        ("ai-extra.list", "Proxy"), ("china.list", "DIRECT"),
    ]
    for list_name, policy in merge_tiers:
        for r in S.read_list(list_name):
            L.append(f"  - {r},{policy}")
    L.append("  - GEOSITE,github,GitHub")
    L.append("  - GEOSITE,tiktok,TikTok")
    L.append("  - GEOSITE,apple,DIRECT")
    L.append("  - GEOSITE,geolocation-cn,DIRECT")
    L.append("  - GEOIP,CN,DIRECT,no-resolve")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------- Clash Verge Global Script -----
def build_clash_script() -> str:
    """
    Clash Verge '全局扩展脚本 (Global Script)' — the most reliable injection point.
    Runs in the enhance stage and builds each group's node list from the ACTUAL proxy
    names (no include-all, no empty-group crash, not clobbered by merge ordering).
    If you already have a Global Script, paste the BEGIN..END block inside your own
    main(config) right before `return config`.
    """
    tiers = [
        ("anthropic.list", "Claude"), ("openai.list", "ChatGPT"),
        ("github.list", "GitHub"), ("google.list", "Google"),
        ("apple.list", "Apple"), ("tiktok.list", "TikTok"),
        ("ai-extra.list", "Proxy"), ("china.list", "DIRECT"),
    ]
    rules: list[str] = []
    # IM first: under TUN, mihomo matches by process — the entire WeChat/QQ/DingTalk/
    # Feishu process goes DIRECT instantly, no DNS or GEOIP lookup involved.
    rules += ["PROCESS-NAME,WeChat,DIRECT", "PROCESS-NAME,QQ,DIRECT",
              "PROCESS-NAME,DingTalk,DIRECT", "PROCESS-NAME,Lark,DIRECT",
              "DOMAIN-SUFFIX,weixin.qq.com,DIRECT", "DOMAIN-SUFFIX,wechat.com,DIRECT",
              "DOMAIN-SUFFIX,qq.com,DIRECT", "DOMAIN-SUFFIX,qpic.cn,DIRECT",
              "DOMAIN-SUFFIX,qlogo.cn,DIRECT"]
    for list_name, policy in tiers:
        for r in S.read_list(list_name):
            rules.append(f"{r},{policy}")
    rules += ["GEOSITE,github,GitHub", "GEOSITE,tiktok,TikTok", "GEOSITE,apple,DIRECT",
              "GEOSITE,geolocation-cn,DIRECT", "GEOIP,CN,DIRECT,no-resolve"]
    rules_js = ",\n    ".join(json.dumps(r) for r in rules)
    f_claude = json.dumps(S.region_filter(["TW"]), ensure_ascii=False)
    f_chatgpt = json.dumps(S.region_filter(["US", "SG", "JP", "HK"]), ensure_ascii=False)
    f_github = json.dumps(S.region_filter(["HK"]), ensure_ascii=False)
    f_google = json.dumps(S.region_filter(["HK", "JP", "SG", "US"]), ensure_ascii=False)
    f_tiktok = json.dumps(S.region_filter(["JP", "TW", "SG"]), ensure_ascii=False)
    return f'''// ============================================================================
// AI-Ultimate-Network — Clash Verge GLOBAL SCRIPT. GENERATED — DO NOT EDIT.
// Rebuild: python3 scripts/build.py --target clash-script
//
// Put this in Clash Verge:  设置 → 全局扩展脚本 (Global Script).
// If you ALREADY have a Global Script (e.g. Adobe block), keep ONE main() and paste
// only the code between "BEGIN" and "END" inside it, just before `return config`.
//
// Groups use include-all + filter, so they pull nodes from the main subscription AND
// any airports you fuse in via proxy-providers (multi-airport). A region with no node
// falls back to Proxy (never DIRECT), so an empty region can't break the config.
// ============================================================================
function main(config) {{
  // ===== AI-Ultimate-Network BEGIN =====
  // Base subscriptions may enable IPv6 even though the standalone profile does not.
  // Disable both kernel IPv6 handling and AAAA answers to avoid TUN direct-path stalls.
  config["ipv6"] = false;
  // --- DNS: deterministic, WeChat-safe (see docs/adr/ADR-0009-wechat-tun-dns.md) ---
  // Root cause of "WeChat stuck at 收取中 for minutes under TUN": fake-ip answers for
  // IM domains break WeChat's own connection logic. Fix = own the dns section:
  // fake-ip mode BUT with IM/NTP/STUN domains excluded (fake-ip-filter), domestic DoH
  // for CN names, foreign fallback for the rest. Verge's "DNS 覆写" toggle can stay OFF.
  config["dns"] = {{
    enable: true,
    ipv6: false,
    "enhanced-mode": "fake-ip",
    "fake-ip-range": "198.18.0.1/16",
    "fake-ip-filter": [
      "*.lan", "*.local", "*.localdomain",
      "+.msftconnecttest.com", "+.msftncsi.com",
      "+.stun.*.*", "+.stun.*.*.*",
      "time.*.com", "time.*.apple.com", "ntp.*.com", "+.pool.ntp.org",
      // IM — WeChat/QQ/DingTalk/Feishu must get REAL IPs or they stall under TUN:
      "+.qq.com", "+.weixin.qq.com", "+.wechat.com", "+.weixinbridge.com",
      "+.wechatapp.com", "+.qpic.cn", "+.qlogo.cn", "+.gtimg.cn", "+.tencent.com",
      "+.dingtalk.com", "+.feishu.cn", "+.larksuite.com",
      "+.163.com", "+.126.net", "+.netease.com"
    ],
    "default-nameserver": ["223.5.5.5", "119.29.29.29"],
    nameserver: ["https://doh.pub/dns-query", "https://dns.alidns.com/dns-query"],
    "nameserver-policy": {{
      "geosite:cn": ["https://doh.pub/dns-query", "https://dns.alidns.com/dns-query"]
    }},
    fallback: ["https://dns.google/dns-query", "https://cloudflare-dns.com/dns-query"],
    "fallback-filter": {{ geoip: true, "geoip-code": "CN", ipcidr: ["240.0.0.0/4"] }}
  }};
  var mk = function (name, filter) {{
    return {{ name: name, type: "select", "include-all": true, filter: filter, proxies: ["Proxy"] }};
  }};
  var aiGroups = [
    mk("Claude", {f_claude}),
    mk("ChatGPT", {f_chatgpt}),
    mk("GitHub", {f_github}),
    mk("Google", {f_google}),
    mk("TikTok", {f_tiktok}),
    {{ name: "Proxy", type: "select", "include-all": true }},
    {{ name: "Apple", type: "select", proxies: ["DIRECT", "Proxy"] }}
  ];
  config["proxy-groups"] = aiGroups.concat(config["proxy-groups"] || []);
  var aiRules = [
    {rules_js}
  ];
  config["rules"] = aiRules.concat(config["rules"] || []);
  // ===== AI-Ultimate-Network END =====
  return config;
}}
'''


# --------------------------------------- Clash Verge Global Script + Adobe block ---
def build_clash_script_adobe() -> str:
    """
    'Fused' Global Script: the owner's Adobe-telemetry block + the full AI-Ultimate
    block in ONE main(). Spliced from build_clash_script()'s BEGIN..END section so
    the two script variants can never drift. Paste this WHOLE file into Clash Verge
    设置 → 全局扩展脚本 — full-select replace, nothing else needed.
    """
    base = build_clash_script()
    begin = base.index("  // ===== AI-Ultimate-Network BEGIN =====")
    end = base.index("  // ===== AI-Ultimate-Network END =====") \
        + len("  // ===== AI-Ultimate-Network END =====")
    ai_block = base[begin:end]
    return f'''// ============================================================================
// AI-Ultimate-Network — Clash Verge GLOBAL SCRIPT (Adobe + AI fused). GENERATED.
// Rebuild: python3 scripts/build.py --target clash-script-adobe
//
// ONE main(): Adobe telemetry block (RULE-SET -> REJECT) + the complete
// AI-Ultimate block (WeChat-safe DNS, IM process rules, 5 strategy groups).
// Paste this ENTIRE file into Clash Verge: 设置 → 全局扩展脚本 (full replace).
// Copy from the raw file only — never via Markdown editors/IM apps, they inject
// invisible zero-width characters that break JS parsing (learned the hard way).
// ============================================================================
function main(config) {{
  // ===== Adobe block =====
  config["rule-providers"] = config["rule-providers"] || {{}};
  config["rule-providers"]["adobe-block"] = {{
    type: "http", behavior: "classical", format: "yaml",
    url: "https://fastly.jsdelivr.net/gh/ignaciocastro/a-dove-is-dumb@latest/clash.yaml",
    path: "./ruleset/adobe-block.yaml", interval: 86400
  }};
  config.rules = config.rules || [];
  config.rules.unshift("RULE-SET,adobe-block,REJECT");

{ai_block}
  return config;
}}
'''


BUILDERS = {
    "shadowrocket": build_shadowrocket,
    "clash": build_clash,
    "clash-merge": build_clash_merge,
    "clash-script": build_clash_script,
    "clash-script-adobe": build_clash_script_adobe,
    "surge": build_surge,
}


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    target = None
    if "--target" in args:
        i = args.index("--target")
        target = args[i + 1] if i + 1 < len(args) else None
        if target not in BUILDERS:
            raise SystemExit(f"[build] unknown target {target!r}; choose from {list(BUILDERS)}")
    targets = [target] if target else list(BUILDERS)

    rc = 0
    for t in targets:
        built = BUILDERS[t]()
        path = OUT[t]
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != built:
                print(f"[build] --check FAILED: {path.relative_to(ROOT)} is stale. "
                      f"Run: python3 scripts/build.py")
                rc = 1
            else:
                print(f"[build] --check OK: {path.relative_to(ROOT)}")
        else:
            path.write_text(built, encoding="utf-8")
            n = sum(1 for ln in built.splitlines()
                    if "," in ln and ln.lstrip("# -").split(",", 1)[0] in {
                        "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "RULE-SET", "GEOIP",
                        "GEOSITE", "IP-CIDR", "FINAL", "MATCH"})
            print(f"[build] wrote {path.relative_to(ROOT)} (~{n} rules).")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
