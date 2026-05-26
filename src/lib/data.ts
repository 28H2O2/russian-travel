// 功能：加载 cards.json / scenes.json 并提供查询辅助
// 输入：src/data/cards.json + src/data/scenes.json
// 输出：getScenes / getCards / getCardsByScene / getEssentialCards
// 依赖：./types
// 在项目中的作用：唯一的数据访问层。组件只通过这里读数据，不直接 import JSON。

import cardsJson from '../data/cards.json';
import scenesJson from '../data/scenes.json';
import type { Card, Scene, SceneId } from './types';

const cards = cardsJson as Card[];
const scenes = (scenesJson as Scene[]).sort((a, b) => a.order - b.order);

export function getScenes(): Scene[] {
  return scenes;
}

export function getScene(id: SceneId): Scene | undefined {
  return scenes.find((s) => s.id === id);
}

export function getCards(): Card[] {
  return cards;
}

export function getCardsByScene(sceneId: SceneId): Card[] {
  return cards.filter((c) => c.scene === sceneId);
}

export function getEssentialCards(limit = 10): Card[] {
  return cards
    .filter((c) => c.is_essential)
    .sort((a, b) => a.tier - b.tier)
    .slice(0, limit);
}

export function countByScene(sceneId: SceneId): number {
  return cards.filter((c) => c.scene === sceneId).length;
}
