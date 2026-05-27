#!/usr/bin/env python3
"""
功能：用 Microsoft Edge Neural TTS 给 uzbek.json 中所有卡片生成乌兹别克语发音
输入：src/data/uzbek.json
输出：public/audio/uzbek/uzbek_NNNN_{normal|slow}.mp3
如何运行：
    uv run --with edge-tts scripts/generate-tts-uzbek.py
依赖：edge-tts (>= 7.x)、uzbek.json
在项目中的作用：彩蛋页 /uzbek 的音频流水线，与 generate-tts.py 区别在 voice
            （uz-UZ-MadinaNeural 而非 ru-RU-SvetlanaNeural）和输入文件。
            SKIP_EXISTING=True，增量补卡时只跑缺的。
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

ROOT = Path(__file__).resolve().parent.parent
UZBEK_PATH = ROOT / "src" / "data" / "uzbek.json"
PUBLIC_DIR = ROOT / "public"

VOICE = "uz-UZ-MadinaNeural"     # 女声、与俄语 Svetlana 对齐
RATE_NORMAL = "+0%"
RATE_SLOW = "-30%"
CONCURRENCY = 4
SKIP_EXISTING = True


async def synthesize(text: str, voice: str, rate: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(out_path))


def rel_to_abs(rel: str) -> Path:
    return PUBLIC_DIR / rel.lstrip("/")


async def main() -> int:
    cards = json.loads(UZBEK_PATH.read_text(encoding="utf-8"))
    sem = asyncio.Semaphore(CONCURRENCY)
    total = len(cards) * 2
    completed = 0
    skipped = 0

    async def one(text: str, out: Path, rate: str, label: str) -> None:
        nonlocal completed
        if SKIP_EXISTING and out.exists() and out.stat().st_size > 0:
            return
        async with sem:
            try:
                await synthesize(text, VOICE, rate, out)
                completed += 1
                print(f"  [{completed:>3}] {label}  {out.name}")
            except Exception as exc:  # noqa: BLE001
                print(f"  ✗ FAIL {out.name}: {exc}", file=sys.stderr)

    tasks: list[asyncio.Task[None]] = []
    for card in cards:
        text = card["latin"]
        normal_out = rel_to_abs(card["audio"]["phrase_normal"])
        slow_out = rel_to_abs(card["audio"]["phrase_slow"])
        if SKIP_EXISTING:
            if normal_out.exists() and normal_out.stat().st_size > 0:
                skipped += 1
            if slow_out.exists() and slow_out.stat().st_size > 0:
                skipped += 1
        tasks.append(asyncio.create_task(one(text, normal_out, RATE_NORMAL, "normal")))
        tasks.append(asyncio.create_task(one(text, slow_out, RATE_SLOW, "slow  ")))

    print(f"生成 {total} 个乌兹别克语 TTS（voice={VOICE}, 并发={CONCURRENCY}, skip_existing={SKIP_EXISTING}）")
    if SKIP_EXISTING:
        print(f"  其中 {skipped} 个已存在、将跳过；实际需要合成 {total - skipped} 个")
    await asyncio.gather(*tasks)
    print(f"\n完成。新合成 {completed} 个 mp3（跳过 {skipped} 个）写入 public/audio/uzbek/")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
