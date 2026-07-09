#!/usr/bin/env python3
"""
strategy.py — the single, client-agnostic source of truth for AI-Ultimate-Network.

Shadowrocket, Clash Meta (Clash Verge) and Surge configs are all generated from the
data here + the shared rules/*.list providers, so the strategy can never drift between
clients. Each client's emitter (in build.py) renders this into its native syntax.

Design contracts (see docs/DESIGN.md, docs/adr/):
  - AI groups (Claude/ChatGPT/GitHub/Google) are SELECT-only.
  - <=10 strategy groups.
  - Nodes auto-join by region regex; never hardcoded. \\bXX\\b avoids US matching AUS.
  - Canonical rule order: Anthropic -> OpenAI -> GitHub -> Google -> Apple -> China -> Proxy -> Final.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"

# --- Regions -> name tokens (EN + zh-Hans + zh-Hant). \b guards short codes. -------
REGIONS: dict[str, list[str]] = {
    "TW": [r"\bTW\b", "Taiwan", "台湾", "台灣"],
    "US": [r"\bUS\b", "USA", "美国", "美國"],
    "SG": [r"\bSG\b", "Singapore", "新加坡", "狮城"],
    "JP": [r"\bJP\b", "Japan", "日本"],
    "HK": [r"\bHK\b", "Hong ?Kong", "香港"],
}


def region_filter(codes: list[str]) -> str:
    """Case-insensitive regex matching any node whose name contains a region token."""
    toks = [t for c in codes for t in REGIONS[c]]
    return "(?i)(" + "|".join(toks) + ")"


# --- Strategy groups (<=10). 'select' unless noted. --------------------------------
# kind: select | url-test ; regions: list[str] | "ALL" ; members: explicit policies.
GROUPS: list[dict] = [
    {"name": "Claude",  "kind": "select",   "regions": ["TW"]},
    # ChatGPT group covers all OpenAI incl. Codex (one group, per user request).
    {"name": "ChatGPT", "kind": "select",   "regions": ["US", "SG", "JP", "HK"]},
    {"name": "GitHub",  "kind": "select",   "regions": ["HK"]},
    {"name": "Google",  "kind": "select",   "regions": ["HK", "JP", "SG", "US"]},
    {"name": "TikTok",  "kind": "select",   "regions": ["JP", "TW", "SG"]},
    {"name": "Proxy",   "kind": "select",   "regions": "ALL"},
    {"name": "Auto",    "kind": "url-test", "regions": "ALL"},
    {"name": "Apple",   "kind": "select",   "members": ["DIRECT", "Proxy"]},
    {"name": "Final",   "kind": "select",   "members": ["Proxy", "DIRECT"]},
]

# AI groups must stay Select-only (anti-ban). TikTok is a region-select group too.
AI_GROUPS = ("Claude", "ChatGPT", "GitHub", "Google")
REGION_SELECT_GROUPS = tuple(
    g["name"] for g in GROUPS if g["kind"] == "select" and isinstance(g.get("regions"), list)
)  # Claude, ChatGPT, GitHub, Google, TikTok
HEALTH_URL = "http://www.gstatic.com/generate_204"

# --- Local provider inlines, in canonical order. (file, target policy/group) -------
LOCAL_TIERS: list[tuple[str, str]] = [
    ("anthropic.list", "Claude"),
    ("openai.list",    "ChatGPT"),
    ("github.list",    "GitHub"),
    ("google.list",    "Google"),
    ("apple.list",     "Apple"),
    ("tiktok.list",    "TikTok"),
    ("ai-extra.list",  "Proxy"),
    ("china.list",     "DIRECT"),
    ("proxy.list",     "Proxy"),
]


def read_list(list_name: str) -> list[str]:
    """Return 'TYPE,value' lines from rules/<list_name> (comments/blanks stripped)."""
    path = RULES_DIR / list_name
    if not path.exists():
        raise SystemExit(f"[strategy] missing rules file: {path}")
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def group_filter(group: dict) -> str | None:
    """Region regex for a group, or '.*' for ALL, or None for member-list groups."""
    regions = group.get("regions")
    if regions == "ALL":
        return ".*"
    if regions:
        return region_filter(regions)
    return None
