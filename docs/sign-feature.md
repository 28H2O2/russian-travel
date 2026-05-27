# 路牌识字 /signs — Feature 文档

> 30 张真实塔什干 / 俄语国家招牌图。被动识字训练，独立于 250 张短语卡和 15 张 Uzbek 彩蛋。

---

## 为什么做这个

现有体系（230 张俄语 + 15 张 Uzbek + SRS 练习）训练的是「主动产出」：能说、能听懂回话。但实地的塔什干，**80% 俄语 / 乌兹别克语接触来自眼睛**：

- 机场指示牌
- 地铁站名 + 站内出口标识
- 巴扎摊位编号 + 品类区
- 餐厅菜单
- 药店 / 应急服务

会开口但看不懂招牌，照样寸步难行。这模块就是把这块缺口补上。

---

## 与短语卡的区别

| | 短语卡 / Uzbek 彩蛋 | 路牌识字 |
|---|---|---|
| 认知任务 | 主动产出（说 + 听） | 被动识别（读） |
| 主信息 | 音频 + 文字 | 真实照片 + 文字 |
| 数据形态 | `Card` / `UzbekCard` | `Sign` |
| 进 SRS | ✅ Russian Cards | ❌（不同认知曲线） |
| 内容来源 | LLM 生成 | Wikimedia Commons + Flickr CC |

---

## 数据结构

定义在 `src/lib/types.ts`：

```ts
export type SignCategory = 'airport' | 'street' | 'market' | 'restaurant' | 'public';

export interface SignAttribution {
  author: string;
  source_url: string;
  license: string;
  via?: string;
}

export interface Sign {
  id: string;
  category: SignCategory;
  image: { src: string; alt: string; attribution: SignAttribution };

  ru?: string;          // 俄语西里尔
  ru_translit?: string; // 发音式拼音
  uz_latin?: string;    // 乌兹别克语拉丁
  uz_cyrillic?: string; // 乌兹别克语西里尔

  chinese: string;
  literal?: string;
  context: string;
  local_note?: string;
}
```

真理来源：`src/data/signs.json`。

---

## 分类与 v1 内容 (30 张)

| Category | 中文 | Icon | v1 数量 |
|---|---|---|---|
| `airport` | 机场 | ✈️ | 5 |
| `street` | 街道 & 地铁 | 🚏 | 7 |
| `market` | 超市 & 巴扎 | 🛒 | 6 |
| `restaurant` | 餐厅 & 菜单 | 🍽️ | 6 |
| `public` | 公共标识 & 应急 | ⚠️ | 6 |

颜色映射：复用现有 scene 色变量，不引入新 token：
- `airport` / `street` → `--scene-transport`（蓝）
- `market` → `--scene-shopping`（橙）
- `restaurant` → `--scene-food`（红）
- `public` → `--scene-emergency`（灰）

---

## 内容生产 Pipeline

### 阶段 1: 抓候选 — `scripts/fetch-signs.py`

调用 Wikimedia Commons MediaWiki API，对 ~16 个搜索 query（每个 ≤8 结果）做：

1. 搜索 namespace=6（File:）
2. 过滤 license：保留 CC0 / PD / CC-BY / CC-BY-SA（含全部子版本）
3. 拒绝：NonCommercial、NoDerivatives、Fair use
4. 仅图片 MIME（jpg / png / webp）
5. 下载 1000px 宽缩略图到 `scripts/.signs-staging/<query_slug>/img_NN.<ext>`
6. 输出 `scripts/.signs-staging/_manifest.json` 含每张图的 author / license / source_url / desc

`.signs-staging/` 被 `.gitignore` 排除（不入仓、不入 dist）。

### 阶段 2: 人工挑选 + 转码 — `scripts/build-signs.py`

脚本内嵌 `SELECTIONS: list[dict]`，每条指向一张 staging 图 + 完整字段（chinese / context / local_note / ru / uz_*）。运行后：

1. 调 `cwebp -q 78 -resize 960 0`：转 webp + 缩到 960px 宽
2. 写到 `public/signs/<category>/<id>.webp`
3. 从 manifest 自动抓 attribution（author / license / source_url）
4. 生成最终 `src/data/signs.json`

### 阶段 3: Astro build

`public/signs/**/*.webp` 自动被 PWA workbox precache（`globPatterns` 含 webp）。无需改 PWA 配置。

---

## UI 设计

`src/components/SignCard.astro` —— 信息全部平铺、不折叠：

```
┌─────────────────────────────────┐
│  [真实照片 4:3 object-cover]     │
│                                  │
│  © 作者 · 协议 (链回 Commons)    │
├─────────────────────────────────┤
│  Прилёт              (Cyrillic) │
│  UZ Kelish · Келиш   (UZ 双显)  │
│  PRI-lyot            (拼音)     │
│  到达 / 抵港          (中)       │
│  (字面：动词 прилететь 的名词)   │
├─────────────────────────────────┤
│  何时看到：机场出关方向...        │
│  当地注：塔什干 TAS 通常三语...  │
└─────────────────────────────────┘
```

布局：`grid gap-4 md:grid-cols-2`，手机一列、桌面两列。

---

## License 合规

- 所有图片来自 Wikimedia Commons，授权为 CC0 / Public Domain / CC-BY / CC-BY-SA
- 每张图必须在卡面**可见**显示 author + 协议名
- attribution 元素链回原图页 (Commons File: 页)，方便核验

CC-BY-SA 的传染性 (ShareAlike) 只约束**该图的衍生作品**——网页嵌入并标 attribution 不构成衍生，整站可继续保留默认许可。

---

## 已知缺口 & v1.1 计划

- **AIRPORT**：Wikimedia 上 TAS 机场内部指示牌照片稀缺，主要是停机坪 / 飞机 / 外景。用户 8 月到塔什干后实拍：登机口、行李提取、海关、出租车上客点
- **PUBLIC**：v1 全是「药店 (Аптека)」变体——Wikimedia 上 ВЫХОД / Не курить / Туалет / 警察 / 应急标识基本没有合规照片。期望 v1.1 补 5 张：地铁 ВЫХОД、街头禁烟、WC、街头警察岗亭、消防出口
- **MARKET**：Chorsu Bazaar 之外的小型超市（如 Korzinka, Havas 连锁）没在 Wikimedia 上找到合规照——也是 v1.1 实地补拍候选

---

## 维护

```bash
# 重新抓候选图（如需扩内容）
python3 scripts/fetch-signs.py

# 修改 SELECTIONS 列表后，重新转 webp + 写 signs.json
python3 scripts/build-signs.py

# 跑 build 验证
npm run build
```

修改 `SELECTIONS` 时：
- `src_rel` 必须指向 `scripts/.signs-staging/<cat>/<slug>/img_NN.<ext>`
- 至少有 `ru` 或 `uz_latin` 其中之一（识字目标不可缺）
- `chinese` / `context` 必填
- `local_note` 强烈建议（这是和 Card / UzbekCard 一致的"乌兹别克斯坦本地视角"）

8 月实地补拍图入库的流程：
1. 用 iPhone 拍 jpg → 邮件给自己 / iCloud → 落地到 macOS `/tmp/`
2. 创建 `scripts/.signs-staging/_user_field/` 把图放进去
3. 在 `SELECTIONS` 加新条目，`src_rel = "scripts/.signs-staging/_user_field/foo.jpg"`
4. attribution.author = "用户本人现场实拍"，license = "© personal"
5. 重跑 build-signs.py

> 自拍图的 attribution 处理略简单——personal 版权可以自己定，不必走 CC 流程。
