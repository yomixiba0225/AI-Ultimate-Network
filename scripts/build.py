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

import sys
from pathlib import Path

import strategy as S

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "config" / "AI-Ultimate.template.conf"
OUT = {
    "shadowrocket": ROOT / "config" / "AI-Ultimate.conf",
    "clash": ROOT / "config" / "AI-Ultimate.clash.yaml",
    "clash-merge": ROOT / "config" / "AI-Ultimate.clash-merge.yaml",
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
    # 1. local provider inlines (precise AI routing), canonical order
    for list_name, policy in S.LOCAL_TIERS:
        for r in S.read_list(list_name):
            L.append(f"  - {r},{policy}")
    # 2. native GEOSITE/GEOIP tail (bundled with the core — no external URLs)
    L.append("  - GEOSITE,github,GitHub")
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
    wanted = ["Claude", "ChatGPT", "GitHub", "Google", "Proxy", "Apple"]
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
        ("apple.list", "Apple"), ("ai-extra.list", "Proxy"), ("china.list", "DIRECT"),
    ]
    for list_name, policy in merge_tiers:
        for r in S.read_list(list_name):
            L.append(f"  - {r},{policy}")
    L.append("  - GEOSITE,github,GitHub")
    L.append("  - GEOSITE,apple,DIRECT")
    L.append("  - GEOSITE,geolocation-cn,DIRECT")
    L.append("  - GEOIP,CN,DIRECT,no-resolve")
    L.append("")
    return "\n".join(L)


BUILDERS = {
    "shadowrocket": build_shadowrocket,
    "clash": build_clash,
    "clash-merge": build_clash_merge,
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
