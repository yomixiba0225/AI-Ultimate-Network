#!/usr/bin/env python3
"""
build.py — Assemble config/AI-Ultimate.conf from the template + rules/*.list.

Configuration-as-code (ARCH 5): the shipped .conf is GENERATED, never hand-edited.
Every `#!INCLUDE <file> <group>` line in the template is replaced by the rules in
rules/<file>, each with `,<group>` appended as its policy.

Usage:
    python3 scripts/build.py            # build
    python3 scripts/build.py --check    # build to memory, fail if on-disk differs
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "config" / "AI-Ultimate.template.conf"
OUTPUT = ROOT / "config" / "AI-Ultimate.conf"
RULES_DIR = ROOT / "rules"

INCLUDE = "#!INCLUDE"
HEADER = (
    "# ============================================================================\n"
    "#  AI-Ultimate.conf — GENERATED FILE. DO NOT EDIT BY HAND.\n"
    "#  Source: config/AI-Ultimate.template.conf + rules/*.list\n"
    "#  Rebuild: python3 scripts/build.py\n"
    "# ============================================================================\n"
)


def load_rule_lines(list_name: str) -> list[str]:
    """Return TYPE,value lines from a rules/*.list file (comments/blanks stripped)."""
    path = RULES_DIR / list_name
    if not path.exists():
        raise SystemExit(f"[build] ERROR: missing rules file: {path}")
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def expand(template_text: str) -> str:
    result: list[str] = [HEADER]
    for line in template_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(INCLUDE):
            parts = stripped.split()
            if len(parts) != 3:
                raise SystemExit(f"[build] ERROR: bad INCLUDE directive: {line!r}")
            _, list_name, group = parts
            rules = load_rule_lines(list_name)
            result.append(f"# --- expanded from rules/{list_name} -> {group} "
                          f"({len(rules)} rules) ---")
            for rule in rules:
                result.append(f"{rule},{group}")
        else:
            result.append(line)
    text = "\n".join(result)
    if not text.endswith("\n"):
        text += "\n"
    return text


def main() -> int:
    if not TEMPLATE.exists():
        raise SystemExit(f"[build] ERROR: missing template: {TEMPLATE}")
    built = expand(TEMPLATE.read_text(encoding="utf-8"))

    if "--check" in sys.argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != built:
            print("[build] --check FAILED: config/AI-Ultimate.conf is stale. "
                  "Run: python3 scripts/build.py")
            return 1
        print("[build] --check OK: built config matches on-disk.")
        return 0

    OUTPUT.write_text(built, encoding="utf-8")
    rule_count = sum(1 for ln in built.splitlines()
                     if ln and not ln.startswith("#") and "," in ln
                     and ln.split(",", 1)[0] in {
                         "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-SET",
                         "DOMAIN-WILDCARD", "RULE-SET", "IP-CIDR", "IP-CIDR6",
                         "GEOIP", "IP-ASN", "USER-AGENT", "URL-REGEX", "FINAL",
                         "DST-PORT", "AND", "OR", "NOT",
                     })
    print(f"[build] wrote {OUTPUT.relative_to(ROOT)} ({rule_count} rules).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
