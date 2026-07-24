# Winter Publish Check

Winter 的国内自媒体发布前审核 Skill，以抖音为默认平台，检查标题、简介、口播稿、字幕、封面和完整媒体的发布风险。

## 能做什么

- 扫描敏感词、行业词、站外导流和平台策略候选；
- 结合上下文判断版权、隐私、AI/转载/营销披露和效果主张；
- 输出风险位置、风险等级和保留原意的修改建议；
- 修改后重新扫描，区分已解决、仍存在和新增风险。

## 使用

在仓库根目录运行：

```bash
python3 scripts/scan.py --file /path/to/content.txt --platform douyin
```

商业内容或强监管行业需要显式声明：

```bash
python3 scripts/scan.py --file /path/to/content.txt \
  --platform douyin --commercial --industry finance
```

扫描器只提供复核候选，不直接宣布“违规”或保证过审；最终判断还要结合语境、画面、音频、来源、权利和当前平台规则。

## 目录

```text
SKILL.md              # AI 使用说明和审核工作流
scripts/              # 统一入口和两个扫描引擎
rules/                # 文本规则与媒体规则词库
references/           # 平台、版权、披露、行业和修改参考
data/                 # 本地个人规则与审核沉淀，默认不入 Git
tests/                # 关键行为回归测试
licenses/             # 上游项目许可证
UPSTREAMS.md          # 来源、改造范围和维护边界
```

## 维护边界

本项目基于两个开源 Skill 整合而来，后续由 Winter 在本仓库中独立迭代。不会自动同步上游；规则更新、个人经验和测试样例以本仓库为准。来源和许可证见 [UPSTREAMS.md](UPSTREAMS.md)。
