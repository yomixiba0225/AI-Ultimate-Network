#!/usr/bin/env python3
"""
test_config.py — acceptance tests across all client targets.

Run:  python3 -m unittest discover -s tests
Pure stdlib (yaml optional). Verifies the AI-first strategy is identical on
Shadowrocket, Clash Meta/Verge and Surge (generated from one source of truth).
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import strategy as S  # noqa: E402

SR = ROOT / "config" / "AI-Ultimate.conf"
CLASH = ROOT / "config" / "AI-Ultimate.clash.yaml"
SURGE = ROOT / "config" / "AI-Ultimate.surge.conf"
BUILD = ROOT / "scripts" / "build.py"
VALIDATE = ROOT / "scripts" / "validate.py"
AI = set(S.REGION_SELECT_GROUPS)  # region-filtered select groups (incl. TikTok)


def ini_section(text, name):
    out, cur = [], None
    for ln in text.splitlines():
        m = re.match(r"^\[(.+?)\]\s*$", ln.strip())
        if m:
            cur = m.group(1)
            continue
        if cur == name:
            out.append(ln)
    return out


def ini_groups(text):
    g = {}
    for ln in ini_section(text, "Proxy Group"):
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            name, _, rhs = s.partition("=")
            g[name.strip()] = rhs.strip()
    return g


def ini_rules(text):
    return [ln.strip() for ln in ini_section(text, "Rule")
            if ln.strip() and not ln.strip().startswith("#")]


class TestPipeline(unittest.TestCase):
    def test_build_all_fresh(self):
        r = subprocess.run([sys.executable, str(BUILD), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_validate_all_pass(self):
        r = subprocess.run([sys.executable, str(VALIDATE)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestShadowrocket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t = SR.read_text(encoding="utf-8")
        cls.groups, cls.rules = ini_groups(t), ini_rules(t)

    def test_le_10_groups(self):
        self.assertLessEqual(len(self.groups), 10)

    def test_ai_groups_select_only(self):
        for g in AI:
            self.assertTrue(self.groups[g].startswith("select"))
            for f in ("url-test", "fallback", "load-balance", "random"):
                self.assertNotIn(f, self.groups[g])

    def test_final_last(self):
        self.assertEqual(self.rules[-1], "FINAL,Final")

    def test_claude_chatgpt_separate(self):
        self.assertTrue(any(r.endswith(",Claude") and "anthropic" in r for r in self.rules))
        self.assertTrue(any(r.endswith(",ChatGPT") and "openai" in r for r in self.rules))


class TestClash(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CLASH.read_text(encoding="utf-8")

    def test_exists_and_generated(self):
        self.assertIn("proxy-groups:", self.text)
        self.assertIn("proxy-providers:", self.text)

    def test_match_is_last_rule(self):
        rules = re.findall(r"^\s*-\s+((?:DOMAIN|GEOSITE|GEOIP|MATCH)[^\n]*)", self.text, re.M)
        self.assertEqual(rules[-1].strip(), "MATCH,Final")

    def test_ai_groups_select_with_filter(self):
        for g in AI:
            block = re.search(rf"name:\s*{g}\b.*?(?=\n\s*-\s|\Z)", self.text, re.S).group(0)
            self.assertIn("type: select", block)
            self.assertIn("filter:", block)
            self.assertNotIn("url-test", block)

    def test_regex_backslash_b_preserved(self):
        # single-quoted YAML keeps \b literal (double quotes would corrupt to backspace)
        self.assertIn(r"filter: '(?i)(\bTW\b|Taiwan|台湾|台灣)'", self.text)


class TestSurge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t = SURGE.read_text(encoding="utf-8")
        cls.groups, cls.rules = ini_groups(t), ini_rules(t)

    def test_final_last(self):
        self.assertEqual(self.rules[-1], "FINAL,Final")

    def test_ai_groups_select_with_regex(self):
        for g in AI:
            self.assertTrue(self.groups[g].startswith("select"))
            self.assertIn("policy-regex-filter=", self.groups[g])
            for f in ("url-test", "fallback", "load-balance"):
                self.assertNotIn(f, self.groups[g])

    def test_claude_chatgpt_separate(self):
        self.assertTrue(any(r.endswith(",Claude") for r in self.rules))
        self.assertTrue(any(r.endswith(",ChatGPT") for r in self.rules))


class TestClashMergeOverlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "config" / "AI-Ultimate.clash-merge.yaml").read_text(encoding="utf-8")

    def test_is_prepend_overlay(self):
        self.assertIn("prepend-proxy-groups:", self.text)
        self.assertIn("prepend-rules:", self.text)

    def test_no_catch_all(self):
        # overlay must NOT own the final rule (the base subscription profile does)
        self.assertNotIn("MATCH,", self.text)
        self.assertNotIn("FINAL,", self.text)

    def test_groups_use_include_all(self):
        # works across ALL subscriptions without per-sub URLs
        for g in ("Claude", "ChatGPT", "GitHub", "Google"):
            block = re.search(rf"name: {g}\b[^}}]*", self.text).group(0)
            self.assertIn("include-all: true", block)
            self.assertIn("filter:", block)


class TestCrossClientConsistency(unittest.TestCase):
    """The AI region strategy must be identical across all three clients."""

    def _region_filter(self, code_group):
        return S.region_filter(code_group)

    def test_ai_region_filters_match_strategy(self):
        sr = ini_groups(SR.read_text(encoding="utf-8"))
        surge = ini_groups(SURGE.read_text(encoding="utf-8"))
        clash = CLASH.read_text(encoding="utf-8")
        # Derive expected filters straight from strategy so the test auto-covers
        # every region group (Claude/ChatGPT/GitHub/Google/TikTok) and any changes.
        for g in S.GROUPS:
            if g["kind"] == "select" and isinstance(g.get("regions"), list):
                regex = S.region_filter(g["regions"])
                name = g["name"]
                self.assertIn(regex, sr[name], f"SR {name}")
                self.assertIn(regex, surge[name], f"Surge {name}")
                self.assertIn(regex, clash, f"Clash {name}")

    def test_same_group_set_everywhere(self):
        want = {g["name"] for g in S.GROUPS}
        sr = set(ini_groups(SR.read_text(encoding="utf-8")))
        surge = set(ini_groups(SURGE.read_text(encoding="utf-8")))
        self.assertEqual(sr, want)
        self.assertEqual(surge, want)


if __name__ == "__main__":
    unittest.main(verbosity=2)
