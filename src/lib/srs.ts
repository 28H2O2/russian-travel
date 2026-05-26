// 功能：SM-2 间隔重复算法（Anki 同源），纯函数、零外部依赖
// 输入：CardProgress 状态 + 用户评分 grade ('again'|'good'|'easy')
// 输出：新的 CardProgress 状态（含下次到期时间）
// 如何运行：被 src/lib/db.ts 与 src/pages/practice.astro import
// 依赖：无
// 在项目中的作用：把"用户评分"翻译成"下次什么时候再考你"——SRS 的灵魂

/* ============================================================ */
/* 类型                                                          */
/* ============================================================ */

/**
 * 用户评分。3 按钮设计——移动端拇指友好，按错代价低。
 *   again: 完全不会 → 短时间内再练
 *   good : 想了想会 → 正常推进间隔
 *   easy : 秒答对   → 加速推进
 *
 * （SM-2 原版用 0-5 共 6 档，对手机太繁琐。这里映射到 q=2/4/5。）
 */
export type Grade = 'again' | 'good' | 'easy';

export interface CardProgress {
  card_id: string;

  /** 难度系数，1.3 ~ 2.5+，越大说明越好记 */
  ease_factor: number;

  /** 上次评分后给的复习间隔（天）。0 = 还没开始学 / 刚 lapse */
  interval_days: number;

  /** 连续答对次数（grade != 'again' 累计） */
  repetitions: number;

  /** 下次到期时间戳（ms）。<= now 即为 "到期" */
  due: number;

  /** 上次复习时间戳，null = 从未练过 */
  last_reviewed: number | null;

  /** 累计 'again' 次数（用于稳定性分析与"难卡"识别） */
  lapses: number;

  /** 累计复习次数（含 again） */
  total_reviews: number;
}

/* ============================================================ */
/* 常量                                                          */
/* ============================================================ */

/** Anki 默认初始 ease */
const INITIAL_EASE = 2.5;

/** ease 不允许低于此值（再低算法发散） */
const MIN_EASE = 1.3;

/** 'again' 后的"短期再练"间隔。SM-2 原版重置 1 天，Anki 10 分钟。这里取 1 小时，更适合一次性集中练习的旅行者。 */
const LAPSE_RECOVERY_MS = 60 * 60 * 1000;

/** 一天毫秒数 */
const DAY_MS = 24 * 60 * 60 * 1000;

/** 评分映射到 SM-2 的 q 值（0-5）。又称 "答题质量" */
const GRADE_TO_Q: Record<Grade, number> = {
  again: 2, // 想不起来 / 错答
  good: 4, // 正确，需要稍想
  easy: 5, // 秒答
};

/* ============================================================ */
/* 工厂                                                          */
/* ============================================================ */

/** 新建一张未练过的卡片的进度记录 */
export function newCardProgress(card_id: string, now: number = Date.now()): CardProgress {
  return {
    card_id,
    ease_factor: INITIAL_EASE,
    interval_days: 0,
    repetitions: 0,
    due: now, // 新卡默认立即到期（出现在练习队列里）
    last_reviewed: null,
    lapses: 0,
    total_reviews: 0,
  };
}

/* ============================================================ */
/* 评分推进——SM-2 核心                                          */
/* ============================================================ */

/**
 * 应用一次评分，返回新状态。
 *
 * SM-2 算法（简化）：
 *   1) again → 重置 repetitions=0，interval=1h，lapses++
 *      ease_factor 仍然按公式下调
 *   2) good/easy →
 *      repetitions=0: interval=1天
 *      repetitions=1: interval=6天
 *      repetitions>=2: interval *= ease_factor （或 'good' 时用稍弱系数）
 *   3) ease_factor 调整：
 *      new_ef = ef + (0.1 - (5-q) * (0.08 + (5-q)*0.02))
 *      下限 1.3
 */
export function review(
  state: CardProgress,
  grade: Grade,
  now: number = Date.now(),
): CardProgress {
  const q = GRADE_TO_Q[grade];

  // ease_factor 调整公式（SM-2 原版）
  const efDelta = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02);
  const newEase = Math.max(MIN_EASE, state.ease_factor + efDelta);

  let interval_days: number;
  let repetitions: number;
  let due: number;
  let lapses = state.lapses;

  if (grade === 'again') {
    // Lapse：短时间内再来
    repetitions = 0;
    interval_days = 0;
    due = now + LAPSE_RECOVERY_MS;
    lapses += 1;
  } else {
    repetitions = state.repetitions + 1;
    if (state.repetitions === 0) {
      interval_days = 1;
    } else if (state.repetitions === 1) {
      interval_days = 6;
    } else {
      // 'good' 比 'easy' 推进得慢一点——这是 Anki 的做法
      const multiplier = grade === 'easy' ? newEase + 0.15 : newEase;
      interval_days = Math.max(1, Math.round(state.interval_days * multiplier));
    }
    due = now + interval_days * DAY_MS;
  }

  return {
    ...state,
    ease_factor: newEase,
    interval_days,
    repetitions,
    due,
    last_reviewed: now,
    lapses,
    total_reviews: state.total_reviews + 1,
  };
}

/* ============================================================ */
/* 查询辅助                                                      */
/* ============================================================ */

/** 是否到期（应进入今日队列） */
export function isDue(state: CardProgress, now: number = Date.now()): boolean {
  return state.due <= now;
}

/** 是否新卡（从未学过） */
export function isNew(state: CardProgress): boolean {
  return state.total_reviews === 0;
}

/** 是否"成熟"（连续答对足够多次、间隔足够长） */
export function isMature(state: CardProgress): boolean {
  return state.repetitions >= 3 && state.interval_days >= 21;
}

/** 距下次到期的人类可读字符串，例 "30 分钟后" / "明天" / "3 天后" */
export function dueLabel(state: CardProgress, now: number = Date.now()): string {
  const diff = state.due - now;
  if (diff <= 0) return '现在';
  const mins = Math.round(diff / (60 * 1000));
  if (mins < 60) return `${mins} 分钟后`;
  const hours = Math.round(diff / (60 * 60 * 1000));
  if (hours < 24) return `${hours} 小时后`;
  const days = Math.round(diff / DAY_MS);
  if (days === 1) return '明天';
  if (days < 30) return `${days} 天后`;
  const months = Math.round(days / 30);
  return `${months} 个月后`;
}

/* ============================================================ */
/* 队列调度                                                      */
/* ============================================================ */

export interface QueueStats {
  due: number; // 到期复习（学习中、due <= now）
  new: number; // 新卡（从未学过）
  later: number; // 学习中但未到期
  mature: number; // 已掌握（含未到期与到期）
  total: number; // 全部卡数
}

/**
 * 把进度记录数组分桶。card_ids 是 cards.json 里所有卡的 id 列表。
 * 没有 progress 记录的卡视为"新卡"。
 */
export function bucketize(
  card_ids: string[],
  progress: CardProgress[],
  now: number = Date.now(),
): QueueStats {
  const byId = new Map(progress.map((p) => [p.card_id, p]));
  let due = 0;
  let neu = 0;
  let later = 0;
  let mature = 0;
  for (const id of card_ids) {
    const p = byId.get(id);
    if (!p || isNew(p)) {
      neu += 1;
      continue;
    }
    if (isMature(p)) mature += 1;
    if (isDue(p, now)) due += 1;
    else later += 1;
  }
  return { due, new: neu, later, mature, total: card_ids.length };
}

/**
 * 给定全部 card_ids 与进度，生成今日练习队列（按优先级排序的 card_id 数组）：
 *   1. 学习中、已到期（先来）—— 按 due 升序，越早到期越优先
 *   2. 新卡 —— 按 priority callback 给的顺序（通常 essential + tier）
 *
 * dailyNewLimit 限制每日新卡数量，避免一次"翻新"太狠。
 */
export function buildQueue(
  card_ids: string[],
  progress: CardProgress[],
  options: {
    now?: number;
    dailyNewLimit?: number;
    newOrderPriority?: (card_id: string) => number;
  } = {},
): string[] {
  const now = options.now ?? Date.now();
  const limit = options.dailyNewLimit ?? 20;
  const priorityOf = options.newOrderPriority ?? (() => 0);

  const byId = new Map(progress.map((p) => [p.card_id, p]));

  const dueList: { id: string; due: number }[] = [];
  const newList: { id: string; priority: number }[] = [];

  for (const id of card_ids) {
    const p = byId.get(id);
    if (!p || isNew(p)) {
      newList.push({ id, priority: priorityOf(id) });
    } else if (isDue(p, now)) {
      dueList.push({ id, due: p.due });
    }
  }

  dueList.sort((a, b) => a.due - b.due);
  newList.sort((a, b) => a.priority - b.priority);

  return [...dueList.map((d) => d.id), ...newList.slice(0, limit).map((n) => n.id)];
}
