# Card Schema · 卡片数据契约

`src/data/cards.json` 是一个 `Card[]`。每张卡的字段如下。**这份契约就是真理；当代码与数据冲突时，改代码不改数据。**

## TypeScript 类型

```ts
type Politeness = 'Вы' | 'ты' | 'neutral';
type Tier = 1 | 2 | 3;
type VerificationStatus =
  | 'ai_generated_unreviewed'
  | 'verified'
  | 'wrong'
  | 'native_reviewed';

interface Card {
  id: string;                    // 见下面 ID 约定
  scene: SceneId;                // 8 场景之一
  is_essential: boolean;         // 是否进顶部"必备卡"便捷柜
  tier: Tier;                    // 1=必背 50, 2=次重要 100, 3=锦上添花

  cyrillic: string;              // 含重音标记的西里尔字母
  transliteration: string;       // 发音式拉丁化（不是 BGN/PCGN！）
  chinese: string;               // 中文翻译
  literal: string;               // 字面直译，让用户看见结构

  audio: {
    phrase_normal: string;       // /audio/<scene>/<id>_normal.mp3
    phrase_slow: string;         // /audio/<scene>/<id>_slow.mp3
  };

  politeness: Politeness;
  register_note: string;         // 一句话说明何时/对谁用

  likely_responses: {
    cyrillic: string;
    trans: string;
    cn: string;
  }[];                           // ★ 不能是空数组！本项目核心创新字段

  slots: {
    label: string;               // 中文：替换槽含义
    swap: string;                // 俄语：可直接替换进句子的形式（已变好格）
    trans: string;
  }[];                           // 可以是空数组

  local_note: string;            // Uzbekistan-specific 备注，可空
  verification_status: VerificationStatus;
}
```

## ID 约定

```
<scene>.<subcategory>.<short_key>
```

例：
- `essentials.greeting.hello_formal`
- `transport.taxi.how_much_to_center`
- `food.diet.no_meat`

`<short_key>` 用 snake_case 英文、表意，长度 ≤ 25 字符。`audio` 路径里也用这个 id（去掉 `<scene>.` 前缀、转成 4 位流水号——见 scripts/）。

## 重音标记

- 必须使用 Unicode combining acute accent (U+0301) 标在元音后
- 单音节词不标
- 例：`Ско́лько`（"о" 之后跟 U+0301）

测试方法：`echo -n 'Ско́лько' | wc -c` 应该是 14 字节（普通 6 字符 "Сколько" 是 13 字节，多 1 字节即是 combining mark）。

## 发音式拉丁音译规则

**目的：让你嘴上念出来的就是俄语母语者听得懂的。**

| 规则 | 例 |
|---|---|
| 重音音节用大写 | `SKOL'-ka`（重音在 SKOL） |
| 无重音的 `о` → `a` | `молоко́` → `ma-la-KO`（不是 `mo-lo-KO`） |
| 无重音的 `е/я` → `i`/`ye-ya` 中性 | `язы́к` → `ya-ZYK` |
| 软音符 `ь` → `'` | `Сколько` → `SKOL'-ka` |
| 颚化 `ч/ш/щ/ж` → `ch/sh/shch/zh` | `чай` → `chay` |
| 用连字符分音节 | `SKOL'-ka da TSEN-tra` |
| 不用 IPA、不用 BGN/PCGN | 这套是为说话者定制、不是为图书馆员 |

## 礼貌等级 (politeness)

- `Вы` — 客气/正式（对陌生人、店员、司机、长辈默认）
- `ты` — 亲昵（朋友、孩子；旅游场景几乎用不到）
- `neutral` — 句子里没有人称代词，无需标

旅游场景：**一律 Вы，除非有明确反例**。

## likely_responses 字段（核心创新）

**为什么重要**：你能说出去不算赢，你能听懂对面那句才算赢。

每张卡至少 1 条、推荐 2-3 条。每条要：
- 俄语母语者真实可能说出的话（**LLM 容易出现"教科书式"假回答**，写时刻意避免）
- 简短（1-5 词），不要罗列整段
- 中文翻译保留语气（如 "По счётчику" = "按表跳"，不是 "according to the meter"）

## slots 字段

可替换槽——展示这张卡的"句型"特性。每个槽里 `swap` 字段必须给的是 **可以直接替换进句子的形式**（介词后是属格 / 与格等已经变好），不是字典原型。

例：`Сколько до центра?` 的 slot
- ✅ `до вокза́ла` (vokzal 属格)
- ❌ `вокза́л`（主格，替进去语法错）

## local_note 字段

Uzbekistan-specific 备注。可以包含：
- 当地货币 / 价格区间（"约 1700 苏姆"）
- 当地常见替代物 / 文化差异（"乌兹别克菜没有猪肉"）
- 当地工具或服务（"Yandex Go 比街边出租透明"）
- 风险提示（"街边野鸡换钱点不要碰"）

**不要写**：纯学术语言学注释、对其他俄语国家的对比（除非对乌兹别克斯坦特别相关）。

## verification_status 字段

- `ai_generated_unreviewed` — LLM 生成、未经母语者审校（v1 全部）
- `verified` — 用户在乌兹别克斯坦现场用过、确认有效
- `wrong` — 用户在现场发现是错的、需要重写
- `native_reviewed` — 俄语母语者审校通过

**永远不要**在没有真实审校的情况下把卡片标成 `verified` 或 `native_reviewed`。
