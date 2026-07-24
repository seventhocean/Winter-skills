#!/usr/bin/env python3
"""winter-publish-check 的最小回归测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import media_engine  # noqa: E402
import scan  # noqa: E402
import text_engine  # noqa: E402


class WinterPublishCheckTests(unittest.TestCase):
    def test_clean_personal_share_has_no_candidates(self):
        result = scan.run(
            "我分享一次自己的工具使用经历，具体效果以每个人的环境为准。",
            "douyin",
            False,
            set(),
            24,
        )
        self.assertEqual(result["text_scan"]["candidates"], [])
        self.assertEqual(result["media_scan"]["hits"], [])

    def test_commercial_claim_and_diversion_are_candidates(self):
        result = scan.run(
            "这个课程保证三十天回本，加我微信进群领取资料。",
            "douyin",
            True,
            set(),
            24,
        )
        self.assertTrue(result["text_scan"]["candidates"])
        self.assertTrue(result["media_scan"]["hits"])

    def test_platform_name_without_action_is_not_automatically_diversion(self):
        result = scan.run(
            "我在比较 Workbuddy、Codex 和 Claude Code 的使用体验。",
            "douyin",
            False,
            set(),
            24,
        )
        self.assertEqual(result["media_scan"]["hits"], [])

    def test_rules_live_in_project_rules_directory(self):
        self.assertEqual(text_engine.TERMS_PATH, ROOT / "rules" / "text-terms.json")
        self.assertEqual(media_engine.DEFAULT_RULES, ROOT / "rules" / "media-patterns.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
