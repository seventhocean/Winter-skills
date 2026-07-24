#!/usr/bin/env python3
"""Winter 发布前审核的统一文本预检入口。

合并中文行业词面扫描与媒体发布策略扫描；输出候选，不直接给出合规结论。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import media_engine
import text_engine


PLATFORMS = ("douyin", "xiaohongshu", "weixin-video-accounts", "kuaishou", "all")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Winter 发布前双引擎文本预检")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="UTF-8 文本文件")
    source.add_argument("--text", help="直接传入文本")
    parser.add_argument("--platform", choices=PLATFORMS, default="douyin")
    parser.add_argument("--commercial", action="store_true", help="内容有商业属性")
    parser.add_argument("--industry", default="", help="逗号分隔：medical,finance")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--context", type=int, default=24)
    return parser.parse_args()


def load_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    try:
        return args.file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"输入必须是 UTF-8 文本：{exc}") from exc
    except OSError as exc:
        raise SystemExit(f"无法读取输入：{exc}") from exc


def run(text: str, platform: str, commercial: bool, industries: set[str], context: int) -> dict:
    text_result = text_engine.scan(text, commercial, industries, max(0, context))
    media_rules = media_engine.load_rules(media_engine.DEFAULT_RULES)
    media_hits = media_engine.scan(text, media_rules, platform, max(0, context))
    media_result = media_engine.result_payload(text, platform, media_hits)
    return {
        "tool": "winter-publish-check",
        "platform": platform,
        "characters": len(text),
        "text_scan": text_result,
        "media_scan": media_result,
        "disclaimer": "词面命中只是复核候选，不是最终违规结论；仍需结合语境、权利、画面、音频、声明和当前平台规则判断。",
    }


def render_markdown(result: dict) -> str:
    text_result = result["text_scan"]
    media_result = result["media_scan"]
    lines = [
        "# Winter 发布前文本预检",
        "",
        f"- 平台：`{result['platform']}`｜扫描字符：{result['characters']}",
        f"- 说明：{result['disclaimer']}",
        "",
        "## 中文规则和个人规则候选",
        "",
        text_engine.render_markdown(text_result),
        "",
        "## 媒体发布策略候选",
        "",
        media_engine.render_markdown(media_result),
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    industries = {item.strip() for item in args.industry.split(",") if item.strip()}
    result = run(load_text(args), args.platform, args.commercial, industries, args.context)
    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
