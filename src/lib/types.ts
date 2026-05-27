// 功能：cards.json / scenes.json 的 TypeScript 类型定义
// 输入：被 src/lib/data.ts 与所有组件 import
// 输出：导出 Card / Scene / Politeness / Response / Slot 等类型
// 依赖：无外部依赖
// 在项目中的作用：让 IDE 与 astro check 在数据进入组件之前就报错

export type Politeness = 'Вы' | 'ты' | 'neutral';

export type Tier = 1 | 2 | 3;

export type VerificationStatus =
  | 'ai_generated_unreviewed'
  | 'verified'
  | 'wrong'
  | 'native_reviewed';

export interface ResponseEntry {
  cyrillic: string;
  trans: string;
  cn: string;
}

export interface SlotEntry {
  label: string;
  swap: string;
  trans: string;
}

export interface CardAudio {
  phrase_normal: string;
  phrase_slow: string;
}

export interface Card {
  id: string;
  scene: string;
  is_essential: boolean;
  tier: Tier;

  cyrillic: string;
  transliteration: string;
  chinese: string;
  literal: string;

  audio: CardAudio;

  politeness: Politeness;
  register_note: string;

  likely_responses: ResponseEntry[];
  slots: SlotEntry[];

  local_note: string;
  verification_status: VerificationStatus;
}

export type SceneId =
  | 'essentials'
  | 'money'
  | 'transport'
  | 'food'
  | 'lodging'
  | 'shopping'
  | 'emergency'
  | 'chat';

export type ColorToken = SceneId | 'uzbek';

export interface Scene {
  id: SceneId;
  name_zh: string;
  name_en: string;
  name_ru: string;
  color_token: ColorToken;
  order: number;
  v1_target: number;
  v2_target: number;
  icon: string;
  blurb: string;
}

/* ============================================================ */
/* Uzbek 彩蛋卡片 schema —— 独立于 Card                          */
/* ============================================================ */

/**
 * 乌兹别克语彩蛋卡片。
 * 与 Russian Card 的差异：
 *   - latin 字段（乌兹别克语 1995 年起官方拉丁字母）
 *   - 没有 likely_responses / slots（这不是对话，只是单点礼貌包）
 *   - 没有 verification_status / SRS 字段（不进 /practice 队列）
 *   - 关键字段是 why_uzbek：为什么放着俄语不说要说乌兹别克语
 */
export type UzbekCategory = 'greeting' | 'thanks' | 'food' | 'bazaar';

export interface UzbekCard {
  id: string;                    // 'uzbek.<category>.<short>'
  category: UzbekCategory;
  latin: string;                 // 'Salom!' — 1995 起的官方拉丁字母
  cyrillic: string;              // 'Салом!' — 苏联沿用至今的西里尔字母，
                                 //   街头招牌 / 老一辈 / 宗教场合常见。
                                 //   双显设计：拉丁主、西里尔副。
  pronunciation: string;         // 'sa-LOM' — 发音式拉丁化（大写=重音）
  chinese: string;
  russian_equivalent?: string;   // 对应俄语句（可空——有些更直接表达没俄语对应）
  audio: {
    phrase_normal: string;
    phrase_slow: string;
  };
  context: string;               // 何时 / 对谁 / 什么场景用
  why_uzbek: string;             // ★ 彩蛋专属——用这句而非俄语的效果
}
