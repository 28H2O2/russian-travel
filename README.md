# Русский для Узбекистана · 俄语生存包

> ~250 张俄语生存短语卡，给 2026 年 8 月去乌兹别克斯坦的旅行者使用。
> 借 ogden.munch.love 的形式语言，重写内容逻辑。
> PWA、离线可用、无注册、无收集。

项目约定：[`CLAUDE.md`](./CLAUDE.md)
卡片 schema：[`docs/card-schema.md`](./docs/card-schema.md)
在线：<https://russian-travel-tau.vercel.app>

## 快速开始

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # 生成 dist/ 静态站（含 service worker）
npm run preview      # 预览生产构建
npm run check        # astro check (TypeScript)
```

## 项目状态（截至 2026-05-27）

- ✅ **W1 完成** 脚手架 + 20 张占位卡端到端：8 场景 + 必备柜 + 卡片可展开 + 手机优先布局
- ✅ **W2 完成** 100 张 v1 内容（4 场景 × 25）+ Edge TTS 200 个真发音 mp3 + IndexedDB 进度 + SM-2 SRS + JSON 导入导出
- ✅ **W3 完成（提前）** PWA service worker + 离线音频预缓存 + manifest + 全套图标 → v1 上线
- ✅ **W4-6 主体完成** v2 扩到 230 张俄语卡（8 场景齐全）+ 15 张乌兹别克语礼貌包彩蛋（/uzbek 独立页 + uz-UZ TTS） → **v2 上线**
- ⏳ **剩余 v2 待办**：现场反馈按钮（🚩）
- ⏳ **W7-10** 用户进入纯学习期，旅行前掌握 80+ 张
- ⏳ **8 月在路上** 现场标记错卡、Airbnb 房东扫一眼 Top 30

## 四个页面

| 路径 | 干什么 |
|---|---|
| `/` | 主页：8 场景 + 必备柜 + 230 张卡浏览；右上 彩蛋 / 练习 / 数据 入口；右下 FAB 显示"今日 N 张待复习" |
| `/practice` | SRS 练习：今日队列 → 翻面 → 3 按钮评分（忘了/一般/很会）。键盘空格翻面、1/2/3 评分；每日新卡上限 20 |
| `/data` | 4 桶统计（未学/到期/学习中/已掌握）+ JSON 导入导出 + 危险区清空 |
| `/uzbek` 🇺🇿 | 彩蛋页：15 句乌兹别克语礼貌包（招呼 / 谢谢 / 餐桌 / 巴扎）。不进 SRS，纯文化加分项；每张卡的核心字段是 `why_uzbek`——为什么不说俄语要说这句 |

## 目录

```
src/
├── data/                   # cards.json / scenes.json / uzbek.json — 唯一内容真理
├── components/             # Card / SceneSection / EssentialBar / AudioButton / PolitenessBadge / UzbekCard
├── layouts/Layout.astro    # 全站外壳（含 PWA / iOS meta）
├── lib/
│   ├── types.ts            # Card / Scene / UzbekCard 类型
│   ├── data.ts             # cards.json 访问层
│   ├── srs.ts              # SM-2 算法 + 队列 + bucketize（纯函数）
│   ├── db.ts               # IndexedDB 薄封装（progress + meta + 每日新卡上限）
│   └── progress-export.ts  # JSON bundle 导出 / 导入（带 schema 校验）
├── pages/
│   ├── index.astro         # 主页
│   ├── practice.astro      # SRS 练习
│   ├── data.astro          # 统计 + 备份
│   └── uzbek.astro         # 🇺🇿 乌兹别克语彩蛋
└── styles/global.css       # 所有 design tokens（CSS 变量）

public/
├── audio/                  # 460 个俄语 mp3 + 30 个乌兹别克语 mp3（慢/正常）
├── favicon.svg
├── icon-{192,512,512-maskable,apple-touch}.png

scripts/
├── generate-tts.py         # 俄语 Edge TTS 主流水线（voice ru-RU-SvetlanaNeural）
├── generate-tts-uzbek.py   # 乌兹别克语 TTS（voice uz-UZ-MadinaNeural）
├── generate-icons.mjs      # sharp 把 favicon.svg 光栅化为 PWA 图标
├── expand-cards-v1.py      # 一次性：把 cards 从 20 张扩到 100 张（原稿）
├── expand-cards-v2.py      # 一次性：把 cards 从 100 张扩到 230 张（原稿）
└── generate-silent-stubs.sh  # 已退役：W1 用过的 silent beep；保留作 TTS 失联应急

docs/
└── card-schema.md          # 卡片字段契约（Card；uzbek schema 在 src/lib/types.ts）
```

## 改东西的入口

| 想改什么 | 改哪里 |
|---|---|
| 俄语卡片内容 | `src/data/cards.json` （改 data、不改组件） |
| 乌兹别克彩蛋 | `src/data/uzbek.json` |
| 场景顺序 / 颜色名 / 目标卡片数 | `src/data/scenes.json` |
| 色板、字体、卡片圆角阴影 | `src/styles/global.css` 的 `:root` 变量 |
| 卡面布局 | `src/components/Card.astro` |
| 主页结构 | `src/pages/index.astro` |
| SRS 算法（间隔、ease、评分映射） | `src/lib/srs.ts` |
| 练习页 UX（翻面 / 评分 / 快捷键） | `src/pages/practice.astro` |
| 备份导入导出 schema | `src/lib/progress-export.ts` |
| PWA 预缓存策略 / manifest | `astro.config.mjs` |

## 生成 / 补充音频

```bash
# 装 edge-tts（任选其一）
uv tool install edge-tts          # 推荐
# 或 pip install edge-tts

# 增量补卡：已存在的 mp3 自动跳过；只补缺的
uv run --with edge-tts python3 scripts/generate-tts.py          # 俄语
uv run --with edge-tts python3 scripts/generate-tts-uzbek.py    # 乌兹别克语
```

边缘网络抽风时会留下 <100 字节的失败 mp3；这时跑：

```bash
find public/audio -name '*.mp3' -size -100c -delete
uv run --with edge-tts python3 scripts/generate-tts.py   # 只重跑失败那几个
```

## 离线 / PWA

- 部署后首次打开 → service worker 预缓存全部 HTML / JS / CSS / 图标 / 字体 / 490 个 mp3（约 9 MB）
- 手机 Safari/Chrome：分享 → "添加到主屏幕"
- 主屏图标启动 → standalone 全屏
- 飞行模式可用：230 俄语卡 + 15 乌兹别克语彩蛋 + 全部音频 + SRS 进度

## 设计原则（不可妥协）

1. **手机优先**
2. **离线必达**
3. **零账号、零收集**
4. **deadline 大于 scope**——v1 必须 week 3 前上线

## License

Personal project. 内容仅供学习参考；俄语未经母语者审校时带 `⚠ AI 未审` 标签。
