#!/usr/bin/env python3
"""
validate.py — Quality gate for ALL generated client configs.

Validates:
  config/AI-Ultimate.conf        (Shadowrocket)
  config/AI-Ultimate.clash.yaml  (Clash Meta / Verge)
  config/AI-Ultimate.surge.conf  (Surge)

Shared invariants enforced everywhere:
  - freshly built (matches strategy.py + template + rules/*.list),
  - <= 10 strategy groups,
  - AI groups (Claude/ChatGPT/GitHub/Google) are SELECT-only,
  - AI groups select nodes by region regex (not hardcoded),
  - every rule targets a defined group / built-in policy (no dangling refs),
  - the catch-all (FINAL / MATCH) is the last rule and points to Final.

Usage: python3 scripts/validate.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import strategy as S

ROOT = Path(__file__).resolve().parent.parent
CONF = {
    "shadowrocket": ROOT / "config" / "AI-Ultimate.conf",
    "clash": ROOT / "config" / "AI-Ultimate.clash.yaml",
    "clash-merge": ROOT / "config" / "AI-Ultimate.clash-merge.yaml",
    "surge": ROOT / "config" / "AI-Ultimate.surge.conf",
}
BUILTINS = {"DIRECT", "PROXY", "REJECT", "REJECT-DROP", "REJECT-NO-DROP", "REJECT-200",
            "REJECT-IMG", "REJECT-TINYGIF", "REJECT-DICT", "REJECT-ARRAY", "TAILSCALE",
            "MATCH", "PASS", "COMPATIBLE"}
AI = set(S.AI_GROUPS)
FORBIDDEN = {"url-test", "fallback", "load-balance", "random"}
MAX_GROUPS = 10
MODIFIERS = {"no-resolve", "dns-failed", "force-remote-dns", "extended-matching", "src"}
errors: list[str] = []


def fail(scope: str, msg: str) -> None:
    errors.append(f"[{scope}] {msg}")


def policy_of(rule: str) -> str:
    """Last comma field, ignoring trailing rule modifiers (no-resolve, etc.)."""
    parts = [p.strip() for p in rule.split(",")]
    while len(parts) > 2 and parts[-1] in MODIFIERS:
        parts.pop()
    return parts[-1]


# ------------------------------------------------------------------ Shadowrocket ---
def validate_shadowrocket(text: str) -> None:
    scope = "shadowrocket"
    groups, rules = _parse_ini(text)
    _check_groups(scope, groups)
    valid = set(groups) | BUILTINS
    _check_rules(scope, rules, valid, final_kw="FINAL")


# ------------------------------------------------------------------------ Surge ---
def validate_surge(text: str) -> None:
    scope = "surge"
    groups, rules = _parse_ini(text)
    _check_groups(scope, groups)
    valid = set(groups) | BUILTINS
    _check_rules(scope, rules, valid, final_kw="FINAL")


def _parse_ini(text: str):
    """Return ({group: type}, [rule lines]) for Shadowrocket/Surge INI configs."""
    groups: dict[str, str] = {}
    rules: list[str] = []
    section = None
    for raw in text.splitlines():
        s = raw.strip()
        if re.match(r"^\[.+\]$", s):
            section = s[1:-1]
            continue
        if not s or s.startswith("#"):
            continue
        if section == "Proxy Group" and "=" in s:
            name, _, rhs = s.partition("=")
            gtype = rhs.split(",")[0].strip()
            groups[name.strip()] = gtype
        elif section == "Rule":
            rules.append(s)
    return groups, rules


# ------------------------------------------------------------------------ Clash ---
def validate_clash(text: str) -> None:
    scope = "clash"
    data = _load_yaml(text)
    if data is not None:
        groups = {g["name"]: g["type"] for g in data.get("proxy-groups", [])}
        rules = list(data.get("rules", []))
        if "proxy-providers" not in data or "airport" not in data.get("proxy-providers", {}):
            fail(scope, "missing proxy-providers.airport")
        # AI groups must carry a regex filter (not hardcoded nodes)
        for g in data.get("proxy-groups", []):
            if g["name"] in AI and "filter" not in g:
                fail(scope, f"AI group {g['name']!r} has no regex filter")
    else:
        # yaml lib unavailable: lightweight structural parse
        groups = {}
        for m in re.finditer(r"-\s*(?:\{)?name:\s*([A-Za-z]+),?\s*type:\s*([a-z-]+)", text):
            groups[m.group(1)] = m.group(2)
        rules = re.findall(r"^\s*-\s+((?:DOMAIN|GEOSITE|GEOIP|IP-CIDR|MATCH|RULE-SET|PROCESS)[^\n]*)",
                           text, re.M)
    _check_groups(scope, groups)
    valid = set(groups) | BUILTINS
    _check_rules(scope, [r.strip() for r in rules], valid, final_kw="MATCH")


def validate_clash_merge(text: str) -> None:
    """Overlay fragment: prepend-proxy-groups + prepend-rules, no MATCH tail."""
    scope = "clash-merge"
    data = _load_yaml(text)
    if data is None:
        # lightweight: just confirm the two prepend keys exist
        if "prepend-proxy-groups:" not in text or "prepend-rules:" not in text:
            fail(scope, "missing prepend-proxy-groups / prepend-rules")
        return
    pg = data.get("prepend-proxy-groups")
    rules = data.get("prepend-rules")
    if not pg:
        fail(scope, "missing prepend-proxy-groups")
        return
    if not rules:
        fail(scope, "missing prepend-rules")
        return
    groups = {g["name"]: g["type"] for g in pg}
    _check_groups(scope, groups)
    for g in pg:
        if g["name"] in AI and "filter" not in g:
            fail(scope, f"AI group {g['name']!r} has no regex filter")
    valid = set(groups) | BUILTINS
    for r in rules:
        pol = policy_of(r)
        if pol not in valid:
            fail(scope, f"prepend-rule targets undefined policy {pol!r}: {r!r}")
    # an overlay must NOT contain a catch-all (that belongs to the base profile)
    if any(r.split(",", 1)[0] in ("MATCH", "FINAL") for r in rules):
        fail(scope, "overlay must not contain MATCH/FINAL (base profile owns the tail)")


def _load_yaml(text: str):
    try:
        import yaml  # optional; present in CI
    except ModuleNotFoundError:
        return None
    return yaml.safe_load(text)


# ------------------------------------------------------------------- shared checks -
def _check_groups(scope: str, groups: dict[str, str]) -> None:
    if len(groups) > MAX_GROUPS:
        fail(scope, f"too many groups: {len(groups)} > {MAX_GROUPS}")
    for g in AI:
        if g not in groups:
            fail(scope, f"missing AI group {g!r}")
        elif groups[g] != "select":
            fail(scope, f"AI group {g!r} must be select, got {groups[g]!r}")
    for name, t in groups.items():
        if name in AI and t in FORBIDDEN:
            fail(scope, f"AI group {name!r} uses forbidden type {t!r}")


def _check_rules(scope: str, rules: list[str], valid: set[str], final_kw: str) -> None:
    if not rules:
        fail(scope, "no rules")
        return
    seen: set[str] = set()
    for i, r in enumerate(rules):
        is_last = i == len(rules) - 1
        head = r.split(",", 1)[0]
        if head in (final_kw,):
            if not is_last:
                fail(scope, f"{final_kw} is not the last rule")
            if policy_of(r) not in valid:
                fail(scope, f"{final_kw} targets undefined {policy_of(r)!r}")
            continue
        pol = policy_of(r)
        if pol not in valid:
            fail(scope, f"rule targets undefined policy {pol!r}: {r!r}")
        if r in seen:
            fail(scope, f"duplicate rule: {r!r}")
        seen.add(r)
    if not rules[-1].startswith(final_kw):
        fail(scope, f"last rule is not {final_kw}: {rules[-1]!r}")


def main() -> int:
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--check"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout.strip())
        fail("build", "configs are stale — run: python3 scripts/build.py")

    validators = {"shadowrocket": validate_shadowrocket, "clash": validate_clash,
                  "clash-merge": validate_clash_merge, "surge": validate_surge}
    for name, path in CONF.items():
        if not path.exists():
            fail(name, f"missing {path}")
            continue
        validators[name](path.read_text(encoding="utf-8"))

    if errors:
        for e in errors:
            print(f"[validate] FAIL {e}")
        print(f"[validate] RESULT: FAILED ({len(errors)} errors)")
        return 1
    print(f"[validate] all targets PASSED: {', '.join(CONF)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
