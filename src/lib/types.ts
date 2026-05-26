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
