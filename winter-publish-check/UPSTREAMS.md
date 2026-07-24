# 上游来源与维护边界

`winter-publish-check` 是 Winter 在本地整合并持续维护的 Skill。它不是从零开始编写，而是基于以下两个 MIT 开源项目整理：

## 上游项目

### media-publish-check

- 仓库：[XshuiAi/media-publish-check](https://github.com/XshuiAi/media-publish-check)
- 本项目吸收：媒体证据检查、版权/隐私/AI/转载/营销披露、平台策略、R0-R4 风险框架和媒体候选扫描器；
- 许可证：见 `licenses/media-publish-check-LICENSE`。

### yuwen-publish-precheck

- 仓库：[yuwen-cool/yuwen-publish-precheck](https://github.com/yuwen-cool/yuwen-publish-precheck)
- 本项目吸收：中文文本候选扫描、抖音和国内平台规则、商业/医疗/金融规则、个人词库和保意修复流程；
- 许可证：见 `licenses/yuwen-publish-precheck-LICENSE`。

## 本项目的独立部分

- `SKILL.md`：Winter 的审核流程、抖音优先策略和个人化边界；
- `scripts/scan.py`：统一调度入口；
- `scripts/text_engine.py`、`scripts/media_engine.py`：在本项目内维护的两个扫描引擎；
- `rules/`：本项目使用的规则快照；
- `data/`：Winter 的个人规则、词库和审核沉淀；
- `tests/`：本项目自己的回归测试。

## 维护约定

- 本仓库不自动拉取或同步上游更新；
- 后续规则调整、误报修正和个人案例沉淀，以 Winter 的提交为准；
- 继承的许可证和版权声明继续保留；
- 不把本项目描述为两个上游项目的官方版本，也不把整理所得全部宣称为从零原创。
