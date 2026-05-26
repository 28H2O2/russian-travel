#!/usr/bin/env bash
# 功能：为 cards.json 中所有卡片生成静音 mp3 占位文件
# 输入：src/data/cards.json (读取 audio.phrase_normal / audio.phrase_slow 路径)
# 输出：public/audio/<scene>/*.mp3 (~3KB 的静音 mp3)
# 如何运行：bash scripts/generate-silent-stubs.sh
# 依赖：ffmpeg、jq
# 在项目中的作用：W1 阶段让 AudioButton 有可播放的目标文件；W2 用 Yandex TTS 替换

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null; then
  echo "需要 ffmpeg"; exit 1
fi
if ! command -v jq >/dev/null; then
  echo "需要 jq"; exit 1
fi

TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

# W1 临时方案：normal = 0.5s 440Hz 嘀声；slow = 0.6s 330Hz 嘀声
# 用 sine 而不是静音，让用户点击按钮时能听到"嘀"——证明 audio pipeline 通了。
# W2 用 Yandex SpeechKit 真生成俄语发音替换。
ffmpeg -y -loglevel error \
  -f lavfi -i "sine=frequency=440:duration=0.5:sample_rate=22050" \
  -af "afade=t=in:st=0:d=0.05,afade=t=out:st=0.45:d=0.05,volume=0.4" \
  -q:a 9 -acodec libmp3lame \
  "$TMP/beep_normal.mp3"

ffmpeg -y -loglevel error \
  -f lavfi -i "sine=frequency=330:duration=0.6:sample_rate=22050" \
  -af "afade=t=in:st=0:d=0.05,afade=t=out:st=0.55:d=0.05,volume=0.4" \
  -q:a 9 -acodec libmp3lame \
  "$TMP/beep_slow.mp3"

count=0
# 从 cards.json 抽出所有音频路径，去重；用 while-read 兼容 macOS 系统 bash 3.x
while IFS= read -r rel; do
  # rel 形如 /audio/transport/transport_0001_normal.mp3
  target="public${rel}"
  mkdir -p "$(dirname "$target")"
  if [[ "$rel" == *_slow.mp3 ]]; then
    cp "$TMP/beep_slow.mp3" "$target"
  else
    cp "$TMP/beep_normal.mp3" "$target"
  fi
  count=$((count + 1))
done < <(jq -r '.[] | .audio.phrase_normal, .audio.phrase_slow' src/data/cards.json | sort -u)

echo "生成 $count 个嘀声占位 mp3 到 public/audio/ (normal=440Hz, slow=330Hz)"
