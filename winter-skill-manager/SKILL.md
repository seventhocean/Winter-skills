---
name: winter-skill-manager
description: Scan, classify, plan, and safely reorganize local Agent Skills, symlinks, plugin entries, and project-level Skill references without breaking existing usage. Use when a user wants to audit scattered Skills, distinguish personal and third-party sources, remove duplicate copies, create a canonical Skill layout, repair links, migrate entries, verify runtime health, or roll back a previous migration.
---

# Winter Skill Manager

Use this Skill to turn a scattered local Skill installation into a maintainable system. Treat the user's machine as unknown: discover paths instead of assuming a vendor layout, distinguish complete projects from Skills, and keep software-managed plugin ecosystems outside the migration scope.

The Skill is branded for Winter but is intentionally portable. Never embed Winter's paths, repository URLs, vault names, API keys, or private configuration in generated reports or migration logic.

## Non-negotiable safety rules

- Run `inventory` before making a recommendation.
- Run `classify` and `plan` as read-only operations. Treat uncertain ownership as `review`, never as personal or third-party fact.
- Never modify files during `inventory`, `classify`, or `plan`.
- Apply only operations with `approved: true`, and require `apply --confirm`.
- Back up existing destinations before moving, replacing, or removing anything. The script moves approved removals into a backup directory; it never permanently deletes them.
- Do not modify Codex plugin caches, WorkBuddy internal data, package dependencies, virtual environments, build outputs, or user media.
- Do not overwrite a non-empty directory during rollback.
- Verify broken links and source availability after every migration.
- If the user has not confirmed a proposed destructive change, stop after producing the plan.

## Workflow

### 1. Inventory

Use the bundled scanner. It defaults to common user-level roots that exist, or accept explicit `--scan-root` and `--project-root` arguments. Prefer explicit roots when the user has already identified a project.

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  inventory \
  --scan-root "/path/to/.claude/skills" \
  --scan-root "/path/to/.agents/skills" \
  --project-root "/path/to/project" \
  --output /tmp/skill-inventory.json
```

The inventory records physical Skill directories, symlink entrypoints, broken targets, frontmatter, project markers, Git remotes, plugin paths, and content hashes. It skips common runtime directories such as `.git`, `node_modules`, `.venv`, `build`, and `out`.

### 2. Classify

Pass the inventory to `classify`. Supply canonical roots when the user has chosen them:

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  classify \
  --input /tmp/skill-inventory.json \
  --personal-public-root "/path/to/public-skills" \
  --personal-private-root "/path/to/private-skills" \
  --third-party-root "/path/to/third-party-skills" \
  --output /tmp/skill-classified.json
```

Use `references/classification.md` for the decision rules. A Git remote proves that a source is versioned, not that it belongs to the user. Use `external-repo-skill`, `unknown`, and `needs_review` when evidence is insufficient.

### 3. Plan

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  plan --input /tmp/skill-classified.json --output /tmp/skill-plan.json
```

Explain the plan to the user before applying it. The generated plan intentionally leaves every mutating operation unapproved. Review the proposed source, destination, category, and reason; edit the JSON only after the user confirms the intended mapping. See `references/plan-schema.md`.

### 4. Apply

Only use `apply` after the user has approved the edited plan:

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  apply --plan /tmp/skill-plan.json --confirm
```

For approved `move` or `link` operations, the script creates parent directories and backs up existing destinations. `remove` additionally requires `--allow-delete`, and still moves the source into the backup directory rather than deleting it. Report the backup path and transaction manifest.

### 5. Verify

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  verify --input /tmp/skill-classified.json --output /tmp/skill-verify.json
```

Verification fails on broken symlinks or missing `SKILL.md` records and reports duplicate content as warnings. If the local state changed after inventory, rescan before verifying.

### 6. Audit Skill behavior

Run the static audit against an inventory or explicit roots. It reads `SKILL.md` and executable script files only; it never executes scanned code or makes network requests:

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  audit --input /tmp/skill-inventory.json --output /tmp/skill-audit.json
```

Review exact file, line, excerpt, rule, and severity for every finding. A high or critical finding makes the command exit non-zero. Read [references/security-audit.md](references/security-audit.md) when interpreting findings. Protected Codex plugin paths are reported as skipped and are never modified.

### 7. Inspect entrypoints

Use `status` to see which host or project entrypoints point to which physical source:

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  status --project-root "/path/to/project" --include-sources
```

The report distinguishes direct absolute links, relative links, indirect links, broken links, and protected plugin entries. It also exposes both full-content and behavioral fingerprints.

### 8. Quarantine and restore

Quarantine only one explicitly selected Skill at a time. It is confirmation-gated, recoverable, refuses the manager itself, and refuses Codex plugin or WorkBuddy paths:

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  quarantine move --path "/path/to/suspicious-skill" --confirm

python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  quarantine list

python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  quarantine restore --manifest "/path/to/quarantine/timestamp/transaction.json" --confirm
```

The source directory or symlink is moved as one recoverable unit; an existing original destination is never overwritten during restore. Read [references/security-audit.md](references/security-audit.md) and [references/status-quarantine.md](references/status-quarantine.md) for the decision boundaries.

### 9. Roll back

Use the `transaction.json` written by `apply`:

```bash
python3 /absolute/path/to/winter-skill-manager/scripts/skill_system_manager.py \
  rollback --manifest "/path/to/backup/transaction.json" --confirm
```

Rollback is also confirmation-gated. Stop and report conflicts instead of removing a newer file or non-empty directory.

## Classification boundaries

- `personal-public`: source is under the user's configured public root.
- `personal-private`: source is under the user's configured private root.
- `third-party`: source is under the configured third-party root or has a strong third-party path signal.
- `project-with-skill`: the Skill directory also contains project markers such as `package.json` or `pyproject.toml`; keep the complete project separate from ordinary Skill sources.
- `plugin`: path is inside a protected plugin cache; inspect only.
- `external-repo-skill`: a Git remote exists but ownership is not established; ask the user.
- `symlink-entrypoint`: a working link whose canonical ownership is not yet known.
- `broken-link`: a symlink target is unavailable; do not guess a replacement.
- `unknown`: insufficient evidence; leave untouched.

## Output contract

Always report:

1. scan roots and skipped protected directories;
2. counts by category and the uncertain entries;
3. duplicate content groups and broken links;
4. audit findings and exact evidence when `audit` is used;
5. entrypoint health and protected paths when `status` is used;
6. proposed operations and which ones require confirmation;
7. backup, quarantine, and transaction paths after applying changes;
8. verification result and any remaining manual work.

Keep user-specific paths in runtime reports only. Never commit those reports into this public Skill repository.

Read references only when the corresponding mode or decision requires them. Do not load user inventory files into the public repository.
