#!/usr/bin/env python3
"""
功能：用 Microsoft Edge Neural TTS 给 cards.json 中所有卡片生成俄语发音
输入：src/data/cards.json
输出：public/audio/<scene>/<id>_normal.mp3 + _slow.mp3
如何运行：
    uv run --with edge-tts scripts/generate-tts.py
    # 或假设 edge-tts 已通过 uv tool install 装好：
    python3 scripts/generate-tts.py
依赖：edge-tts (>= 7.x)、cards.json
在项目中的作用：W2 起取代 generate-silent-stubs.sh 的"嘀"声，提供真发音
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("缺少 edge-tts。运行: uv tool install edge-tts  或  pip install edge-tts", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------- 配置
ROOT = Path(__file__).resolve().parent.parent
CARDS_PATH = ROOT / "src" / "data" / "cards.json"
PUBLIC_DIR = ROOT / "public"

VOICE = "ru-RU-SvetlanaNeural"   # 女声、友好正向，旅游场景最自然
RATE_NORMAL = "+0%"
RATE_SLOW = "-30%"               # 慢档放慢 30% 便于跟读
CONCURRENCY = 8                  # 同时跑 8 个 TTS 任务

# ---------------------------------------------------------------- 工具


async def synthesize(text: str, voice: str, rate: str, out_path: Path) -> None:
    """单次合成。写入 out_path（mp3）。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(out_path))


def rel_to_abs(rel: str) -> Path:
    """cards.json 里的 /audio/x.mp3 → public/audio/x.mp3"""
    return PUBLIC_DIR / rel.lstrip("/")


# ---------------------------------------------------------------- 主流程


async def main() -> int:
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))
    sem = asyncio.Semaphore(CONCURRENCY)
    completed = 0
    total = len(cards) * 2

    async def one(text: str, out: Path, rate: str, label: str) -> None:
        nonlocal completed
        async with sem:
            try:
                await synthesize(text, VOICE, rate, out)
                completed += 1
                print(f"  [{completed:>2}/{total}] {label}  {out.name}")
            except Exception as exc:  # noqa: BLE001
                print(f"  ✗ FAIL {out.name}: {exc}", file=sys.stderr)

    tasks: list[asyncio.Task[None]] = []
    for card in cards:
        text = card["cyrillic"]
        normal_out = rel_to_abs(card["audio"]["phrase_normal"])
        slow_out = rel_to_abs(card["audio"]["phrase_slow"])
        tasks.append(asyncio.create_task(one(text, normal_out, RATE_NORMAL, "normal")))
        tasks.append(asyncio.create_task(one(text, slow_out, RATE_SLOW, "slow  ")))

    print(f"生成 {total} 个俄语 TTS（voice={VOICE}, 并发={CONCURRENCY}）...")
    await asyncio.gather(*tasks)
    print(f"\n完成。{completed}/{total} 个 mp3 写入 public/audio/")
    return 0 if completed == total else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
