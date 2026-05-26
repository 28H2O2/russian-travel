# Русский для Узбекистана · 俄语生存包

> ~250 张俄语生存短语卡，给 2026 年 8 月去乌兹别克斯坦的旅行者使用。
> 借 ogden.munch.love 的形式语言，重写内容逻辑。
> PWA、离线可用、无注册、无收集。

项目约定：[`CLAUDE.md`](./CLAUDE.md)
卡片 schema：[`docs/card-schema.md`](./docs/card-schema.md)

## 快速开始

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # 生成 dist/ 静态站
npm run preview      # 预览生产构建
```

## 项目状态

- **W1 (完成)** 脚手架 + 20 张占位卡端到端：8 场景 + 必备柜可见、卡片可展开、音频按钮可点（silent stub）、手机优先布局
- **W2 (进行中)** 100 张 v1 内容生产 + Yandex TTS 真发音 + IndexedDB + SM-2 SRS
- **W3** PWA + 离线音频 + 移动端打磨 → **v1 上线**
- **W4-6** 扩到 250 张 + Uzbek 彩蛋 + 现场反馈按钮 → **v2 上线**
- **W7-10** 用户进入纯学习期

## 目录

```
src/
├── data/          # cards.json / scenes.json — 唯一内容真理
├── components/    # Card / SceneSection / EssentialBar / AudioButton / PolitenessBadge
├── layouts/       # Layout.astro 全站外壳
├── lib/           # types + data 访问层（W2 加 srs / db / progress）
├── pages/         # index.astro 主页
└── styles/        # global.css — 全部 design tokens

public/audio/      # mp3 文件（W1 是静音 stub）
scripts/           # 一次性内容/音频生产脚本
docs/              # AI-人共读的文档体系
```

## 改东西的入口

| 想改什么 | 改哪里 |
|---|---|
| 卡片内容 | `src/data/cards.json` |
| 场景顺序 / 颜色名 / 目标卡片数 | `src/data/scenes.json` |
| 色板、字体、卡片圆角阴影 | `src/styles/global.css` 的 `:root` 变量 |
| 卡面布局 | `src/components/Card.astro` |
| 主页结构 | `src/pages/index.astro` |

## 生成音频占位

```bash
bash scripts/generate-silent-stubs.sh    # W1 用：silent mp3
# W2 会换成真 Yandex SpeechKit
```

## 设计原则（不可妥协）

1. **手机优先**
2. **离线必达**
3. **零账号、零收集**
4. **deadline 大于 scope**——v1 必须 week 3 前上线

## License

Personal project. 内容仅供学习参考；俄语未经母语者审校时带 `⚠ AI 未审` 标签。
