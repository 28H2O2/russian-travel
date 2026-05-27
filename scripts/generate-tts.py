#!/usr/bin/env python3
"""
功能：用 Microsoft Edge Neural TTS 给 cards.json 中所有卡片生成俄语发音
输入：src/data/cards.json（按 cards[].audio.phrase_normal / phrase_slow 的路径写文件）
输出：public/audio/<scene>/<scene>_NNNN_{normal|slow}.mp3
如何运行：
    uv run --with edge-tts scripts/generate-tts.py
    # 或假设 edge-tts 已通过 uv tool install 装好：
    python3 scripts/generate-tts.py
依赖：edge-tts (>= 7.x)、cards.json
在项目中的作用：v1 起所有 mp3 的主流水线。SKIP_EXISTING=True，增量补卡时只跑缺的；
            失败的 mp3（< 100 字节）建议 `find public/audio -name '*.mp3' -size -100c -delete`
            后再跑一次让它自动补齐。
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
SKIP_EXISTING = True             # mp3 已存在则不重新合成（增量补卡时省时省钱）

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

    skipped = 0

    async def one(text: str, out: Path, rate: str, label: str) -> None:
        nonlocal completed
        if SKIP_EXISTING and out.exists() and out.stat().st_size > 0:
            return  # 已存在的 mp3 跳过，留给增量补卡用
        async with sem:
            try:
                await synthesize(text, VOICE, rate, out)
                completed += 1
                print(f"  [{completed:>3}] {label}  {out.name}")
            except Exception as exc:  # noqa: BLE001
                print(f"  ✗ FAIL {out.name}: {exc}", file=sys.stderr)

    tasks: list[asyncio.Task[None]] = []
    for card in cards:
        text = card["cyrillic"]
        normal_out = rel_to_abs(card["audio"]["phrase_normal"])
        slow_out = rel_to_abs(card["audio"]["phrase_slow"])
        # 预先统计跳过数量（不入任务队列，print 才显示完整概况）
        if SKIP_EXISTING:
            if normal_out.exists() and normal_out.stat().st_size > 0:
                skipped += 1
            if slow_out.exists() and slow_out.stat().st_size > 0:
                skipped += 1
        tasks.append(asyncio.create_task(one(text, normal_out, RATE_NORMAL, "normal")))
        tasks.append(asyncio.create_task(one(text, slow_out, RATE_SLOW, "slow  ")))

    print(f"生成 {total} 个俄语 TTS（voice={VOICE}, 并发={CONCURRENCY}, skip_existing={SKIP_EXISTING}）")
    if SKIP_EXISTING:
        print(f"  其中 {skipped} 个已存在、将跳过；实际需要合成 {total - skipped} 个")
    await asyncio.gather(*tasks)
    print(f"\n完成。新合成 {completed} 个 mp3（跳过 {skipped} 个）写入 public/audio/")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
