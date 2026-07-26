# 分类与边界

## 证据优先级

按以下顺序判断来源，不能只看目录名称：

1. 用户明确指定的真实源目录；
2. 当前路径是否位于用户配置的公开、私有或第三方根目录；
3. 是否位于受保护的插件缓存；
4. `SKILL.md` 的 `name`、`description` 和内容特征；
5. Git remote、仓库 README 和目录结构；
6. 路径名称和文件命名，只能作为弱信号。

## Skill 与完整项目

发现 `SKILL.md` 不等于发现一个独立 Skill。若同一目录还包含 `package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、Remotion 配置或其他明确的项目入口，将它标记为 `project-with-skill`。

这类目录应保留完整项目运行所需的文件；只在项目内部存在可分发的 Skill 包时，另行建立 Skill 入口。不要把 `.venv`、`node_modules`、`build`、`out` 等运行时内容移动到 Skill 源目录。

## 常见分类

| 分类 | 证据 | 默认动作 |
|---|---|---|
| `personal-public` | 位于用户配置的公开根目录 | 保留；可由入口链接使用 |
| `personal-private` | 位于用户配置的私有根目录 | 保留；禁止发布 |
| `third-party` | 位于用户配置的第三方根目录，或用户明确确认来源 | 保留；不改写内容 |
| `plugin` | 位于受保护插件缓存 | 只读检查 |
| `project-with-skill` | Skill 与项目标记共存 | 单独维护完整项目 |
| `external-repo-skill` | 有 Git remote，但无法确认所有权 | 请求确认 |
| `unknown` | 没有足够来源证据 | 不移动、不删除 |
| `broken-link` | 软链接目标不存在 | 请求确认真实目标 |

“有 Git remote”只能证明它被版本控制，不能证明它是用户原创。描述中出现个人品牌也只能作为线索，不能替代来源证据。

## 受保护范围

默认不修改：

- Codex 插件缓存；
- WorkBuddy 内部数据和生态目录；
- 软件包管理器目录；
- 当前项目的业务文件；
- 用户没有列入计划的目录；
- 无法确认来源的 Skill。

如果用户明确要求扩大范围，先重新生成 inventory 和 plan，再单独确认。
