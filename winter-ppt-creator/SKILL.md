---
name: winter-ppt-creator
description: "生成赛博朋克风格的网页PPT演示文稿。支持自定义内容，自动应用霓虹灯光效、故障动画和弹出式翻页效果。适用于技术分享、产品展示、创意演示等场景。当用户说做一个PPT、生成演示文稿、做赛博朋克风格的幻灯片、做技术分享的PPT时触发此Skill。"
agent_created: true
---

# Winter PPT Creator

生成赛博朋克风格的单文件 HTML 网页 PPT。霓虹灯光效、故障动画、弹出式翻页。

## 模板

当前唯一模板：`assets/template-cyberpunk.html`

## 工作流程

### 1. 确认需求

询问用户：
- 主题
- 每页的核心内容或大纲（默认 7-9 页）

### 2. 读取模板

读取 `assets/template-cyberpunk.html`，理解其结构。

### 3. 分析模板结构

模板包含 9 页标准结构：
- **P1 封面**：大数字 + 标题 + 副标题 + 日期
- **P2-P8 内容页**：7 种不同布局
  - P2: 2x2 网格布局
  - P3: 左右分栏布局
  - P4: Before/After 对比布局
  - P5: 三列流程布局
  - P6: 垂直步骤布局
  - P7: 图文混排布局（列表 + 模拟界面）
  - P8: 雷达图布局（中心 + 环绕节点）
- **P9 封底**：标签墙 + 关注引导

### 4. 内容填充

根据用户提供的内容：
1. 确定每页使用哪种布局
2. 替换文本内容
3. 搭配霓虹色类（neon-cyan/pink/green/purple/yellow）
4. 保持动画延迟类（d1-d10）

### 5. 输出文件

保存到用户的工作目录，文件名示例：`技术分享-WorkBuddy-赛博朋克.html`

## 设计风格速查

### 色系

| 变量 | 色值 | 常用场景 |
|------|------|----------|
| `--neon-cyan` | #00f0ff | 主色，信息/链接 |
| `--neon-pink` | #ff2d7b | 强调，对比/警告 |
| `--neon-green` | #39ff14 | 成功/数字高亮 |
| `--neon-purple` | #b026ff | 创意/工具 |
| `--neon-yellow` | #ffe600 | 亮点/市场 |

### 字体

- 英文标题：`Orbitron`（科技感粗体）
- 中文标题：`Noto Sans SC` 900 字重
- 代码：`JetBrains Mono`

### 动画系统

**入场动画类**：
- `a-up` / `a-left` / `a-right` — 方向入场
- `a-scale` — 缩放弹入
- `a-glitch` — 故障入场
- `a-slam` — 从上砸下
- `a-rotate` — 旋转入场

**延迟系统**：`d1`-`d10`，间隔 0.1s → 1.4s，控制元素依次入场。

**翻页效果**：弹出式（scale 0.85 → 1.0 + opacity 淡入）。

**循环动画**：
- `neonPulse` — 霓虹脉冲
- `scanDown` — 扫描线
- `gridDrift` — 网格漂移

### 布局组件

| 类名 | 用途 |
|------|------|
| `glass-card` | 玻璃拟态卡片（加 `.pink/.green/.purple` 变色） |
| `skill-card` | 带四角装饰的技能卡 |
| `office-grid` | 2x2 网格 |
| `flow-row` | 三列流程 |
| `transform-box` | Before/After 对比 |
| `radar-container` | 雷达环（中心 + 环绕节点） |
| `cover-number` | 超大霓虹数字（封面用） |
| `label` | 小号大写分类标签 |
| `title-big` / `title-zh` | 大标题 |
| `subtitle` | 副标题 |

## 注意事项

- 动画延迟类（d1-d10）必须保留，确保视觉节奏
- 霓虹色类（neon-*）可灵活搭配
- 翻页 JS 逻辑（go 函数）是弹出式效果的核心，不要删除
- 扫描线、网格背景等装饰元素增强氛围，建议保留
- 后续新增风格模板时，在 `assets/` 中添加 `template-风格名.html`，并更新此文档
