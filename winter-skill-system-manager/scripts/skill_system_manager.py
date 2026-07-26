#!/usr/bin/env python3
"""Inventory and safely reorganize local Agent Skills.

The command is deliberately plan-driven: inventory/classify/plan are read-only,
apply requires an edited plan plus --confirm, and rollback uses the transaction
manifest written by apply. The implementation uses only the Python standard
library so it can run on a fresh machine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SKILL_FILE = "SKILL.md"
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "node_modules",
    "__pycache__",
    ".cache",
    "build",
    "dist",
    "out",
    "release",
}
PROJECT_MARKERS = (
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "composer.json",
    "remotion.config.ts",
    "remotion.config.js",
    "vite.config.ts",
    "vite.config.js",
)
DEFAULT_SKILL_ROOTS = (
    ".agents/skills",
    ".claude/skills",
    ".codex/skills",
    ".workbuddy/skills",
)
DEFAULT_QUARANTINE_ROOT = "~/.winter-skill-system-manager/quarantine"
BEHAVIORAL_SCRIPT_EXTENSIONS = {
    ".bash",
    ".cjs",
    ".js",
    ".mjs",
    ".php",
    ".pl",
    ".ps1",
    ".py",
    ".rb",
    ".sh",
    ".ts",
    ".zsh",
}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "info": 3}
SEVERITY_LABELS = {
    "critical": "严重风险",
    "high": "高风险",
    "medium": "需要复核",
    "info": "信息提示",
}
THIS_SKILL_ROOT = Path(__file__).resolve().parents[1]


def absolute(path: str | Path) -> Path:
    return Path(path).expanduser().absolute()


def lexists(path: str | Path) -> bool:
    return os.path.lexists(str(path))


def is_under(path: Path, root: Path) -> bool:
    try:
        path.absolute().relative_to(root.absolute())
        return True
    except ValueError:
        return False


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stamp_for_path() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def read_text(path: Path, limit: int = 256_000) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except (OSError, UnicodeError):
        return ""


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = scalar(match.group(2))
    return result


def nearest_repo(path: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def git_remote(repo: Path | None) -> str | None:
    if repo is None:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "remote", "get-url", "origin"],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value or None


def project_markers(path: Path) -> list[str]:
    return [marker for marker in PROJECT_MARKERS if (path / marker).exists()]


def plugin_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    normalized = "/".join(part.lower() for part in path.parts)
    return ".codex" in parts and "plugins" in parts or "/plugins/cache/" in normalized


def hash_directory(path: Path) -> str | None:
    if not path.is_dir():
        return None
    digest = hashlib.sha256()
    try:
        for root, dirs, files in os.walk(path, followlinks=False):
            dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
            for name in sorted(files):
                file_path = Path(root) / name
                relative = file_path.relative_to(path).as_posix()
                digest.update(relative.encode("utf-8", "replace"))
                digest.update(b"\0")
                if file_path.is_symlink():
                    digest.update(os.readlink(file_path).encode("utf-8", "replace"))
                else:
                    with file_path.open("rb") as handle:
                        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                            digest.update(chunk)
                digest.update(b"\0")
    except OSError:
        return None
    return digest.hexdigest()


def is_behavioral_script(path: Path, skill_root: Path) -> bool:
    """Return whether a file is part of the executable behavior surface."""
    if not path.is_file() or path.is_symlink():
        return False
    if os.access(path, os.X_OK):
        return True
    try:
        relative = path.relative_to(skill_root)
    except ValueError:
        return False
    return bool(relative.parts and relative.parts[0] == "scripts" and path.suffix.lower() in BEHAVIORAL_SCRIPT_EXTENSIONS)


def behavioral_files(path: Path) -> list[Path]:
    """Collect SKILL.md and executable script files without executing them."""
    if not path.is_dir() or not (path / SKILL_FILE).is_file():
        return []
    candidates: set[Path] = {path / SKILL_FILE}
    try:
        for root, dirs, files in os.walk(path, followlinks=False):
            dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
            for name in sorted(files):
                file_path = Path(root) / name
                if is_behavioral_script(file_path, path):
                    candidates.add(file_path)
    except OSError:
        return []
    return sorted(candidates, key=lambda file_path: file_path.relative_to(path).as_posix())


def hash_behavior(path: Path) -> str | None:
    files = behavioral_files(path)
    if not files:
        return None
    digest = hashlib.sha256()
    try:
        for file_path in files:
            relative = file_path.relative_to(path).as_posix()
            digest.update(relative.encode("utf-8", "replace"))
            digest.update(b"\0")
            with file_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\0")
    except OSError:
        return None
    return digest.hexdigest()


def source_details(path: Path, kind: str, link_target: str | None = None) -> dict[str, Any]:
    resolved = path.resolve(strict=False) if kind == "symlink" else path
    target_exists = resolved.exists() if kind == "symlink" else path.exists()
    skill_path = resolved / SKILL_FILE if resolved.is_dir() else None
    metadata = frontmatter(skill_path) if skill_path and skill_path.is_file() else {}
    repo = nearest_repo(resolved) if target_exists else None
    markers = project_markers(resolved) if target_exists and resolved.is_dir() else []
    return {
        "resolved_path": str(resolved) if target_exists else None,
        "target_exists": target_exists,
        "skill_file": str(skill_path) if skill_path and skill_path.is_file() else None,
        "metadata": metadata,
        "project_markers": markers,
        "project_with_skill": bool(markers),
        "plugin_path": plugin_path(resolved),
        "repo_root": str(repo) if repo else None,
        "git_remote": git_remote(repo),
        "content_hash": hash_directory(resolved) if target_exists and skill_path and skill_path.is_file() else None,
        "behavioral_fingerprint": hash_behavior(resolved) if target_exists and skill_path and skill_path.is_file() else None,
        "link_target": link_target,
    }


def inspect_path(path: Path, kind: str) -> dict[str, Any]:
    if kind == "symlink":
        return {"path": str(path), "kind": kind, **source_details(path, kind, os.readlink(path))}
    return {"path": str(path), "kind": kind, **source_details(path, kind)}


def scan_root(root: Path, max_depth: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    visited_physical: set[str] = set()

    def visit(directory: Path, depth: int) -> None:
        if not directory.is_dir() or directory.is_symlink():
            return
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError:
            return
        for entry in entries:
            path = Path(entry.path)
            try:
                if entry.is_symlink():
                    records.append(inspect_path(path, "symlink"))
                    continue
                if not entry.is_dir(follow_symlinks=False):
                    continue
            except OSError:
                continue
            if entry.name in SKIP_DIRS:
                continue
            if (path / SKILL_FILE).is_file():
                real = str(path.resolve(strict=False))
                if real not in visited_physical:
                    records.append(inspect_path(path, "skill"))
                    visited_physical.add(real)
            if depth < max_depth and not plugin_path(path):
                visit(path, depth + 1)

    if root.is_symlink():
        records.append(inspect_path(root, "symlink"))
    elif root.is_dir():
        if (root / SKILL_FILE).is_file():
            records.append(inspect_path(root, "skill"))
        visit(root, 0)
    return records


def default_roots(home: Path) -> list[Path]:
    return [home / relative for relative in DEFAULT_SKILL_ROOTS if (home / relative).exists()]


def project_roots(projects: Iterable[str]) -> list[Path]:
    result: list[Path] = []
    for project in projects:
        root = absolute(project)
        if not root.exists():
            continue
        result.append(root)
        result.extend(root / relative for relative in DEFAULT_SKILL_ROOTS if (root / relative).exists())
    return result


def inventory(roots: list[Path], max_depth: int) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for root in roots:
        for record in scan_root(root, max_depth):
            key = (record["kind"], record["path"])
            if key not in seen_keys:
                records.append(record)
                seen_keys.add(key)
    return {
        "schema_version": 1,
        "generated_at": timestamp(),
        "scan_roots": [str(root) for root in roots],
        "records": records,
    }


def canonical_category(path: Path, args: argparse.Namespace) -> tuple[str | None, list[str]]:
    roots = (
        ("personal-public", getattr(args, "personal_public_root", None)),
        ("personal-private", getattr(args, "personal_private_root", None)),
        ("third-party", getattr(args, "third_party_root", None)),
    )
    signals: list[str] = []
    for category, root in roots:
        if root:
            root_path = absolute(root)
            if is_under(path, root_path):
                signals.append(f"under:{category}")
                return category, signals
    lowered = "/".join(part.lower() for part in path.parts)
    if any(token in lowered for token in ("/third-party-skill/", "/third_party_skill/", "/thirdparty/")):
        signals.append("path-name:third-party")
        return "third-party", signals
    return None, signals


def classify_record(record: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    result = dict(record)
    resolved = Path(record["resolved_path"]) if record.get("resolved_path") else None
    signals: list[str] = []
    if record.get("kind") == "symlink":
        if not record.get("target_exists"):
            category = "broken-link"
        elif record.get("plugin_path"):
            category = "plugin"
            signals.append("inside-plugin-cache")
        elif resolved:
            category, source_signals = canonical_category(resolved, args)
            signals.extend(source_signals)
            category = category or "symlink-entrypoint"
        else:
            category = "unknown"
    elif record.get("plugin_path"):
        category = "plugin"
        signals.append("inside-plugin-cache")
    elif record.get("project_with_skill"):
        category = "project-with-skill"
        signals.append("project-marker:" + ",".join(record.get("project_markers", [])))
    elif resolved:
        category, source_signals = canonical_category(resolved, args)
        signals.extend(source_signals)
        if category is None and record.get("git_remote"):
            category = "external-repo-skill"
            signals.append("has-git-remote")
        category = category or "unknown"
    else:
        category = "unknown"
    if record.get("git_remote"):
        signals.append("git:" + record["git_remote"])
    result["category"] = category
    result["signals"] = signals
    result["needs_review"] = category in {
        "broken-link",
        "external-repo-skill",
        "unknown",
        "symlink-entrypoint",
    }
    return result


def classify_data(data: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    records = [classify_record(record, args) for record in data.get("records", [])]
    result = dict(data)
    result["classified_at"] = timestamp()
    result["records"] = records
    result["summary"] = dict(Counter(record["category"] for record in records))
    return result


def write_json(data: dict[str, Any], output: str | None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output:
        target = absolute(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}")
    else:
        print(text, end="")


def load_json(path: str) -> dict[str, Any]:
    return json.loads(absolute(path).read_text(encoding="utf-8"))


def print_summary(data: dict[str, Any], label: str) -> None:
    records = data.get("records", [])
    print(f"{label}: {len(records)} record(s)")
    if data.get("summary"):
        for key, value in sorted(data["summary"].items()):
            print(f"  {key}: {value}")


def audit_targets(data: dict[str, Any]) -> tuple[list[Path], list[str]]:
    targets: dict[str, Path] = {}
    skipped_protected: set[str] = set()
    for record in data.get("records", []):
        resolved_value = record.get("resolved_path")
        if not resolved_value or not record.get("target_exists"):
            continue
        resolved = absolute(resolved_value)
        if is_self_target(resolved):
            skipped_protected.add(f"{resolved} (manager itself)")
            continue
        if record.get("plugin_path"):
            skipped_protected.add(str(resolved))
            continue
        if (resolved / SKILL_FILE).is_file():
            targets[str(resolved)] = resolved
    return sorted(targets.values(), key=str), sorted(skipped_protected)


def defensive_context(line: str) -> bool:
    lowered = line.lower()
    return any(
        marker in lowered
        for marker in (
            "untrusted content",
            "external content",
            "prompt injection",
            "do not follow",
            "don't follow",
            "never follow",
            "treat as data",
            "不可信内容",
            "外部内容",
            "提示词注入",
            "不要执行",
            "禁止执行",
            "不得上传",
        )
    )


def executable_code_segment(file_path: Path, line: str) -> str:
    """Remove ordinary inline comments from executable source before matching behavior."""
    if file_path.name == SKILL_FILE:
        return line
    segment = line
    if segment.lstrip().startswith(("#", "//")):
        return ""
    segment = re.split(r"\s+#", segment, maxsplit=1)[0]
    segment = re.split(r"\s//", segment, maxsplit=1)[0]
    return segment


def audit_line(file_path: Path, line_number: int, line: str, findings: list[dict[str, Any]]) -> None:
    """Apply conservative, line-level static checks; never execute the file."""
    lowered = line.lower()
    code = executable_code_segment(file_path, line)
    is_instruction = file_path.name == SKILL_FILE

    def add(
        severity: str,
        rule: str,
        principle: str,
        message: str,
    ) -> None:
        findings.append(
            {
                "severity": severity,
                "severity_label": SEVERITY_LABELS[severity],
                "rule": rule,
                "principle": principle,
                "message": message,
                "file": str(file_path),
                "line": line_number,
                "excerpt": line.strip()[:300],
            }
        )

    network_call = re.search(
        r"(?:\b(?:curl|wget)\s+|requests?\.(?:get|post|put|patch|request)\s*\(|httpx\.(?:get|post|put|patch|request)\s*\(|urllib\.request\.(?:urlopen|Request)\s*\(|fetch\s*\(|axios\.(?:get|post|put|patch|request)\s*\()",
        code,
        re.IGNORECASE,
    )
    prohibitive = re.search(r"\b(?:do not|don't|never|avoid|without)\b|不(?:读取|访问|发送|上传)|禁止|不得|不要", lowered)
    example_context = re.search(r"\b(?:example|sample|usage|demo)\b|示例|例如", lowered)
    explanatory_context = re.search(r"高风险|建议隔离|风险|未说明授权|明确授权", lowered)

    sensitive_path = re.search(
        r"(~/.ssh|\.ssh/(?:id_|known_hosts|config)|\.aws/credentials|\.netrc|/etc/shadow|keychain|cookies?\.sqlite|浏览器.*cookies?)",
        code,
        re.IGNORECASE,
    )
    secret_name = re.search(
        r"(api[_ -]?key|access[_ -]?token|refresh[_ -]?token|client[_ -]?secret|password|cookie|authorization|bearer|私钥|密钥|令牌|口令)",
        code,
        re.IGNORECASE,
    )

    if sensitive_path and not prohibitive:
        add(
            "high",
            "sensitive-file-access",
            "Skill should only access data necessary for the user-requested task.",
            "读取可能包含凭据或浏览器会话的本地文件，需要确认是否确有必要。",
        )

    if network_call and secret_name and not prohibitive:
        add(
            "critical",
            "possible-secret-exfiltration",
            "Sensitive values must not leave the machine without explicit user authorization.",
            "同一行同时出现敏感信息和外部网络调用，可能存在数据外传。",
        )
    elif secret_name and re.search(r"(?:os\.environ|getenv\s*\(|process\.env|ENV\[)", code, re.IGNORECASE) and not prohibitive and not example_context:
        add(
            "medium",
            "secret-environment-access",
            "Environment secrets should be accessed only when the task explicitly requires them.",
            "读取可能包含密钥、令牌或 Cookie 的环境变量，需要人工确认用途。",
        )

    if network_call and not is_instruction and not prohibitive and not example_context:
        add(
            "medium",
            "external-network-call",
            "External communication should be explicit, scoped, and expected by the user.",
            "可执行文件包含外部网络调用，需确认目标、发送内容和用户授权。",
        )

    if re.search(r"(?:curl|wget)\s+[^\n|]+\|\s*(?:bash|sh|zsh)\b", code, re.IGNORECASE) and not prohibitive and not example_context:
        add(
            "critical",
            "remote-script-execution",
            "Do not execute downloaded code without inspection and explicit authorization.",
            "把远程下载内容直接交给 Shell 执行，属于高危操作。",
        )
    elif re.search(r"\brm\s+-[a-z]*r[a-z]*f\b|\bsudo\s+|\bshell\s*=\s*True|subprocess\.(?:run|Popen|call)\s*\(|os\.system\s*\(|child_process\.(?:exec|spawn)\s*\(|\beval\s*\(", code, re.IGNORECASE) and not prohibitive and not example_context:
        add(
            "high" if re.search(r"\brm\s+-[a-z]*r[a-z]*f\b|\bsudo\s+", code, re.IGNORECASE) else "medium",
            "system-command-execution",
            "System commands require narrow scope and explicit user intent.",
            "包含系统命令或动态执行代码，需要确认命令范围和执行条件。",
        )

    prompt_injection = re.search(
        r"(ignore|disregard|override)\s+(?:all\s+|any\s+|the\s+)?(?:previous|prior|system)\s+instructions|reveal\s+(?:the\s+)?system\s+prompt|follow\s+these\s+instructions\s+instead|忽略(?:之前|上面|系统)指令|泄露系统提示词",
        line,
        re.IGNORECASE,
    )
    if prompt_injection and not defensive_context(line):
        add(
            "high",
            "instruction-hijacking",
            "A Skill must serve the user's task and must not replace higher-priority instructions.",
            "发现可能改变任务目标或索取系统提示词的指令，需要人工复核。",
        )

    covert_promotion = re.search(
        r"(?:always|must|regardless|every response|始终|必须|无论用户|每次).{0,80}(?:promot|advertis|affiliate|buy|purchase|关注|购买|推广|加微信|私信|下单|返佣|引流)|(?:always|must|始终|必须).{0,60}(?:mention|include).{0,40}(?:affiliate|sponsor|buy|purchase|微信|购买)",
        line,
        re.IGNORECASE,
    )
    if covert_promotion and not prohibitive and not explanatory_context and not re.search(r"(?:user requested|disclosure|review|sponsored|用户明确要求|广告披露|评测)", lowered):
        add(
            "medium",
            "covert-commercial-directive",
            "Commercial intent must be relevant to the task and transparent to the user.",
            "发现可能与用户任务无关的强制推广或引流指令，需要人工复核。",
        )


def audit_data(data: dict[str, Any]) -> dict[str, Any]:
    targets, skipped_protected = audit_targets(data)
    findings: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for target in targets:
        for file_path in behavioral_files(target):
            scanned_files.append(str(file_path))
            text = read_text(file_path, limit=512_000)
            for line_number, line in enumerate(text.splitlines(), start=1):
                audit_line(file_path, line_number, line, findings)

    unique_findings: dict[tuple[str, str, int], dict[str, Any]] = {}
    for finding in findings:
        key = (finding["rule"], finding["file"], finding["line"])
        unique_findings[key] = finding
    findings = sorted(
        unique_findings.values(),
        key=lambda finding: (SEVERITY_ORDER[finding["severity"]], finding["file"], finding["line"]),
    )
    summary = Counter(finding["severity"] for finding in findings)
    return {
        "schema_version": 1,
        "audited_at": timestamp(),
        "target_count": len(targets),
        "targets": [str(target) for target in targets],
        "scanned_files": sorted(scanned_files),
        "skipped_protected": skipped_protected,
        "findings": findings,
        "summary": dict(summary),
        "ok": not any(finding["severity"] in {"critical", "high"} for finding in findings),
        "method": "static read-only scan of SKILL.md and executable script files; no code execution or network access",
    }


def command_audit(args: argparse.Namespace) -> int:
    if args.input:
        data = load_json(args.input)
    else:
        roots = [absolute(root) for root in args.scan_root] if args.scan_root else default_roots(absolute(args.home))
        roots.extend(project_roots(args.project_root))
        data = inventory(list(dict.fromkeys(root for root in roots if root.exists())), args.max_depth)
    result = audit_data(data)
    print(
        f"audit: {'PASS' if result['ok'] else 'REVIEW REQUIRED'}; "
        f"targets={result['target_count']}; findings={len(result['findings'])}"
    )
    for severity in ("critical", "high", "medium", "info"):
        if result["summary"].get(severity):
            print(f"  {SEVERITY_LABELS[severity]}: {result['summary'][severity]}")
    write_json(result, args.output)
    return 0 if result["ok"] else 1


def command_inventory(args: argparse.Namespace) -> int:
    roots = [absolute(root) for root in args.scan_root] if args.scan_root else default_roots(absolute(args.home))
    roots.extend(project_roots(args.project_root))
    roots = list(dict.fromkeys(root for root in roots if root.exists()))
    data = inventory(roots, args.max_depth)
    print_summary(data, "inventory")
    write_json(data, args.output)
    return 0


def command_classify(args: argparse.Namespace) -> int:
    data = load_json(args.input)
    result = classify_data(data, args)
    print_summary(result, "classify")
    write_json(result, args.output)
    return 0


def make_plan(data: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    operations: list[dict[str, Any]] = []
    for record in data.get("records", []):
        category = record.get("category", "unknown")
        path = record.get("path")
        if category == "broken-link":
            action = "review"
            reason = "broken link; locate the intended source before changing it"
        elif category in {"plugin", "project-with-skill"}:
            action = "keep"
            reason = "protected ecosystem or complete project; do not auto-migrate"
        elif category in {"personal-public", "personal-private", "third-party"}:
            action = "keep"
            reason = "already under a configured canonical root"
        elif record.get("kind") == "symlink" and record.get("target_exists"):
            action = "review"
            reason = "working entrypoint; confirm whether it should point directly to a canonical source"
        else:
            action = "review"
            reason = "source and ownership need user confirmation"
        operations.append(
            {
                "id": len(operations) + 1,
                "action": action,
                "approved": False,
                "path": path,
                "target": record.get("resolved_path"),
                "category": category,
                "reason": reason,
            }
        )
    return {
        "schema_version": 1,
        "generated_at": timestamp(),
        "source_inventory": data.get("generated_at"),
        "safety": {
            "default_mode": "dry-run",
            "requires_approval": True,
            "backup_before_change": True,
            "deletion_is_never_automatic": True,
        },
        "operations": operations,
        "instructions": "Edit operations, set approved=true, then run apply --confirm. Review every move/link/remove operation.",
    }


def command_plan(args: argparse.Namespace) -> int:
    data = load_json(args.input)
    result = make_plan(data, args)
    print(f"plan: {len(result['operations'])} operation(s); all require review")
    write_json(result, args.output)
    return 0


def backup_existing(path: Path, backup_root: Path, index: int) -> Path | None:
    if not lexists(path):
        return None
    backup_root.mkdir(parents=True, exist_ok=True)
    destination = backup_root / f"{index:03d}-{path.name}"
    if lexists(destination):
        destination = backup_root / f"{index:03d}-{index}-{path.name}"
    shutil.move(str(path), str(destination))
    return destination


def validate_operation(operation: dict[str, Any]) -> str | None:
    action = operation.get("action")
    if action not in {"move", "link", "remove", "keep", "review"}:
        return f"unsupported action: {action!r}"
    if action in {"move", "remove"} and not operation.get("path"):
        return "path is required"
    if action in {"move", "link"} and not operation.get("destination"):
        return "destination is required"
    if action == "link" and not operation.get("target"):
        return "target is required"
    return None


def command_apply(args: argparse.Namespace) -> int:
    plan_path = absolute(args.plan)
    plan = load_json(str(plan_path))
    operations = plan.get("operations", [])
    approved = [op for op in operations if op.get("approved") is True and op.get("action") not in {"keep", "review"}]
    if not args.confirm:
        print(f"dry-run: {len(approved)} approved operation(s) found; pass --confirm to apply", file=sys.stderr)
        return 2 if approved else 0
    backup_root = absolute(args.backup_dir) if args.backup_dir else plan_path.parent / f".winter-skill-backup-{stamp_for_path()}"
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "created_at": timestamp(),
        "plan": str(plan_path),
        "backup_root": str(backup_root),
        "operations": [],
    }
    errors: list[str] = []
    for index, operation in enumerate(approved, start=1):
        error = validate_operation(operation)
        if error:
            errors.append(f"operation {operation.get('id')}: {error}")
            continue
        action = operation["action"]
        source = absolute(operation["path"]) if operation.get("path") else None
        destination = absolute(operation["destination"]) if operation.get("destination") else None
        try:
            if action == "move":
                if source is None or not lexists(source):
                    raise RuntimeError(f"source does not exist: {source}")
                destination_backup = backup_existing(destination, backup_root, index) if destination else None
                assert destination is not None
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                manifest["operations"].append({"action": action, "source": str(source), "destination": str(destination), "destination_backup": str(destination_backup) if destination_backup else None})
            elif action == "link":
                target = absolute(operation["target"])
                if not target.exists():
                    raise RuntimeError(f"link target does not exist: {target}")
                assert destination is not None
                destination_backup = backup_existing(destination, backup_root, index)
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.symlink(str(target), str(destination), target_is_directory=target.is_dir())
                manifest["operations"].append({"action": action, "target": str(target), "destination": str(destination), "destination_backup": str(destination_backup) if destination_backup else None})
            elif action == "remove":
                if not args.allow_delete:
                    raise RuntimeError("remove requires --allow-delete; it is backed up, not permanently deleted")
                assert source is not None
                removed_to = backup_existing(source, backup_root, index)
                if removed_to is None:
                    raise RuntimeError(f"source does not exist: {source}")
                manifest["operations"].append({"action": action, "source": str(source), "removed_to": str(removed_to)})
        except (OSError, RuntimeError) as exc:
            errors.append(f"operation {operation.get('id')}: {exc}")
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest_path = backup_root / "transaction.json"
    write_json(manifest, str(manifest_path))
    print(f"applied: {len(manifest['operations'])}; backup: {backup_root}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


def quarantine_root_from_args(args: argparse.Namespace) -> Path:
    return absolute(args.quarantine_root) if args.quarantine_root else absolute(DEFAULT_QUARANTINE_ROOT)


def is_protected_runtime_path(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return plugin_path(path) or ".workbuddy" in lowered


def is_self_target(path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(THIS_SKILL_ROOT)
        return True
    except ValueError:
        return False


def valid_quarantine_target(path: Path) -> tuple[bool, str]:
    if not lexists(path):
        return False, f"source does not exist: {path}"
    if path.is_symlink():
        target = path.resolve(strict=False)
        if not target.exists() or not target.is_dir() or not (target / SKILL_FILE).is_file():
            return False, "symlink must point to an existing directory containing SKILL.md"
        return True, "symlink"
    if path.is_dir() and (path / SKILL_FILE).is_file():
        return True, "directory"
    return False, "quarantine target must be a Skill directory or a symlink to one"


def quarantine_manifest_paths(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    manifests: list[Path] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
        if "transaction.json" in files:
            manifests.append(Path(current) / "transaction.json")
    return sorted(manifests, key=str)


def command_quarantine_list(args: argparse.Namespace) -> int:
    root = quarantine_root_from_args(args)
    entries: list[dict[str, Any]] = []
    for manifest_path in quarantine_manifest_paths(root):
        try:
            manifest = load_json(str(manifest_path))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        manifest["manifest"] = str(manifest_path)
        entries.append(manifest)
    result = {
        "schema_version": 1,
        "quarantine_root": str(root),
        "entries": entries,
        "count": len(entries),
    }
    print(f"quarantine: {len(entries)} manifest(s); root={root}")
    for manifest in entries:
        status = manifest.get("status", "quarantined")
        for entry in manifest.get("entries", []):
            print(f"  {status}: {entry.get('original_path')} -> {entry.get('quarantined_path')}")
    write_json(result, args.output)
    return 0


def command_quarantine_move(args: argparse.Namespace) -> int:
    source = absolute(args.path)
    root = quarantine_root_from_args(args)
    if is_self_target(source):
        print("error: refusing to quarantine Winter Skill System Manager itself", file=sys.stderr)
        return 1
    if is_protected_runtime_path(source):
        print("error: refusing to modify a protected plugin or WorkBuddy path", file=sys.stderr)
        return 1
    valid, kind_or_error = valid_quarantine_target(source)
    if not valid:
        print(f"error: {kind_or_error}", file=sys.stderr)
        return 1
    if is_under(root, source) or is_under(source, root):
        print("error: quarantine root and source must not contain one another", file=sys.stderr)
        return 1
    batch_root = root / stamp_for_path()
    destination = batch_root / source.name
    suffix = 2
    while lexists(destination):
        destination = batch_root / f"{source.name}-{suffix}"
        suffix += 1
    preview = {
        "action": "quarantine",
        "source": str(source),
        "destination": str(destination),
        "kind": kind_or_error,
        "quarantine_root": str(root),
    }
    if not args.confirm:
        print("dry-run: would quarantine one explicitly selected Skill; pass --confirm to move it")
        write_json(preview, args.output)
        return 2
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        manifest = {
            "schema_version": 1,
            "action": "quarantine",
            "created_at": timestamp(),
            "status": "quarantined",
            "quarantine_root": str(root),
            "entries": [
                {
                    "original_path": str(source),
                    "quarantined_path": str(destination),
                    "kind": kind_or_error,
                }
            ],
        }
        manifest_path = batch_root / "transaction.json"
        write_json(manifest, str(manifest_path))
        print(f"quarantined: {source} -> {destination}")
        print(f"manifest: {manifest_path}")
        return 0
    except OSError as exc:
        if lexists(destination) and not lexists(source):
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
        print(f"error: quarantine failed: {exc}", file=sys.stderr)
        return 1


def command_quarantine_restore(args: argparse.Namespace) -> int:
    manifest_path = absolute(args.manifest)
    try:
        manifest = load_json(str(manifest_path))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: cannot read quarantine manifest: {exc}", file=sys.stderr)
        return 1
    if manifest.get("action") != "quarantine":
        print("error: manifest is not a quarantine transaction", file=sys.stderr)
        return 1
    entries = manifest.get("entries", [])
    if not isinstance(entries, list) or not entries:
        print("error: quarantine manifest has no entries", file=sys.stderr)
        return 1
    conflicts: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("original_path") or not entry.get("quarantined_path"):
            conflicts.append("quarantine manifest contains an invalid entry")
            continue
        original = absolute(entry["original_path"])
        quarantined = absolute(entry["quarantined_path"])
        if is_self_target(original):
            conflicts.append(f"refusing to restore over Winter Skill System Manager: {original}")
        if is_protected_runtime_path(original):
            conflicts.append(f"refusing to restore into a protected plugin or WorkBuddy path: {original}")
        if lexists(original):
            conflicts.append(f"original destination already exists: {original}")
        if not lexists(quarantined):
            conflicts.append(f"quarantined source is missing: {quarantined}")
    if conflicts:
        for conflict in conflicts:
            print(f"error: {conflict}", file=sys.stderr)
        return 1
    if not args.confirm:
        print(f"dry-run: would restore {len(entries)} quarantined entr{'y' if len(entries) == 1 else 'ies'}; pass --confirm to restore")
        return 0
    try:
        for entry in entries:
            original = absolute(entry["original_path"])
            quarantined = absolute(entry["quarantined_path"])
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(quarantined), str(original))
        manifest["status"] = "restored"
        manifest["restored_at"] = timestamp()
        write_json(manifest, str(manifest_path))
        print(f"restored: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
        return 0
    except OSError as exc:
        print(f"error: restore failed: {exc}; inspect the manifest before retrying", file=sys.stderr)
        return 1


def command_quarantine(args: argparse.Namespace) -> int:
    return args.quarantine_function(args)


def host_for_path(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if plugin_path(path):
        return "codex-plugin"
    for name in ("claude", "agents", "codex", "workbuddy"):
        if f".{name}" in parts:
            return name
    return "project-or-other"


def status_entry(record: dict[str, Any]) -> dict[str, Any]:
    path = absolute(record["path"])
    raw_target = record.get("link_target") or ""
    raw_path = Path(raw_target)
    lexical_target = raw_path if raw_path.is_absolute() else path.parent / raw_path
    indirect = lexical_target.is_symlink()
    target_exists = bool(record.get("target_exists"))
    target_has_skill = bool(record.get("skill_file"))
    host = host_for_path(path)
    protected = host in {"codex-plugin", "workbuddy"}
    if not target_exists:
        health = "broken"
    elif not target_has_skill:
        health = "missing-skill-file"
    elif protected:
        health = "protected"
    elif indirect:
        health = "indirect-link"
    elif not raw_path.is_absolute():
        health = "relative-link"
    else:
        health = "direct-link"
    return {
        "path": str(path),
        "host": host,
        "protected": protected,
        "health": health,
        "link_target": raw_target,
        "link_style": "absolute" if raw_path.is_absolute() else "relative",
        "resolved_path": record.get("resolved_path"),
        "target_exists": target_exists,
        "target_skill_file": record.get("skill_file"),
        "target_repo_root": record.get("repo_root"),
        "target_git_remote": record.get("git_remote"),
    }


def status_data(data: dict[str, Any], include_sources: bool = False) -> dict[str, Any]:
    entrypoints = [status_entry(record) for record in data.get("records", []) if record.get("kind") == "symlink"]
    sources = [
        {
            "path": record.get("path"),
            "repo_root": record.get("repo_root"),
            "git_remote": record.get("git_remote"),
            "content_hash": record.get("content_hash"),
            "behavioral_fingerprint": record.get("behavioral_fingerprint"),
        }
        for record in data.get("records", [])
        if record.get("kind") == "skill"
    ]
    summary = dict(Counter(entry["health"] for entry in entrypoints))
    result = {
        "schema_version": 1,
        "generated_at": timestamp(),
        "scan_roots": data.get("scan_roots", []),
        "entrypoints": entrypoints,
        "summary": summary,
        "entrypoint_count": len(entrypoints),
    }
    if include_sources:
        result["sources"] = sources
        result["source_count"] = len(sources)
    return result


def command_status(args: argparse.Namespace) -> int:
    if args.input:
        data = load_json(args.input)
    else:
        roots = [absolute(root) for root in args.scan_root] if args.scan_root else default_roots(absolute(args.home))
        roots.extend(project_roots(args.project_root))
        data = inventory(list(dict.fromkeys(root for root in roots if root.exists())), args.max_depth)
    result = status_data(data, include_sources=args.include_sources)
    print(f"status: entrypoints={result['entrypoint_count']}")
    for key, value in sorted(result["summary"].items()):
        print(f"  {key}: {value}")
    for entry in result["entrypoints"]:
        target = entry.get("resolved_path") or "<missing>"
        print(f"  [{entry['host']}] {entry['health']}: {entry['path']} -> {target}")
    write_json(result, args.output)
    unhealthy = result["summary"].get("broken", 0) + result["summary"].get("missing-skill-file", 0)
    return 0 if not unhealthy else 1


def command_rollback(args: argparse.Namespace) -> int:
    manifest_path = absolute(args.manifest)
    manifest = load_json(str(manifest_path))
    operations = manifest.get("operations", [])
    if not args.confirm:
        print(f"dry-run: would rollback {len(operations)} operation(s); pass --confirm to rollback")
        return 0
    errors: list[str] = []
    for operation in reversed(operations):
        try:
            action = operation["action"]
            if action == "move":
                source = absolute(operation["source"])
                destination = absolute(operation["destination"])
                if lexists(destination) and not lexists(source):
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
                backup = operation.get("destination_backup")
                if backup and lexists(backup) and not lexists(destination):
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(backup), str(destination))
            elif action == "link":
                destination = absolute(operation["destination"])
                if destination.is_symlink() or lexists(destination):
                    if destination.is_symlink() or destination.is_file():
                        destination.unlink()
                    else:
                        raise RuntimeError(f"refusing to remove non-empty rollback destination: {destination}")
                backup = operation.get("destination_backup")
                if backup and lexists(backup):
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(backup), str(destination))
            elif action == "remove":
                source = absolute(operation["source"])
                removed_to = absolute(operation["removed_to"])
                if lexists(removed_to) and not lexists(source):
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(removed_to), str(source))
        except (OSError, RuntimeError) as exc:
            errors.append(f"{operation.get('action')}: {exc}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"rolled back: {len(operations)} operation(s)")
    return 0


def verify_data(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    hashes: defaultdict[str, list[str]] = defaultdict(list)
    behavioral_hashes: defaultdict[str, list[str]] = defaultdict(list)
    for record in data.get("records", []):
        path = record.get("path")
        if record.get("kind") == "symlink" and not record.get("target_exists"):
            errors.append(f"broken link: {path}")
        if record.get("kind") == "skill" and not record.get("skill_file"):
            errors.append(f"missing SKILL.md: {path}")
        content_hash = record.get("content_hash")
        if content_hash and record.get("kind") == "skill":
            hashes[content_hash].append(path)
        behavioral_fingerprint = record.get("behavioral_fingerprint")
        if behavioral_fingerprint and record.get("kind") == "skill":
            behavioral_hashes[behavioral_fingerprint].append(path)
    duplicates = {key: values for key, values in hashes.items() if len(values) > 1}
    for values in duplicates.values():
        warnings.append("duplicate content: " + " | ".join(values))
    behavioral_duplicates = {key: values for key, values in behavioral_hashes.items() if len(values) > 1}
    for values in behavioral_duplicates.values():
        warnings.append("duplicate behavior: " + " | ".join(values))
    return {
        "schema_version": 1,
        "verified_at": timestamp(),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "duplicate_groups": duplicates,
        "behavioral_duplicate_groups": behavioral_duplicates,
        "record_count": len(data.get("records", [])),
    }


def command_verify(args: argparse.Namespace) -> int:
    if args.input:
        data = load_json(args.input)
    else:
        roots = [absolute(root) for root in args.scan_root] if args.scan_root else default_roots(absolute(args.home))
        roots.extend(project_roots(args.project_root))
        data = inventory(list(dict.fromkeys(root for root in roots if root.exists())), args.max_depth)
    result = verify_data(data)
    print(f"verify: {'PASS' if result['ok'] else 'FAIL'}; records={result['record_count']}; warnings={len(result['warnings'])}")
    write_json(result, args.output)
    return 0 if result["ok"] else 1


def add_scan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scan-root", action="append", default=[], help="Directory to scan; repeatable")
    parser.add_argument("--project-root", action="append", default=[], help="Project root; also checks its standard hidden Skill directories")
    parser.add_argument("--home", default=str(Path.home()), help="Home directory used by auto-discovery")
    parser.add_argument("--max-depth", type=int, default=6, help="Maximum recursive depth per scan root")


def add_classify_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--personal-public-root", help="Canonical root for public personal Skills")
    parser.add_argument("--personal-private-root", help="Canonical root for private personal Skills")
    parser.add_argument("--third-party-root", help="Canonical root for third-party Skills")


def add_report_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", help="Inventory JSON; if omitted, scan")
    parser.add_argument("--output", help="Write JSON report to this path")
    add_scan_arguments(parser)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inventory and safely organize local Agent Skills")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory_parser = subparsers.add_parser("inventory", help="Read-only scan of Skill roots")
    add_scan_arguments(inventory_parser)
    inventory_parser.add_argument("--output", help="Write JSON report to this path")
    inventory_parser.set_defaults(function=command_inventory)

    classify_parser = subparsers.add_parser("classify", help="Classify an inventory JSON report")
    classify_parser.add_argument("--input", required=True)
    classify_parser.add_argument("--output", help="Write JSON report to this path")
    add_classify_arguments(classify_parser)
    classify_parser.set_defaults(function=command_classify)

    audit_parser = subparsers.add_parser("audit", help="Read-only static security audit of Skill instructions and scripts")
    add_report_arguments(audit_parser)
    audit_parser.set_defaults(function=command_audit)

    plan_parser = subparsers.add_parser("plan", help="Generate a reviewable, non-mutating plan")
    plan_parser.add_argument("--input", required=True, help="Classified inventory JSON")
    plan_parser.add_argument("--output", required=True, help="Plan JSON path")
    plan_parser.set_defaults(function=command_plan)

    apply_parser = subparsers.add_parser("apply", help="Apply only approved operations from a plan")
    apply_parser.add_argument("--plan", required=True)
    apply_parser.add_argument("--confirm", action="store_true", help="Confirm that approved operations may modify files")
    apply_parser.add_argument("--allow-delete", action="store_true", help="Allow approved remove operations; they are moved to backup, never erased")
    apply_parser.add_argument("--backup-dir", help="Backup directory; defaults next to the plan")
    apply_parser.set_defaults(function=command_apply)

    rollback_parser = subparsers.add_parser("rollback", help="Restore a transaction from apply")
    rollback_parser.add_argument("--manifest", required=True, help="transaction.json written by apply")
    rollback_parser.add_argument("--confirm", action="store_true", help="Confirm rollback")
    rollback_parser.set_defaults(function=command_rollback)

    status_parser = subparsers.add_parser("status", help="Inspect Skill symlink entrypoints and their targets")
    add_report_arguments(status_parser)
    status_parser.add_argument("--include-sources", action="store_true", help="Include physical Skill source records")
    status_parser.set_defaults(function=command_status)

    quarantine_parser = subparsers.add_parser("quarantine", help="Move one explicitly selected Skill to recoverable isolation")
    quarantine_subparsers = quarantine_parser.add_subparsers(dest="quarantine_command", required=True)

    quarantine_list_parser = quarantine_subparsers.add_parser("list", help="List quarantine manifests")
    quarantine_list_parser.add_argument("--quarantine-root", help="Quarantine root; defaults to ~/.winter-skill-system-manager/quarantine")
    quarantine_list_parser.add_argument("--output", help="Write JSON report to this path")
    quarantine_list_parser.set_defaults(function=command_quarantine_list, quarantine_function=command_quarantine_list)

    quarantine_move_parser = quarantine_subparsers.add_parser("move", help="Quarantine one Skill; never a blanket operation")
    quarantine_move_parser.add_argument("--path", required=True, help="One Skill directory or symlink to quarantine")
    quarantine_move_parser.add_argument("--quarantine-root", help="Quarantine root; defaults to ~/.winter-skill-system-manager/quarantine")
    quarantine_move_parser.add_argument("--confirm", action="store_true", help="Confirm the explicitly selected move")
    quarantine_move_parser.add_argument("--output", help="Write JSON preview when running without confirmation")
    quarantine_move_parser.set_defaults(function=command_quarantine_move, quarantine_function=command_quarantine_move)

    quarantine_restore_parser = quarantine_subparsers.add_parser("restore", help="Restore a quarantine transaction")
    quarantine_restore_parser.add_argument("--manifest", required=True, help="transaction.json written by quarantine move")
    quarantine_restore_parser.add_argument("--confirm", action="store_true", help="Confirm restoration")
    quarantine_restore_parser.set_defaults(function=command_quarantine_restore, quarantine_function=command_quarantine_restore)

    verify_parser = subparsers.add_parser("verify", help="Check links, Skill files, and duplicate content")
    verify_parser.add_argument("--input", help="Inventory or classified JSON; if omitted, scan")
    verify_parser.add_argument("--output", help="Write JSON verification result")
    add_scan_arguments(verify_parser)
    verify_parser.set_defaults(function=command_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.function(args)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
