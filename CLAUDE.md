# Russian Travel — 项目约定

> 一个 PWA 网站：~250 张俄语生存短语卡，给 2026 年 8 月去乌兹别克斯坦的旅行者使用。
> 借 ogden.munch.love 的形式语言，但重写内容逻辑——这是"乌兹别克斯坦俄语生存包"，不是"俄语高频前 N 词"。

完整规划由 Claude Code 的 plan mode 文件持有（不入仓）。

---

## 不可妥协的产品红线

1. **手机优先**——所有视觉、交互、性能决策以手机竖屏为第一目标。PC 上能用是副产品。
2. **离线必达**——所有卡片 + 所有音频 + SRS 进度，飞行模式下完整可用。
3. **零账号、零收集**——保留 Ogden 站的"无注册、不收集任何信息"精神。
4. **deadline 大于 scope**——v1 必须 week 3 上线（不晚于 2026-06-15）。不够的卡片砍内容、不砍 deadline。

---

## 内容真理

`src/data/cards.json` 是所有卡片内容的唯一真理来源。每张卡片必须严格遵守 schema（见 `docs/card-schema.md`）。
当 `cards.json` 与代码冲突时，**改代码不改数据**。

每张卡片必须有：
- `cyrillic`（必含重音标记 `́`）
- `transliteration`（发音式拉丁化，反映元音弱化等实际声学，不是 BGN/PCGN 学术规范）
- `chinese`（中文翻译）
- `literal`（字面直译，让用户看见结构）
- `audio.phrase_normal` + `audio.phrase_slow`（两个 mp3 路径）
- `politeness`（`Вы` / `ты` / `neutral`）
- `likely_responses`（数组，通常 1-3 条——本项目核心创新字段。
  **唯一允许空数组的情况**：独词应答类——数字 / `Да` / `Нет` / `Хорошо́` / `Пожа́луйста`
  / 方向 (`Пря́мо` / `Нале́во` / `Напра́во`) / 付款方式 (`Нали́чными` / `Ка́ртой`)
  / 堂食打包 (`Здесь` / `С собо́й`) 这类卡本身就是"回答"，没有"对方下一句"。
  其它句子必须给至少 1 条 likely_responses。）
- `slots`（数组，可以是空数组）
- `local_note`（可以是空字符串，但优先有）
- `verification_status`（默认 `ai_generated_unreviewed`）

---

## 8 场景 + 1 彩蛋

| id | 中文名 | 颜色 (CSS var) | v1 | v2 |
|---|---|---|---|---|
| `essentials` | 必备应答 & 礼貌 | `--scene-yellow` | 25 | 25 |
| `money` | 数字 & 钱 | `--scene-green` | 25 | 30 |
| `transport` | 交通 | `--scene-blue` | 25 | 35 |
| `food` | 餐饮 | `--scene-red` | 25 | 40 |
| `lodging` | 住宿 | `--scene-purple` | — | 25 |
| `shopping` | 购物砍价 | `--scene-orange` | — | 30 |
| `emergency` | 应急 | `--scene-slate` | — | 20 |
| `chat` | 闲聊 & 文化 | `--scene-gray` | — | 25 |
| `uzbek` | 🇺🇿 乌兹别克语礼貌彩蛋 | `--scene-uzbek` | — | 15 |

顶部"必备卡"便捷柜：跨场景挑选 `is_essential: true` 的 10 张钉顶，颜色保留卡片原场景色。

---

## 代码规范

- **语言**：TypeScript（严格模式）+ Astro 组件
- **样式**：Tailwind 工具类 + 一份 `global.css` 装 design tokens + 仅写极少自定义 utility
- **不引入**：React、Vue、状态管理库（IndexedDB 直读直写）、UI 组件库
- **音频文件**：`public/audio/<scene>/<id>_<normal|slow>.mp3`，对应 cards.json 里的 `audio.phrase_*`
- **每个超过 30 行的源文件头部加中文注释**：功能 / 输入（路径）/ 输出（路径）/ 如何运行 / 依赖 / 在项目中起的作用

---

## 目录约定

- `src/data/` —— 内容真理（cards.json / scenes.json / uzbek.json）
- `src/components/` —— Astro 组件
- `src/lib/` —— 纯 TS 模块（SRS / IndexedDB / 音频预下载 / 进度导入导出）
- `src/pages/` —— 路由页面
- `public/audio/` —— 预生成的所有 mp3
- `scripts/` —— 一次性内容生产与音频生成脚本（不进 PWA bundle）
- `docs/` —— AI-人共读的文档体系（card-schema.md、content-pipeline.md、uzbekistan-notes.md 等）

---

## 推进节奏

- ✅ W1 (5/26 - 6/1): 脚手架 + 20 张占位卡端到端
- ✅ W2 (6/2 - 6/8): 100 张 v1 内容 + Edge TTS + IndexedDB + SM-2 + JSON 导入导出
- ✅ W3 (6/9 - 6/15): PWA + 离线音频预缓存 + 移动端打磨 → **v1 已上线（提前）**
- ⏳ W4-6 (6/16 - 7/6): 扩到 250 张 + Uzbek 彩蛋 + 现场反馈按钮 → **v2 上线**
- ⏳ W7-10 (7/7 - 8/3): 用户进入纯学习期

> 截至 2026-05-27：W1/W2/W3 完成，部署在 <https://russian-travel-tau.vercel.app>。

---

## AI 协作规则

- 改卡片优先改 `cards.json`，不改组件
- 改设计 token 优先改 `global.css` 的 CSS 变量，不改 Tailwind 配置
- 内容生产相关脚本放 `scripts/`，不污染 `src/`
- 跑 dev / build 后必须自查：手机视口下能否一眼看到卡片三行（cyrillic / 音译 / 中文），西里尔字母字体是否可读，重音 mark 是否对齐
- LLM 生成的卡片必须保留 `verification_status: ai_generated_unreviewed`，不许偷偷标 verified

