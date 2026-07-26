# 入口状态与隔离恢复

## `status`

`status` 用于观察入口，不负责修复入口。它会显示：

- 入口属于 Claude、Agent、Codex、WorkBuddy 还是项目目录；
- 软链接目标是否存在且包含 `SKILL.md`；
- 链接是绝对路径、相对路径还是经过另一层软链接；
- 入口是否处于受保护的插件或 WorkBuddy 范围；
- 真实源的完整指纹和行为指纹。

Codex 插件缓存只报告状态，不参与移动、链接、隔离或删除。

## `quarantine`

隔离是可恢复的明确操作：

1. 只能指定一个 Skill 目录或指向 Skill 的软链接；
2. 必须显式传入 `--confirm`；
3. 真实目录和软链接整体移动到 `~/.winter-skill-manager/quarantine/<时间戳>/`；
4. 同时写入 `transaction.json`，记录原路径和隔离路径；
5. 恢复时原路径必须不存在，工具不会覆盖新的文件或目录；
6. 管理器自身、Codex 插件和 WorkBuddy 路径拒绝隔离。

```bash
python3 scripts/skill_system_manager.py quarantine move \
  --path "/path/to/skill" --confirm

python3 scripts/skill_system_manager.py quarantine list

python3 scripts/skill_system_manager.py quarantine restore \
  --manifest "/path/to/transaction.json" --confirm
```
