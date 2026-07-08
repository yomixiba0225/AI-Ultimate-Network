#!/usr/bin/env python3
"""
test_config.py — acceptance tests for the built Shadowrocket config.

Run:  python3 -m unittest discover -s tests
  or: python3 tests/test_config.py

Maps to PRD 20 / Master SUCCESS acceptance criteria. Pure stdlib, no deps.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "config" / "AI-Ultimate.conf"
BUILD = ROOT / "scripts" / "build.py"
VALIDATE = ROOT / "scripts" / "validate.py"


def section(text, name):
    lines, cur = [], None
    for ln in text.splitlines():
        m = re.match(r"^\[(.+?)\]\s*$", ln.strip())
        if m:
            cur = m.group(1)
            continue
        if cur == name:
            lines.append(ln)
    return lines


class TestBuildAndValidate(unittest.TestCase):
    def test_build_is_fresh(self):
        r = subprocess.run([sys.executable, str(BUILD), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_validate_passes(self):
        r = subprocess.run([sys.executable, str(VALIDATE)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestConfigInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CONF.read_text(encoding="utf-8")
        cls.groups = {}
        for ln in section(cls.text, "Proxy Group"):
            s = ln.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            name, _, rhs = s.partition("=")
            cls.groups[name.strip()] = rhs.strip()
        cls.rules = [ln.strip() for ln in section(cls.text, "Rule")
                     if ln.strip() and not ln.strip().startswith("#")]

    def test_at_most_10_groups(self):
        self.assertLessEqual(len(self.groups), 10)

    def test_required_ai_groups_exist(self):
        for g in ("Claude", "ChatGPT", "GitHub", "Google"):
            self.assertIn(g, self.groups)

    def test_ai_groups_are_select_only(self):
        for g in ("Claude", "ChatGPT", "GitHub", "Google"):
            self.assertTrue(self.groups[g].startswith("select"),
                            f"{g} must be select-only: {self.groups[g]}")
            for forbidden in ("url-test", "fallback", "load-balance", "random"):
                self.assertNotIn(forbidden, self.groups[g])

    def test_claude_targets_taiwan(self):
        self.assertIn("TW", self.groups["Claude"])
        self.assertIn("台湾", self.groups["Claude"])

    def test_chatgpt_targets_us_and_sg(self):
        self.assertIn("US", self.groups["ChatGPT"])
        self.assertIn("SG", self.groups["ChatGPT"])

    def test_claude_and_chatgpt_are_separated(self):
        # Core mission: Claude and ChatGPT must NOT share one policy.
        claude_rules = [r for r in self.rules if r.endswith(",Claude")]
        chatgpt_rules = [r for r in self.rules if r.endswith(",ChatGPT")]
        self.assertTrue(claude_rules)
        self.assertTrue(chatgpt_rules)
        self.assertTrue(any("anthropic" in r for r in claude_rules))
        self.assertTrue(any("openai" in r for r in chatgpt_rules))

    def test_apple_appstore_stays_direct(self):
        # The Apple base rule-set must be DIRECT (not proxied).
        self.assertTrue(any("QuantumultX/Apple/Apple.list,DIRECT" in r
                            for r in self.rules))

    def test_final_is_last_and_points_to_group(self):
        self.assertTrue(self.rules[-1].startswith("FINAL,"))
        self.assertEqual(self.rules[-1], "FINAL,Final")

    def test_no_duplicate_rules(self):
        body = [r for r in self.rules if not r.startswith("FINAL")]
        self.assertEqual(len(body), len(set(body)))

    def test_uses_regex_not_hardcoded_nodes(self):
        # No group should reference an explicit airport node name; AI groups use regex.
        for g in ("Claude", "ChatGPT", "GitHub", "Google"):
            self.assertIn("policy-regex-filter=", self.groups[g])

    def test_no_upstream_lazy_ai_bundle(self):
        # The bundled AI.txt must be gone (replaced by per-vendor providers).
        self.assertNotIn("iab0x00/ProxyRules", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
