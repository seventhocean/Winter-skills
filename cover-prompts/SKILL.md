# 封面提示词库

> 收录经过验证的封面/配图提示词模板。只记风格和结构，不绑定具体内容。
> 每期出图时挑一个模板，替换变量即可。

---

## 模板索引

| 模板 | 风格关键词 | 画幅 | 适合场景 | 来源 |
|---|---|---|---|---|
| A. 新粗野主义-文章封面 | 粗黑边框、硬投影、撞色、大字 | 5:2 横版 | 公众号头图 / 观点封面 | [剪藏: 提示词美学解码](../../Clippings/提示词美学解码%20×%20新粗野主义：反AI味！.md) |
| B. 新粗野主义-产品视觉 | UI 界面碎片、broken grid、sticker 标签 | 5:2 横版 | 产品 landing page / 工具概念图 | 同上 |
| C. 新粗野主义-开发者视觉 | 终端窗口、代码卡片、等宽字体点缀 | 5:2 横版 | GitHub 封面 / 文档封面 / 技术教程 | 同上 |
| D. 暗色冬日系列 | 深海军蓝底、emerald green 发光、雪花线稿 | 3:4 竖版 | 抖音视频封面（WorkBuddy 教程系列） | 封面系列说明（项目内维护） |
| E. 赛博朋克系列 | 暗黑底、霓虹绿字、扫描线、电路板纹路、色散故障 | 3:4 竖版 / 16:9 横版 | 抖音视频封面（WorkBuddy Skill 展示） | 第三期 Skill 封面实战 |
| F. 新粗野主义-图生图 | 撞色色块、粗黑边框、硬投影、人物居中 | 3:4 竖版 / 4:3 横版 | 抖音视频封面（真人出镜 + 狂野色块） | 第四期 Vibe Coding 封面实战 |
| G. 蒸汽波-图生图 | 粉紫渐变、复古落日、透视网格、罗马柱 | 3:4 竖版 | 抖音视频封面（真人出镜 + 复古未来感） | 第五期 自媒体工作流 封面实战 |
| H. 杂志编辑风-图生图 | 衬线大字、栏栅网格、暖白底、留白 | 3:4 竖版 / 4:3 横版 | 抖音视频封面（真人出镜 + 高级排版感） | 第六期 文章排版器 封面实战 |
| I. 暗色电影感-科技评论/教学 | 暗色渐变底、电影光影、白+亮色撞色大标题、主题场景元素（评论型散落/教学型实体物体）、人物居右 | 3:4 竖版 | 抖音视频封面（AI 观点评论 + 概念教学 + 真人出镜） | 第八/九期封面实战 |

---

## 通用生图命令

```bash
python3 <image-script> "<prompt>" --size <ratio> --resolution 2k --output <output-path>
```

---

## A. 新粗野主义 · 文章封面

**风格锁**：neo-brutalist, thick black borders, hard offset drop shadows, flat bold color blocks, broken grid, oversized typography, sticker-like UI elements, anti-polish

**Avoid**：glassmorphism, soft gradient SaaS look, glossy 3D, realistic scene, complex dashboard, stock-photo style

**画幅**：5:2 横版

**变量**：

| 变量 | 说明 |
|---|---|
| `{主题}` | 文章标题/摘要/关键词 |
| `{标题}` | 封面主标题文字（可选，留空则自动判断） |
| `{颜色}` | 指定颜色或图形隐喻（可选，留空则无） |

**Prompt 模板**：

```
文章主题：{主题}
用途：文章封面
指定主标题文字：{标题}（可选）
特殊要求：{颜色}（可选）

Create a neo-brutalist article cover poster.
Aspect ratio: 5:2 landscape banner.

Main visual:
One dominant object or interface-like metaphor (a button, a toggle, a broken grid fragment, a card shape), surrounded by offset sticker-like UI cards, tags, and small warning-style labels.

Style lock:
neo-brutalist digital graphic design, thick black borders, hard offset drop shadows, flat bold color blocks, broken grid layout, oversized typography, sticker-like interface elements, raw web aesthetic, anti-polish, playful but structured.

Typography:
One large bold headline, using the text specified above (if left as "自动判断", match the language of the topic/summary given above). Add at most one small supporting label. Do not create fake or unreadable UI text.

Composition:
Asymmetrical layout, one dominant object, overlapping smaller cards and stickers, visible grid disruption, strong negative space, hard-edged geometry.

Color:
High-contrast flat colors — pick 3-4 from off-white, black, cobalt blue, bright yellow, red, purple. No gradients.

Texture:
Slight print grain, matte digital poster feel.

Avoid:
glassmorphism, soft gradient SaaS look, glossy 3D, realistic scene, full complex dashboard, stock-photo style.
```

---

## B. 新粗野主义 · 产品/工具视觉

**风格锁**：neo-brutalist UI illustration, raw interface blocks, thick black outlines, hard offset drop shadows, flat bold color blocks, broken grid, oversized buttons, sticker-like tags, anti-polish

**Avoid**：glassmorphism, soft shadows, glossy 3D, Apple-style clean UI, blue-purple gradient SaaS look, cinematic lighting, realistic office scene, generic laptop mockup, stock-photo style

**画幅**：5:2 横版

**变量**：

| 变量 | 说明 |
|---|---|
| `{产品}` | 产品名/功能/文章主题 |
| `{用途}` | 官网首屏 / Dashboard 概念图 / Pricing 页 |
| `{标题}` | 封面主标题（可选） |
| `{要求}` | 指定颜色/组件/排除元素（可选） |

**Prompt 模板**：

```
产品或主题：{产品}
用途：{用途}
指定标题文字：{标题}（可选）
特殊要求：{要求}（可选）

Create a neo-brutalist SaaS landing page hero illustration.
Aspect ratio: 5:2 landscape banner.

Main visual:
Turn the product/theme into a product page, tool interface, dashboard fragment, or pricing block, with several input fields, buttons, toggles, tabs, status labels, or pricing cards overlapping in a broken-grid layout — not just one isolated element.

Style lock:
neo-brutalist UI illustration, raw interface blocks, thick black outlines, hard offset drop shadows, flat bold color blocks, broken grid, oversized buttons, sticker-like tags, high contrast, playful but structured, anti-polish.

Typography:
Large bold title, using the headline text specified above (if left as "自动判断", match the language of the product/theme description given above), plus 2-3 short supporting labels (e.g. button or tab text). Do not create fake UI labels or unreadable microcopy.

Composition:
Asymmetrical layout, multiple overlapping cards and blocks, visible grid disruption, one dominant element, deliberate not messy.

Color:
Bright flat colors — pick 3-4 from off-white, black, signal yellow, cobalt blue, red, purple, green. No gradients.

Texture:
Slight print grain, matte digital poster feel.

Avoid:
glassmorphism, soft shadows, glossy 3D, Apple-style clean UI, blue-purple gradient SaaS look, cinematic lighting, realistic office scene, generic laptop mockup, stock-photo style.
```

---

## C. 新粗野主义 · 开发者/开源视觉

**风格锁**：neo-brutalist web design, thick black outlines, hard offset drop shadows, flat color panels, broken grid, raw HTML-inspired layout, oversized typography, deliberately unpolished but usable

**Avoid**：glassmorphism, soft gradient SaaS look, realistic IDE screenshot, readable real code, glossy 3D, cyberpunk neon, stock-photo style

**画幅**：5:2 横版

**变量**：

| 变量 | 说明 |
|---|---|
| `{项目}` | 开源项目名/API/技术教程主题 |
| `{用途}` | GitHub 封面 / 文档封面 / 技术教程配图 |
| `{标题}` | 封面主标题（可选） |
| `{要求}` | 品牌色/保留标识/排除元素（可选） |

**Prompt 模板**：

```
项目或主题：{项目}
用途：{用途}
指定标题文字：{标题}（可选）
特殊要求：{要求}（可选）

Create a neo-brutalist website interface concept.
Aspect ratio: 5:2 landscape banner.

Main visual:
A full-screen web layout combining a terminal window or code-card shape with misaligned content cards, navigation tabs, module tags, and status-label blocks. Do not render real, readable code — use abstracted blocky text lines instead.

Style lock:
neo-brutalist web design, thick black outlines, hard offset drop shadows, flat color panels, broken grid, raw HTML-inspired layout, oversized typography, high contrast, deliberately unpolished but usable.

Typography:
Large bold title, using the headline text specified above (if left as "自动判断", match the language of the project/tutorial description given above), monospace-flavored accents allowed for tags/labels only, plus 2-3 short supporting labels.

Composition:
Desktop landing page layout, asymmetrical grid, cards overlapping slightly, one dominant terminal/code block, visible block structure.

Color:
High-contrast flat colors, dark terminal background or off-white/black base allowed — pick 3-4 accent colors, no gradients.

Texture:
Slight print grain, matte digital poster feel.

Avoid:
glassmorphism, soft gradient SaaS look, realistic IDE screenshot, readable real code, glossy 3D, cyberpunk neon, stock-photo style.
```

---

## D. 暗色冬日系列（WorkBuddy 抖音视频封面）

**风格锁**：深海军蓝底 + emerald green 发光 + 雪花线稿，文字永远第一主角

**Avoid**：浅色底、大量插画装饰、大面积色块（会挤压文字呼吸感）

**画幅**：3:4 竖版（抖音封面实际比例）

**品牌色**：`#10B981`（emerald green）| 背景 `#0F1419`

**必含元素**（8 项缺一不可）：

1. 顶部：代码编辑器窗口（绿色标题栏点缀）
2. 主品牌字：`WorkBuddy`（emerald green 大字 + 微弱发光）
3. 主标题：从 0 到 1 入门教程（白色）
4. 副标题：当期具体内容（浅灰）
5. 右上角：白色雪花 icon（line-art）
6. 左下角：`BY 冬天` 小字签名
7. 右下角：`TUTORIAL NN` 期号
8. 背景：暗色 + 极淡远景雪花点 + 底部冬日森林剪影

**变量**：

| 变量 | 说明 |
|---|---|
| `[TITLE_LINE_1]` | 主标题（通常保持"从 0 到 1 入门教程"不变） |
| `[TITLE_LINE_2]` | 当期具体内容（必换） |
| `[NN]` | 期号，2 位数补 0（必换） |

**Prompt 模板**：

```
3:4 vertical cover with dark premium aesthetic. Deep dark navy
background (#0F1419) with subtle radial gradient (slightly
lighter in center). Top: a glowing code editor window with light
code, with a subtle emerald green accent on the title bar.
Center: 'WorkBuddy' in large bold bright emerald green (#10B981)
text with subtle glow. Below: '[TITLE_LINE_1]' in bold white.
Subtitle: '[TITLE_LINE_2]' in light gray. Top-right: a small
white snowflake icon line-art, slightly glowing. Bottom-left:
small 'BY 冬天' signature in light gray. Bottom-right:
'TUTORIAL [NN]' small. Add very faint dot pattern (like distant
snowflakes) in the background. Premium dark tech + winter night
theme.
```

**出图命令**：

```bash
python3 <image-script> "<prompt>" --size 3:4 --resolution 2k --output "<output-dir>/视频封面系列/{NN}_暗色冬日_视频封面"
```

---

##  构图原则（所有模板通用）

> 新粗野主义的"高级感"来自 **表面粗、结构精**——看起来乱，其实是精确控制的错落。
> 构图决定一张封面是"有设计感"还是"像 PPT 模板"。

### 两种构图对比

| | 层叠构图 ✅（推荐） | 排列构图 ❌（避免） |
|---|---|---|
| **元素关系** | 互相叠压、遮挡、大小不一 | 各自独立、平铺排列、互不干扰 |
| **视觉深度** | 有前后层次，视线有落点 | 扁平，一眼看完没有停留 |
| **空间利用** | 元素错落填充整个画面 | 元素集中在某个区域，留白无意义 |
| **Prompt 关键词** | `overlapping`, `staggered`, `layered`, `one dominant element, others orbit around it`, `varying sizes`, `diagonal flow` | `in a row`, `side by side`, `simple`, `minimal`, `clean layout` |

### 三层构图公式（竖版 3:4 推荐）

```
┌─────────────────────┐
│  ① 品牌层（顶）      │  ← WorkBuddy / 系列名，固定位置固定风格
│  ② 主题层（中）      │  ← 当期主标题 + 副标题，画面最大视觉锚点
│  ③ 信息层（底/散）   │  ← 卖点贴纸 / 图标，错落散布，不要排成一行
─────────────────────┘
```

- **品牌层**：位置固定，每期复用，建立系列辨识度
- **主题层**：占画面 40-50% 面积，是视觉第一落点
- **信息层**：3-5 个小元素，**错落散布**而非水平排列，大小不一，有前后叠压

### 避免的构图错误

- ❌ 元素全部排成一行（像货架上的商品）
- ❌ 所有元素同样大小（没有视觉节奏）
- ❌ 元素之间留均匀空白（像表格，不像海报）
- ❌ 画面底部 1/3 堆满装饰，上部空荡（头重脚轻）

### 抖音视频封面专属建议

3:4 竖版手机屏幕，用户扫一眼只有 **1-2 秒**：
- 主标题必须在画面**上半部分**（拇指不会遮住）
- 文字占画面至少 **30%** 面积（抖音信息流里要够大）
- 品牌色块（WorkBuddy 绿）至少出现 **1 处**，建立系列认知

---

## E. 赛博朋克系列（WorkBuddy Skill 展示封面）

**风格锁**：cyberpunk, dark void background (#050510), neon green (#10B981) brand text, neon pink (#ff2d7b) title, perspective grid, scanlines, chromatic aberration glitch, holographic wireframe, circuit board traces, volumetric light beams, particle dust, lens flares

**Avoid**：浅色底、白底、柔和色调、写实场景、卡片列表、信息过载（封面不是信息图）

**画幅**：3:4 竖版（抖音标准）/ 16:9 横版（视频缩略图）

**品牌色**：WorkBuddy 绿 `#10B981` | 标题粉 `#ff2d7b` | 期号绿 `#39ff14` | 背景 `#050510`

**必含元素**：

1. 画面中央大字：`WorkBuddy`（emerald green #10B981，最大号，外发光）
2. 主题标题（neon pink #ff2d7b，比品牌字更大）
3. 副标题/钩子句（浅灰，小号）
4. 期号（neon green #39ff14，glitch offset 效果）
5. `BY 冬天` 签名（深青小字，低调）
6. 背景氛围：透视网格 + 扫描线 + 粒子尘埃 + 光束
7. 装饰：线框几何体、电路板纹路、低透明度霓虹招牌碎片
8. ⚠️ 封面不列 Skill 名称——那是视频内容，不是封面内容

**核心原则**：封面是 teaser 海报，不是信息图。文字全部居中。观众看完封面只知道主题，想知道具体内容必须点进视频。

**变量**：

| 变量 | 说明 |
|---|---|
| `[TITLE]` | 当期主标题（如"必装的7个Skill"） |
| `[HOOK]` | 钩子文案（如"每天手动干活的，你亏大了"） |
| `[NN]` | 期号 |

**Prompt 模板（3:4 竖版）**：

```
Cyberpunk poster cover, 3:4 vertical for 抖音. Text centered, pure visual impact.

Dark void background (#050510) with deep perspective neon grid lines. Horizontal scanlines. Chromatic aberration glitch at edges. Floating holographic particle dust, lens flare streaks.

All text centered:

Top: WorkBuddy in MASSIVE bold emerald green (#10B981), largest text, with strong outer green glow and electric flicker.

Below, even larger: [TITLE] in neon pink (#ff2d7b), enormous, with strong outer glow and chromatic aberration offset.

Below: [HOOK] in light gray with subtle glow.

Bottom center: '[NN]' small in neon green (#39ff14) with glitch offset.

Very bottom: 'BY 冬天' tiny, centered, dark cyan, barely visible.

Surrounding text: holographic wireframe geometric shapes (green), circuit board traces (pink), Japanese/Chinese neon sign fragments at low opacity, diagonal volumetric light beams, hexagonal grid overlay.

No skill names, no lists, no cards. Centered typography. Dark, neon-drenched, cinematic.
```

**Prompt 模板（16:9 横版）**：

```
Cyberpunk video cover, 16:9 widescreen. All text CENTERED in frame, video thumbnail style.

Dark void background (#050510) with perspective neon grid. Horizontal scanlines. Chromatic aberration glitch. Floating holographic particles in green and pink. Wide cinematic lens flares.

CENTERED text stack:

Top: WorkBuddy in MASSIVE bold emerald green (#10B981), largest text, with strong outer green glow and electric flicker.

Below, even LARGER: [TITLE] in neon pink (#ff2d7b), huge, with strong outer glow and chromatic aberration offset.

Below: [HOOK] in light gray with subtle glow.

Below: '[NN]' small in neon green (#39ff14) with glitch offset.

Bottom: 'BY 冬天' tiny, centered, dark cyan, barely visible.

Left and right sides of centered text: holographic wireframe structures (green, left), circuit board traces (pink, right), Japanese/Chinese neon fragments at low opacity, diagonal volumetric beams from corners, hexagonal grid, particle dust.

No skill names, no lists, no cards. Centered typography, cyberpunk atmosphere filling edges. Cinematic, dark, neon-drenched.
```

**出图命令**：

```bash
# 竖版 3:4
python3 <image-script> "<prompt>" --size 3:4 --resolution 2k --output "<output-dir>/cover_skill_[NN]_v"

# 横版 16:9
python3 <image-script> "<prompt>" --size 16:9 --resolution 2k --output "<output-dir>/cover_skill_[NN]_h"
```

---

## 图生图通用框架（F/G/H 共享）

> 核心模式：**真人照片为底图 + AI 重绘背景 + 排版文字叠加**
> 人物始终居中、保持原貌，背景根据风格模板替换，文字按排版层级叠加。

**必含要素**（所有图生图模板通用）：

1. **人物锚定**：`The person in the center must remain exactly as-is — photorealistic, unaltered face/pose/clothing`
2. **背景风格**：根据 F/G/H 选择不同风格关键词
3. **文字层级**：主标题（大字）→ 副标题（小字）→ 期号（右下）→ 签名（左下）
4. **画幅**：竖版 3:4（抖音封面）/ 横版 4:3（视频缩略图）

**出图命令**：

```bash
# 竖版 3:4
python3 <image-script> "<prompt>" -i "<底图路径>" --size 3:4 --resolution 2k --output "<output-dir>/cover_ep[NN]_[风格]_v"

# 横版 4:3
python3 <image-script> "<prompt>" -i "<底图路径>" --size 4:3 --resolution 2k --output "<output-dir>/cover_ep[NN]_[风格]_h"
```

---

## F. 新粗野主义 · 图生图（狂野色块风）

**风格锁**：neo-brutalist, bold flat color blocks, thick black borders, hard offset drop shadows, broken grid, oversized typography, high-contrast flat colors (off-white, black, cobalt blue, signal yellow, bright red)

**Avoid**：暗色背景、柔和色调、写实场景、卡片列表、信息过载

**画幅**：3:4 竖版 / 4:3 横版

**变量**：

| 变量 | 说明 |
|---|---|
| `[底图]` | 真人自拍照片路径 |
| `[主标题]` | 封面核心大字（如 "VIBE CODING"） |
| `[副标题]` | 补充说明小字（如 "复刻动态网站，提示词不求人"） |
| `[期号]` | 期号（如 "EP.04"） |

**Prompt 模板**：

```
Douyin video cover, [画幅] poster, neo-brutalist graphic design style.

BASE PHOTO: The person in the center must remain exactly as-is — photorealistic, unaltered face/pose/clothing. The person is the anchor.

BACKGROUND: Bold flat color blocks in neo-brutalist style — thick black borders, hard offset drop shadows, high-contrast flat colors (off-white, black, cobalt blue, signal yellow, bright red). The color blocks are arranged asymmetrically as a dynamic background behind and around the person, creating energy without covering the person. Think broken grid, overlapping geometric shapes, raw poster aesthetic.

TYPOGRAPHY:
HERO TEXT — '[主标题]' in massive bold letters, neo-brutalist oversized typography, could overlap a color block, could have a thick black outline or hard shadow. This is the visual punch.
SUBTITLE — '[副标题]' in clean smaller text.
BOTTOM-RIGHT — '[期号]' in a sticker-style badge with thick black border.
BOTTOM-LEFT — 'BY 冬天' tiny signature.

COMPOSITION: Person centered in frame. Color blocks explode from edges inward but stop at the person's silhouette. Text is bold and punchy, layered over the color blocks. The overall feel: raw, energetic, designer poster, anti-polish, eye-catching in a fast-scrolling feed. Not messy — deliberate neo-brutalist chaos.
```

---

## G. 蒸汽波 · 图生图（复古未来风）

**风格锁**：vaporwave, pink-to-purple gradient sky, retro sun with horizontal stripe bands, chrome perspective grid floor, neon palm tree silhouettes, Greek/Roman column fragments, VHS scanlines, floating geometric shapes, chromatic aberration glitch, neon pink glow

**Avoid**：暗色底、写实场景、冷色调、信息过载

**画幅**：3:4 竖版

**变量**：

| 变量 | 说明 |
|---|---|
| `[底图]` | 真人自拍照片路径 |
| `[主标题]` | 封面核心大字（如 "自媒体工作流"） |
| `[副标题]` | 补充说明小字（如 "我用WorkBuddy搭建的"） |
| `[期号]` | 期号（如 "EP.05"） |

**Prompt 模板**：

```
Douyin video cover, 3:4 vertical poster, vaporwave aesthetic.

BASE PHOTO: The person in the center must remain exactly as-is — photorealistic, unaltered face/pose/clothing. The person is the anchor.

BACKGROUND: Classic vaporwave scene — pink-to-purple gradient sky, retro sun with horizontal stripe bands setting on the horizon, chrome perspective grid floor extending to infinity, scattered neon palm tree silhouettes, ancient Greek/Roman column fragments, soft VHS scanlines overlay, floating geometric shapes (pyramids, spheres) in chrome and neon pink. Dreamy retro-futuristic 80s digital nostalgia. The vaporwave world surrounds the person like a surreal digital dreamscape.

TYPOGRAPHY:
HERO TEXT — '[主标题]' in large bold letters with vaporwave glitch effect — chromatic aberration, slight RGB split, neon pink glow.
SUBTITLE — '[副标题]' in smaller cyan text with subtle glow.
BOTTOM-RIGHT — '[期号]' in small chrome-styled badge.
BOTTOM-LEFT — 'BY 冬天' tiny signature in lavender.

COMPOSITION: Person centered as the focal point. Vaporwave landscape fills the entire background. Text overlays with good contrast — the neon glow makes text pop against the gradient sky. Retro-futuristic, dreamy, digital nostalgia.
```

---

## H. 杂志编辑风 · 图生图（高级排版感）

**风格锁**：editorial magazine, warm off-white (#F5F0E8) background, subtle grid lines like newspaper columns, thin black divider lines, elegant serif font (Playfair Display / Didot style), lots of intentional white space, small serif page numbers or section markers

**Avoid**：撞色色块、霓虹发光、暗色背景、卡通风格、信息过载

**画幅**：3:4 竖版 / 4:3 横版

**变量**：

| 变量 | 说明 |
|---|---|
| `[底图]` | 真人自拍照片路径 |
| `[引语]` | 封面顶部引语（如 "我做了个"） |
| `[主标题]` | 封面核心大字（如 "文章排版器"） |
| `[副标题]` | 封面 tagline（如 "多种模板任选"） |
| `[期号]` | 期号（如 "EP.06"） |

**Prompt 模板**：

```
Douyin video cover, [画幅] magazine editorial style.

BASE PHOTO: The person in the center must remain exactly as-is — photorealistic, unaltered face/pose/clothing. The person is the anchor, treated like a magazine cover portrait.

BACKGROUND: Clean editorial magazine layout — warm off-white (#F5F0E8) background, subtle grid lines like newspaper columns, thin black divider lines, small serif page numbers or section markers as decorative elements.

TYPOGRAPHY:
HERO TEXT — '[主标题]' in LARGE elegant serif font (like Playfair Display or Didot style), black ink color, editorial masthead position at top.
Above it, smaller: '[引语]' in clean sans-serif.
SUBTITLE — '[副标题]' in small italic serif, positioned like a magazine tagline/deck.
BOTTOM-RIGHT — '[期号]' in small bold serif, like a magazine issue number.
BOTTOM-LEFT — 'BY 冬天' tiny signature.

COMPOSITION: Magazine cover layout — person as the central portrait, text arranged in a clear typographic hierarchy around them. Lots of intentional white space. The overall feel: a premium magazine cover, like The New Yorker or Monocle, but for a tech creator. Sophisticated, calm, confident — the cover itself demonstrates good typesetting.
```

---

## I. 暗色电影感 · 科技评论/教学（图生图）

> 参考 TZFILM 风格：暗色电影感场景底 + 真人居右 + 超大撞色标题居左 + **主题场景元素**
> **这是冬天自己的封面风格方向**——人物 + 字块 + 有叙事感的场景，形成系列辨识度。
> 两种子类型：**评论型**（观点输出，元素散落）和 **教学型**（概念讲解，元素做成场景物体）

**风格锁**：dark cinematic tech, deep navy-black gradient, volumetric lighting, rim light, movie-poster feel, ultra-bold title text (white + accent color), photorealistic person, thematic elements as substantial scene objects

**Avoid**：bright backgrounds, neo-brutalist color blocks, cartoon/anime style, cluttered layout, pastel colors, white background, vaporwave pink/purple

**画幅**：3:4 竖版

**必含元素**：

1. 背景：深海军蓝黑渐变 + 电影感光影（体积光、轮廓光），暗示暗色科技场景但不杂乱
2. 人物：真人抠图居中偏右，姿态配合主题（讲话手势/沉思/摊手），有轮廓光和暗背景分离
3. 顶部小标签：英文分类标签（如 "AI TRUTH · EP.08" / "AI LEARNING · EP.09"），白色小字 monospace
4. 主标题 LINE 1：白色超大粗体，占画面左侧 20-30%，有外发光
5. 主标题 LINE 2：亮色超大粗体（评论型用红色 #FF2D2D，教学型用 emerald green #10B981），紧接 LINE 1 下方
6. **主题场景元素**（核心变量——见下方设计原则）
7. 左下角：`BY 冬天` 小字签名

**主题元素设计原则（两种子类型）**：

### 评论型（观点输出类）
> 元素是**散落的小图形**，20-30% 透明度，大小不一角度各异，点缀在背景中

| 主题 | 对应元素示例 |
|---|---|
| AI 问题不是 AI 的锅 | 报错弹窗、破碎提示词框、警告三角、指向人类的食指、"???" 对话气泡 |
| AI 换皮肤 | 皮肤/主题切换图标、调色板碎片、CSS 代码卡片 |

### 教学型（概念讲解类）⭐ 新方向
> 元素是**实体的场景物体**，不是小图标——它们在画面中有体积、有位置、有叙事功能。观众一眼看到就知道这期讲什么。参考 TZFILM「只要出生就能拿1000$」放金库美金、「AI 能源危机」放风暴矿泉水瓶。

| 主题 | 场景元素设计 |
|---|---|
| AI 三要素（脑子/桌子/双手） | 悬浮发光大脑（上）+ 摆满文件的桌子（中）+ 机械手伸向桌面（下）——三件物体形成视觉三角 |
| AI 工作流 | 流水线/传送带 + 不同工位的机械臂 + 成品输出台 |
| AI 提示词工程 | 巨大的提示词输入框悬浮在空中 + 输出结果从框中流出 + 人物站在框前 |
| AI 工具对比 | 多个工具如武器般排列（扳手、螺丝刀、电锯）+ 人物站在中间选择 |
| AI 记忆/长期记忆 | 书架/档案柜 + 发光记忆球 + 人物翻阅 |
| AI 多 Agent 协作 | 多个工位/小房间 + 连线 + 中央指挥官 |
| AI 成本/Token | 加油站/电表 + 数字跳动着 + 人物看账单 |

> **核心区别**：评论型元素是"装饰"，教学型元素是"场景"。教学型的元素必须是有体积感的物体，和人物共存于同一个空间中。

**教学型场景设计流程**：

1. **读口播稿** → 找到核心比喻（稿子里的"就像…"）
2. **提取 2-3 个关键物体** → 每个比喻对应一个有体积的场景物体
3. **安排空间位置** → 物体之间形成视觉关系（三角/上下/左右）
4. **材质和光效** → 科技感材质（发光、透明、金属）+ emerald green 光效

**变量**：

| 变量 | 说明 |
|---|---|
| `[底图]` | 真人自拍照片路径（必须先压缩到 1200px 以内） |
| `[主标题 L1]` | 标题第一行（白色大字） |
| `[主标题 L2]` | 标题第二行（亮色大字，评论型红色，教学型 emerald green） |
| `[分类标签]` | 顶部小标签（如 "AI LEARNING · EP.09"） |
| `[子类型]` | 评论型 / 教学型 |
| `[主题场景描述]` | 2-3 个与当期内容相关的**场景物体**描述（教学型）或图形描述（评论型） |

**Prompt 模板**：

```
Douyin video cover, 3:4 vertical, cinematic [评论型/教学型] tech style.

BACKGROUND: Deep dark blue-gray gradient with dramatic cinematic volumetric lighting. Moody tech atmosphere. [评论型: dark void/stage] [教学型: surreal scene where thematic elements exist as physical objects in space].

PERSON: A real young Asian man with glasses, wearing white t-shirt, positioned center-right. [姿态描述 — 配合主题]. Photorealistic face and hands, unaltered. Subtle rim lighting separates from dark background.

TYPOGRAPHY (LEFT — THE STAR):
- Top small tag: '[分类标签]' in tiny white uppercase monospace
- HERO TITLE LINE 1: '[主标题 L1]' in MASSIVE bold white text, ultra-thick condensed sans-serif, left side, 20-30% of frame. Strong outer glow.
- HERO TITLE LINE 2: '[主标题 L2]' in BRIGHT [RED #FF2D2D / EMERALD GREEN #10B981], same ultra-bold weight, directly below line 1.
- Text has slight drop shadow for readability.

THEMATIC ELEMENTS ([评论型: scattered small graphics, 20-30% opacity] / [教学型: substantial scene objects forming a narrative tableau]):
[主题场景描述 — 具体描述 2-3 个物体的形态、位置、材质、光效]
[评论型: elements scattered, low opacity, various sizes]
[教学型: elements are physical objects with volume, positioned in the scene, telling the story in one glance]

BOTTOM: Small 'BY 冬天' signature, bottom-left, light gray.

COMPOSITION: 3:4 vertical cinematic poster. Title dominates left. Person center-right. Thematic elements [scattered / forming a scene]. High contrast, movie-poster feel.

Avoid: bright backgrounds, neo-brutalist color blocks, cartoon/anime style, cluttered layout, pastel colors, white background, vaporwave.
```

**出图命令**：

```bash
# ⚠️ 底图必须先压缩到 1200px 以内，否则 API 超时
python3 -c "
from PIL import Image
img = Image.open('原始照片.jpg')
img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
img.save('压缩后.jpg', 'JPEG', quality=85)
"

python3 <image-script> "<prompt>" \
  -i "压缩后.jpg" \
  -s 3:4 \
  -r 2k \
  -o "<output-dir>/cover_ep[N]_[风格]_v"
```

---

## 选择指南

| 你要做什么 | 用哪个模板 |
|---|---|
| 公众号文章封面 / 观点输出封面 | **A**（文章封面） |
| 产品/工具/SaaS 的概念展示图 | **B**（产品视觉） |
| 开源项目/GitHub README/技术教程封面 | **C**（开发者视觉） |
| WorkBuddy 教程系列抖音视频封面（冬日暗色风） | **D**（暗色冬日） |
| WorkBuddy 教程系列抖音视频封面（赛博朋克风） | **E**（赛博朋克） |
| 真人出镜 + 狂野色块 / 高能量视觉冲击 | **F**（新粗野主义-图生图） |
| 真人出镜 + 复古未来感 / AI 主题调性 | **G**（蒸汽波-图生图） |
| 真人出镜 + 高级排版感 / 工具展示类 | **H**（杂志编辑风-图生图） |
| **AI 观点评论 / 概念教学 + 真人出镜（自己的风格）** | **I**（暗色电影感-评论/教学） |

## 新增模板

需要加新模板时，按以下格式追加到索引表和本节：

```
## X. {模板名称}

**风格锁**：{关键词}
**Avoid**：{排除项}
**画幅**：{比例}
**变量**：{表格}
**Prompt 模板**：{代码块}
```
