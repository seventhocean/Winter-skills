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
    for record in data.get("records", []):
        path = record.get("path")
        if record.get("kind") == "symlink" and not record.get("target_exists"):
            errors.append(f"broken link: {path}")
        if record.get("kind") == "skill" and not record.get("skill_file"):
            errors.append(f"missing SKILL.md: {path}")
        content_hash = record.get("content_hash")
        if content_hash and record.get("kind") == "skill":
            hashes[content_hash].append(path)
    duplicates = {key: values for key, values in hashes.items() if len(values) > 1}
    for values in duplicates.values():
        warnings.append("duplicate content: " + " | ".join(values))
    return {
        "schema_version": 1,
        "verified_at": timestamp(),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "duplicate_groups": duplicates,
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
