# Winter Skills

Winter 的公开 Agent Skills 集合，提供可直接安装、复用和更新的 AI Agent 工作能力。

## Skills

| Skill | 用途 |
|---|---|
| `winter-ppt-creator` | 创建赛博朋克风格的网页 PPT，适合将主题、提纲或内容整理为可演示的单页 HTML 幻灯片。 |
| `winter-skill-system-manager` | 盘点、分类和维护本地 Agent Skills、软链接与项目级引用，支持安全审计、可恢复隔离、迁移、验证和回滚。 |

## 安装

使用通用的 [`skills` CLI](https://www.skills.sh/docs/cli) 安装，无需手动克隆仓库。

### 安装全部公开 Skill

```bash
npx -y skills add seventhocean/Winter-skills --global --all
```

### 安装指定 Skill

```bash
npx -y skills add seventhocean/Winter-skills \
  --skill winter-ppt-creator \
  --agent claude-code \
  --global
```

```bash
npx -y skills add seventhocean/Winter-skills \
  --skill winter-skill-system-manager \
  --agent claude-code \
  --global
```

将 `--agent claude-code` 替换为目标 Agent，也可以重复指定多个 Agent：

```bash
npx -y skills add seventhocean/Winter-skills \
  --skill winter-ppt-creator \
  --agent claude-code \
  --agent codex \
  --global
```

去掉 `--global` 可以安装到当前项目，适合随项目一起管理：

```bash
npx -y skills add seventhocean/Winter-skills \
  --skill winter-ppt-creator \
  --agent claude-code
```

## 更新

可以使用 `skills` CLI 更新已安装的 Skill：

```bash
npx skills update winter-ppt-creator --global
npx skills update winter-skill-system-manager --global
```

也可以重新运行对应的 `skills add` 命令。

## 使用

安装完成后，直接用自然语言描述任务即可。Agent 会在需要时调用相应 Skill。

- 需要制作网页 PPT 时，使用 `winter-ppt-creator`。
- 需要整理本地 Skill 或项目级 Skill 引用时，使用 `winter-skill-system-manager`。

Skill 的具体说明、参数和参考资料位于各自目录中。
