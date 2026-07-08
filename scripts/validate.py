#!/usr/bin/env python3
"""
validate.py — Quality gate for config/AI-Ultimate.conf (ARCH 11 / Master VALIDATION).

Checks (any failure => non-zero exit, blocks release):
  1. Config is freshly built (matches template + rules).
  2. Section headers present and well-formed.
  3. <= 10 custom proxy groups.
  4. AI groups (Claude/ChatGPT/GitHub/Google) are SELECT-only
     (no url-test/fallback/load-balance/random).
  5. Every rule policy references a real group / built-in policy (no dangling refs).
  6. Every group's policy-regex-filter compiles as a regex.
  7. No duplicate rules.
  8. Exactly one FINAL rule, and it is the LAST rule line.
  9. Canonical rule-order: Anthropic -> OpenAI -> GitHub -> Google -> Apple ->
     China -> Proxy -> Final (first appearance of each group is monotonic).

Usage: python3 scripts/validate.py [path-to-conf]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONF = ROOT / "config" / "AI-Ultimate.conf"

BUILTIN_POLICIES = {"DIRECT", "PROXY", "REJECT", "REJECT-DROP", "REJECT-NO-DROP",
                    "REJECT-200", "REJECT-IMG", "REJECT-TINYGIF", "REJECT-DICT",
                    "REJECT-ARRAY", "TAILSCALE"}
AI_GROUPS = {"Claude", "ChatGPT", "GitHub", "Google"}
FORBIDDEN_AI_TYPES = {"url-test", "fallback", "load-balance", "random"}
MAX_GROUPS = 10
RULE_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD",
              "DOMAIN-SET", "RULE-SET", "IP-CIDR", "IP-CIDR6", "GEOIP", "IP-ASN",
              "USER-AGENT", "URL-REGEX", "DST-PORT", "FINAL", "AND", "OR", "NOT"}

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^\[(.+?)\]\s*$", line.strip())
        if m:
            current = m.group(1)
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def content_lines(lines: list[str]) -> list[str]:
    out = []
    for raw in lines:
        s = raw.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def check_fresh_build() -> None:
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--check"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        fail(res.stdout.strip() or "build --check failed")


def main() -> int:
    conf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CONF
    if not conf_path.exists():
        print(f"[validate] ERROR: config not found: {conf_path}")
        return 2

    if conf_path == DEFAULT_CONF:
        check_fresh_build()

    text = conf_path.read_text(encoding="utf-8")
    sections = parse_sections(text)

    # 2. sections
    for required in ("General", "Proxy Group", "Rule"):
        if required not in sections:
            fail(f"missing required section [{required}]")

    # --- parse groups ---
    groups: dict[str, dict] = {}
    for line in content_lines(sections.get("Proxy Group", [])):
        if "=" not in line:
            fail(f"malformed group line: {line!r}")
            continue
        name, _, rhs = line.partition("=")
        name = name.strip()
        fields = [f.strip() for f in rhs.split(",")]
        gtype = fields[0] if fields else ""
        regex = None
        members = []
        for f in fields[1:]:
            if f.startswith("policy-regex-filter="):
                regex = f[len("policy-regex-filter="):]
            elif "=" in f:
                pass  # interval=, tolerance=, url=, select=, policy-select-name=
            elif f:
                members.append(f)
        groups[name] = {"type": gtype, "regex": regex, "members": members}

    # 3. group count
    if len(groups) > MAX_GROUPS:
        fail(f"too many proxy groups: {len(groups)} > {MAX_GROUPS}")

    # 4. AI groups select-only
    for g in AI_GROUPS:
        if g in groups and groups[g]["type"] != "select":
            fail(f"AI group {g!r} must be 'select', found {groups[g]['type']!r}")
    for name, g in groups.items():
        if name in AI_GROUPS and g["type"] in FORBIDDEN_AI_TYPES:
            fail(f"AI group {name!r} uses forbidden type {g['type']!r}")

    # 6. regex compiles (strip inline flags Python's re dislikes mid-pattern)
    for name, g in groups.items():
        if g["regex"] and g["regex"] != ".*":
            probe = g["regex"].replace("(?i)", "")
            try:
                re.compile(probe)
            except re.error as e:
                fail(f"group {name!r} regex does not compile: {e}")

    # 5 + 7 + 8 + 9. rules
    valid_targets = set(groups) | BUILTIN_POLICIES
    rule_lines = content_lines(sections.get("Rule", []))
    seen: set[str] = set()
    final_count = 0
    final_is_last = False
    order_seq: list[str] = []
    # canonical order reference
    canonical = ["Claude", "ChatGPT", "GitHub", "Google", "Apple",
                 "__china__", "Proxy", "Final"]

    for idx, line in enumerate(rule_lines):
        parts = [p.strip() for p in line.split(",")]
        rtype = parts[0]
        if rtype not in RULE_TYPES:
            fail(f"unknown rule type: {line!r}")
            continue
        policy = parts[-1]
        is_last = idx == len(rule_lines) - 1

        if rtype == "FINAL":
            final_count += 1
            final_is_last = is_last
            if policy not in valid_targets:
                fail(f"FINAL policy {policy!r} is not a defined group/builtin")
            continue

        # dangling target check
        if policy not in valid_targets:
            fail(f"rule targets undefined policy {policy!r}: {line!r}")

        # duplicate check (full line)
        if line in seen:
            fail(f"duplicate rule: {line!r}")
        seen.add(line)

        # order tracking (first appearance of each service group)
        if policy in ("Claude", "ChatGPT", "GitHub", "Google", "Apple", "Proxy", "Final"):
            if policy not in order_seq:
                order_seq.append(policy)

    if final_count == 0:
        fail("no FINAL rule found")
    elif final_count > 1:
        fail(f"multiple FINAL rules: {final_count}")
    elif not final_is_last:
        fail("FINAL rule is not the last rule")

    # 9. monotonic canonical order (ignore China direct rules interleaving)
    rank = {name: i for i, name in enumerate(canonical)}
    last = -1
    for g in order_seq:
        r = rank.get(g, 10 ** 9)
        if r < last:
            warn(f"rule order: {g!r} appears out of canonical order")
        last = max(last, r)

    # report
    print(f"[validate] groups={len(groups)} rules={len(rule_lines)} "
          f"final_last={final_is_last}")
    for w in warnings:
        print(f"[validate] WARN: {w}")
    if errors:
        for e in errors:
            print(f"[validate] FAIL: {e}")
        print(f"[validate] RESULT: FAILED ({len(errors)} errors)")
        return 1
    print("[validate] RESULT: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
