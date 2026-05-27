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

/* ============================================================ */
/* Sign 路牌识字卡片 schema —— 独立于 Card / UzbekCard           */
/* ============================================================ */

/**
 * 路牌识字卡片。
 *
 * 与 Card 的差异：
 *   - 不是用来「说」的，是用来「认」的——被动识别任务
 *   - 主信息是图（真实招牌照片），不是 audio
 *   - 必须有完整 attribution（CC-BY/CC-BY-SA 强制要求显示作者 / 协议）
 *   - 不进 SRS（不同认知任务，复习曲线会怪）
 *   - 一张招牌可能同时含俄语 + 乌兹别克语，所以 ru/uz_latin/uz_cyrillic 都可选
 */
export type SignCategory = 'airport' | 'street' | 'market' | 'restaurant' | 'public';

export interface SignAttribution {
  /** 作者署名，如 'Francisco Anzola' 或 'User:Bobyrr' */
  author: string;
  /** 该图在 Commons / Flickr 的原始页面 URL */
  source_url: string;
  /** 协议名，如 'CC-BY-SA-4.0' / 'CC-BY-2.0' / 'Public Domain' */
  license: string;
  /** 来源平台，如 'Wikimedia Commons' / 'Flickr' */
  via?: string;
}

export interface Sign {
  /** 'airport.arrivals' 等 */
  id: string;
  category: SignCategory;

  image: {
    /** '/signs/airport/arrivals.webp' */
    src: string;
    /** 屏幕阅读器 / SEO 用，简短描述招牌内容 */
    alt: string;
    attribution: SignAttribution;
  };

  /** 招牌上实际出现的文字。一张牌可能有多语并存——以下三个字段都可选。
   *  但 ru 与 uz_latin 至少要有其中之一，否则就没有「识字」对象了。 */
  ru?: string;                   // 俄语西里尔，如 'Прилёт'（带重音可选）
  ru_translit?: string;          // 发音式拼音，如 'PRI-lyot'
  uz_latin?: string;             // 乌兹别克语拉丁，如 'Kelish'
  uz_cyrillic?: string;          // 乌兹别克语西里尔，如 'Келиш'

  /** 中文意思——必填 */
  chinese: string;
  /** 字面拆分 / 词源小注（可选） */
  literal?: string;
  /** 哪里会看到、看到了该干嘛 */
  context: string;
  /** 塔什干 / 乌兹别克斯坦本地细节（可选） */
  local_note?: string;
}
