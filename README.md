# Winter-skills

冬天的公开 Skill 集合。每个 Skill 直接使用一个独立目录管理。

## 当前 Skill

- `winter-ppt-creator`：赛博朋克风格网页 PPT 生成
- `winter-skill-system-manager`：本地 Skill、软链接和项目引用的盘点、分类、安全审计、可恢复隔离与迁移管理

这里只放经过清理、可以公开发布的内容，不包含本机绝对路径、凭据、个人数据或私有素材。

## 安装方式

本仓库可以通过通用的 `skills` CLI 安装，不需要手动克隆整个项目。首次运行时直接使用 `npx` 即可。

### 安装单个 Skill

```bash
npx skills add seventhocean/Winter-skills \
  --skill winter-ppt-creator \
  --agent claude-code \
  --global
```

```bash
npx skills add seventhocean/Winter-skills \
  --skill winter-skill-system-manager \
  --agent claude-code \
  --global
```

将 `--agent claude-code` 替换为目标 Agent，也可以重复指定多个 Agent：

```bash
npx skills add seventhocean/Winter-skills \
  --skill winter-ppt-creator \
  --agent claude-code \
  --agent codex \
  --global
```

### 安装到当前项目

去掉 `--global`，Skill 会安装到当前项目对应的 Agent 目录，适合随项目一起管理：

```bash
npx skills add seventhocean/Winter-skills \
  --skill winter-ppt-creator \
  --agent claude-code
```

### 查看和更新

```bash
npx skills add seventhocean/Winter-skills --list
npx skills update winter-ppt-creator --global
```

更多参数和支持的 Agent 见 [`skills` CLI 文档](https://www.skills.sh/docs/cli)。
