# 迁移计划格式

`plan` 命令生成 JSON。默认所有操作都是 `approved: false`，用户确认后才可以改为 `true`。

## 操作字段

```json
{
  "id": 1,
  "action": "move | link | remove | keep | review",
  "approved": false,
  "path": "/source/or/entrypoint",
  "target": "/canonical/source",
  "destination": "/new/entrypoint/or/source",
  "category": "personal-public",
  "reason": "why this operation is proposed"
}
```

只有以下操作可以在 `apply --confirm` 中执行：

- `move`：把一个已确认的源目录移动到目标位置；
- `link`：把目标位置创建为指向已存在真实源的软链接；
- `remove`：把已确认的条目移动到备份目录，需要额外的 `--allow-delete`；
- `keep`：不改动；
- `review`：不改动，等待用户补充信息。

## 修改计划的要求

- `move` 必须同时提供 `path` 和 `destination`；
- `link` 必须同时提供 `destination` 和 `target`；
- `remove` 必须提供 `path`，且不能把它用于未知来源的自动清理；
- 不能把插件缓存、虚拟环境、依赖目录或项目运行产物写入迁移操作；
- 每一条变更都要能在 `transaction.json` 中反向追踪；
- 计划本身可以存放在临时目录，不要提交包含本地路径的计划到公开仓库。

## 典型确认流程

```text
inventory → classify → plan → 用户逐项确认 → 编辑 approved → apply --confirm → verify
```

如果验证失败，先保留备份和 transaction manifest，再决定是否 `rollback --confirm`。不要用手工删除的方式“修复”失败迁移。
