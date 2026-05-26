// 功能：IndexedDB 薄封装。两个 store：progress（每张卡的 SRS 状态）+ meta（杂项 KV）
// 输入：被 src/lib/progress-export.ts、src/pages/practice.astro 的 <script> 调用
// 输出：所有方法返回 Promise，结果是 CardProgress | undefined | CardProgress[] 等
// 如何运行：仅浏览器侧。不在 Astro frontmatter (server) 中使用。
// 依赖：./srs (CardProgress 类型)
// 在项目中的作用：SRS 进度的持久化层。所有读写都走这里，组件不直碰 IDBOpenDBRequest

import type { CardProgress } from './srs';

/* ============================================================ */
/* 常量                                                          */
/* ============================================================ */

const DB_NAME = 'russian_travel';
const DB_VERSION = 1;

const STORE_PROGRESS = 'progress';
const STORE_META = 'meta';

/** meta store 里使用的固定 key */
export const META_KEYS = {
  schemaVersion: 'schema_version',
  installedAt: 'installed_at',
  lastSessionAt: 'last_session_at',
  dailyNewCount: 'daily_new_count', // { date: 'YYYY-MM-DD', count: number }
} as const;

/* ============================================================ */
/* 连接                                                          */
/* ============================================================ */

let _dbPromise: Promise<IDBDatabase> | null = null;

function isBrowser(): boolean {
  return typeof indexedDB !== 'undefined';
}

/**
 * 单例打开数据库。第一次调用建表。
 * 之后所有读写共用这个 connection。
 */
export function openDb(): Promise<IDBDatabase> {
  if (!isBrowser()) {
    return Promise.reject(new Error('IndexedDB unavailable (non-browser env)'));
  }
  if (_dbPromise) return _dbPromise;

  _dbPromise = new Promise<IDBDatabase>((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);

    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE_PROGRESS)) {
        db.createObjectStore(STORE_PROGRESS, { keyPath: 'card_id' });
      }
      if (!db.objectStoreNames.contains(STORE_META)) {
        db.createObjectStore(STORE_META, { keyPath: 'key' });
      }
    };
    req.onsuccess = () => {
      const db = req.result;
      // 主动处理版本变更（其他 tab 升级时）
      db.onversionchange = () => {
        db.close();
        _dbPromise = null;
      };
      resolve(db);
    };
    req.onerror = () => reject(req.error);
    req.onblocked = () => reject(new Error('IndexedDB open blocked'));
  });

  return _dbPromise;
}

/** 把 IDBRequest 转 Promise */
function promisify<T>(req: IDBRequest<T>): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

/** 把 IDBTransaction 的 oncomplete 包成 Promise（写完才 resolve） */
function commit(tx: IDBTransaction): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error ?? new Error('Transaction aborted'));
  });
}

/* ============================================================ */
/* progress store                                                */
/* ============================================================ */

export async function getProgress(card_id: string): Promise<CardProgress | undefined> {
  const db = await openDb();
  const tx = db.transaction(STORE_PROGRESS, 'readonly');
  const result = await promisify<CardProgress | undefined>(
    tx.objectStore(STORE_PROGRESS).get(card_id) as IDBRequest<CardProgress | undefined>,
  );
  return result;
}

export async function getAllProgress(): Promise<CardProgress[]> {
  const db = await openDb();
  const tx = db.transaction(STORE_PROGRESS, 'readonly');
  return promisify<CardProgress[]>(
    tx.objectStore(STORE_PROGRESS).getAll() as IDBRequest<CardProgress[]>,
  );
}

export async function putProgress(p: CardProgress): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(STORE_PROGRESS, 'readwrite');
  tx.objectStore(STORE_PROGRESS).put(p);
  return commit(tx);
}

export async function bulkPutProgress(items: CardProgress[]): Promise<void> {
  if (items.length === 0) return;
  const db = await openDb();
  const tx = db.transaction(STORE_PROGRESS, 'readwrite');
  const store = tx.objectStore(STORE_PROGRESS);
  for (const item of items) store.put(item);
  return commit(tx);
}

export async function deleteProgress(card_id: string): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(STORE_PROGRESS, 'readwrite');
  tx.objectStore(STORE_PROGRESS).delete(card_id);
  return commit(tx);
}

export async function clearAllProgress(): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(STORE_PROGRESS, 'readwrite');
  tx.objectStore(STORE_PROGRESS).clear();
  return commit(tx);
}

/* ============================================================ */
/* meta store                                                    */
/* ============================================================ */

interface MetaRecord {
  key: string;
  value: unknown;
}

export async function getMeta<T = unknown>(key: string): Promise<T | undefined> {
  const db = await openDb();
  const tx = db.transaction(STORE_META, 'readonly');
  const rec = await promisify<MetaRecord | undefined>(
    tx.objectStore(STORE_META).get(key) as IDBRequest<MetaRecord | undefined>,
  );
  return rec?.value as T | undefined;
}

export async function setMeta(key: string, value: unknown): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(STORE_META, 'readwrite');
  tx.objectStore(STORE_META).put({ key, value });
  return commit(tx);
}

export async function clearAllMeta(): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(STORE_META, 'readwrite');
  tx.objectStore(STORE_META).clear();
  return commit(tx);
}

/* ============================================================ */
/* 高层辅助                                                      */
/* ============================================================ */

/**
 * 第一次启动时记录 installed_at；之后调用是 no-op。
 * 在 practice 页和 data 页都可以放心调用。
 */
export async function ensureInstalled(now: number = Date.now()): Promise<void> {
  if (!isBrowser()) return;
  const existing = await getMeta<number>(META_KEYS.installedAt);
  if (!existing) await setMeta(META_KEYS.installedAt, now);
}

/**
 * 整库清空（progress + meta）。用于"重置全部进度"或导入前的 replace 模式。
 */
export async function wipeEverything(): Promise<void> {
  await clearAllProgress();
  await clearAllMeta();
}
