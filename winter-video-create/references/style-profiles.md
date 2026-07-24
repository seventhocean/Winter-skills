# Winter Video Style Profiles

## 用途

风格 Profile 只负责“看起来怎样”和“动起来怎样”，不负责决定口播讲什么、舞台使用哪些空间锚点或素材放在哪里。所有 Profile 都必须兼容同一份 `scene` / `layers[]` 契约。

## 选择规则

- 当前只有一个已归档 Profile：`clinical-tech`。
- 一条视频只使用一个主 Profile。章节可以使用该 Profile 的 `chapterAccent` 改变强调色和环境色，但不能随意更换字体、卡片材质和运动语法。
- 用户提供参考视频或提出新的视觉方向时，先在当前项目中实现和验证，不提前创建风格名称，也不在本文件占位。
- 项目实验风格没有正式 `styleProfile`；在 `work/制作规格.md` 中标记为“项目实验风格（暂不入库）”。

## Profile 契约

每个风格至少定义：

```json
{
  "styleProfile": "clinical-tech",
  "tokens": {
    "background": "#07121d",
    "surface": "rgba(4,17,31,.88)",
    "text": "#f5f9ff",
    "mutedText": "#afc0d2",
    "accent": "#32aeff",
    "success": "#42df86",
    "warning": "#ffc34d",
    "danger": "#ff6577"
  },
  "typography": {
    "display": "system-sans-heavy",
    "body": "system-sans",
    "mono": "Menlo"
  },
  "motion": {
    "entrance": "power4.out",
    "emphasis": "easeOutCubic",
    "transition": "cross-stage"
  },
  "surface": "dark-glass",
  "density": "editorial-3-to-6"
}
```

实现组件读取 tokens，不在 `Stage`、`DataStory` 或 `StageTopology` 中硬编码颜色和字体。缺少字体时使用明确的 fallback，不把字体文件复制进每个视频项目。

## 已归档风格

### `clinical-tech`

- 适合：AI 工具、工作流、API、Skill、产品教程和数据解释。
- 视觉：深蓝黑背景、冷色玻璃、蓝 / 绿 / 黄 / 红状态色。
- 材质：低透明玻璃、细边框、轻微模糊；避免游戏 HUD 和厚重霓虹。
- 运动：路径先行、节点接通、数字增长、状态替换；进入利落，停留清晰。
- 密度：3–6 个可见元素，适合整屏多锚点舞台。

## 从项目沉淀为风格

不要先命名风格再寻找画面证明它存在。按以下顺序沉淀：

1. 在真实视频项目中完成一套新的视觉实践。
2. 交付完整成片并记录有效的颜色、字体、材质、运动和密度。
3. 在另一个舞台或后续项目中至少复用一次，确认它不是一次性设计。
4. 提炼稳定 tokens、字体 fallback 和 Remotion / HyperFrames 共享接口。
5. 完成 `talking-head-editorial`、`data-story`、`operation-upper` 三类舞台验证。
6. 通过连续帧、文字可读性、操作保护区和角落聚集检查后，再命名并加入“已归档风格”。

没有走完这条路径的视觉尝试只属于项目，不属于 Skill 的风格库。新增正式风格时只修改本文件和对应渲染模板，不复制整份 Skill。

风格 Profile 不得改变以下硬约束：音频时间轴、真实操作模块优先、字幕最后合成、文字正常方向、最终只有一个音画封装出口。
