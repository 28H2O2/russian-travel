// 功能：把 IndexedDB 里的 SRS 进度导出为 JSON 文件 / 从 JSON 文件导入回 IndexedDB
// 输入：浏览器环境下被 src/pages/data.astro 调用
// 输出：触发浏览器下载（导出）或返回导入统计（导入）
// 依赖：./db, ./srs
// 在项目中的作用：用户的逃生口——换机、清缓存、备份、跨设备同步全靠它

import {
  getAllProgress,
  bulkPutProgress,
  replaceAllProgress,
  getMeta,
  setMeta,
  META_KEYS,
} from './db';
import type { CardProgress } from './srs';

/** 当前导出格式版本。改 schema 时升号、并在 importProgress 里做迁移 */
const BUNDLE_VERSION = 1;

const APP_NAME = 'russian-travel';

export interface ProgressBundle {
  /** 标识，便于人类肉眼识别这是本项目的导出文件 */
  app: typeof APP_NAME;
  /** 文件格式版本 */
  schema_version: number;
  /** 导出时间戳（ms） */
  exported_at: number;
  /** 导出时这台设备记录的卡片进度数 */
  card_count: number;
  /** 全部 progress 记录 */
  progress: CardProgress[];
  /** meta KV 快照（installed_at / last_session_at / daily_new_count 等） */
  meta: Record<string, unknown>;
}

/* ============================================================ */
/* 导出                                                          */
/* ============================================================ */

export async function buildBundle(now: number = Date.now()): Promise<ProgressBundle> {
  const progress = await getAllProgress();
  const meta: Record<string, unknown> = {};
  for (const key of Object.values(META_KEYS)) {
    const v = await getMeta(key);
    if (v !== undefined) meta[key] = v;
  }
  return {
    app: APP_NAME,
    schema_version: BUNDLE_VERSION,
    exported_at: now,
    card_count: progress.length,
    progress,
    meta,
  };
}

/**
 * 触发浏览器下载一个 .json 文件。
 * 文件名形如 russian-travel-progress-2026-08-15.json
 */
export async function exportAndDownload(): Promise<ProgressBundle> {
  const bundle = await buildBundle();
  const blob = new Blob([JSON.stringify(bundle, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const dateStr = new Date(bundle.exported_at).toISOString().slice(0, 10);
  a.download = `${APP_NAME}-progress-${dateStr}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  return bundle;
}

/* ============================================================ */
/* 导入                                                          */
/* ============================================================ */

export type ImportMode = 'replace' | 'merge';

export interface ImportResult {
  imported: number;
  skipped: number;
  mode: ImportMode;
  source_exported_at: number;
}

export class ImportError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ImportError';
  }
}

/** 简单校验进入的对象长得是不是 ProgressBundle */
function validateBundle(obj: unknown): asserts obj is ProgressBundle {
  if (!obj || typeof obj !== 'object') {
    throw new ImportError('文件不是 JSON 对象');
  }
  const b = obj as Partial<ProgressBundle>;
  if (b.app !== APP_NAME) {
    throw new ImportError(`不是 ${APP_NAME} 的导出文件（app="${b.app}"）`);
  }
  if (typeof b.schema_version !== 'number') {
    throw new ImportError('缺少 schema_version');
  }
  if (b.schema_version > BUNDLE_VERSION) {
    throw new ImportError(
      `文件版本 ${b.schema_version} 高于当前应用支持的 ${BUNDLE_VERSION}。请升级应用后重试。`,
    );
  }
  if (!Array.isArray(b.progress)) {
    throw new ImportError('progress 不是数组');
  }
}

/** 校验单条 progress 记录字段齐备 */
function isValidProgress(p: unknown): p is CardProgress {
  if (!p || typeof p !== 'object') return false;
  const x = p as CardProgress;
  return (
    typeof x.card_id === 'string' &&
    typeof x.ease_factor === 'number' &&
    typeof x.interval_days === 'number' &&
    typeof x.repetitions === 'number' &&
    typeof x.due === 'number' &&
    typeof x.lapses === 'number' &&
    typeof x.total_reviews === 'number'
  );
}

/**
 * 导入一个 JSON 字符串。
 * mode='replace'：原子地清空 + 写入（单个 IDB 事务，失败回滚）
 * mode='merge'：按 last_reviewed 取较新；incoming 较旧或并列则跳过
 *
 * 返回 imported = 实际写入条数；skipped = 校验失败 + 合并失败 之和。
 */
export async function importProgress(jsonText: string, mode: ImportMode): Promise<ImportResult> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(jsonText);
  } catch (e) {
    throw new ImportError('JSON 解析失败：' + (e as Error).message);
  }
  validateBundle(parsed);
  const bundle = parsed;

  // 第一道筛：schema 校验
  const valid: CardProgress[] = [];
  let validationSkipped = 0;
  for (const p of bundle.progress) {
    if (isValidProgress(p)) valid.push(p);
    else validationSkipped += 1;
  }

  let toWriteCount: number;
  let mergeSkipped = 0;

  if (mode === 'replace') {
    // 单 tx 原子替换；失败 IDB 自动 abort、原数据保留
    await replaceAllProgress(valid);
    toWriteCount = valid.length;
  } else {
    // merge：incoming 比本地新才写
    const existing = await getAllProgress();
    const byId = new Map(existing.map((e) => [e.card_id, e]));
    const toWrite: CardProgress[] = [];
    for (const incoming of valid) {
      const local = byId.get(incoming.card_id);
      if (!local) {
        toWrite.push(incoming);
      } else {
        const localTs = local.last_reviewed ?? 0;
        const incomingTs = incoming.last_reviewed ?? 0;
        if (incomingTs > localTs) toWrite.push(incoming);
        else mergeSkipped += 1;
      }
    }
    await bulkPutProgress(toWrite);
    toWriteCount = toWrite.length;
  }

  // 恢复 meta：installed_at 始终保留本机；其它字段按时间戳取较新
  // （旧 bundle merge 进新机时，避免把 last_session_at 倒退）
  if (bundle.meta && typeof bundle.meta === 'object') {
    for (const [k, v] of Object.entries(bundle.meta)) {
      if (k === META_KEYS.installedAt) continue;
      if (mode === 'merge') {
        // 数字类时间戳取较新
        const localV = await getMeta(k);
        if (typeof v === 'number' && typeof localV === 'number' && localV >= v) {
          continue; // 本地更新，跳过
        }
      }
      await setMeta(k, v);
    }
  }

  return {
    imported: toWriteCount,
    skipped: validationSkipped + mergeSkipped,
    mode,
    source_exported_at: bundle.exported_at,
  };
}
