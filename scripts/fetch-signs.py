#!/usr/bin/env python3
"""
功能：从 Wikimedia Commons 抓真实路牌候选图（含俄语 / 乌兹别克语招牌）+ 完整 attribution
输入：脚本内 QUERIES 列表（5 类场景，~15 个 query）
输出：
    public/signs/_staging/<query_slug>/img_NN.jpg  ——  候选图（最长边 ~800px）
    public/signs/_staging/_manifest.json          ——  每张图的 attribution / license / source_url / desc
如何运行：
    cd /Users/h2o2/Desktop/Project/Russian_travel
    python3 scripts/fetch-signs.py
依赖：requests （pip install requests）
在项目中的作用：路牌识字 /signs feature 的内容生产 Pipeline 阶段 1。
    抓回来的图是候选——人工挑选阶段会从 _staging/ 中选出 30 张正式入库。
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests


# ---------- 配置 ----------

# Wikimedia Commons API
API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    # Wikimedia 要求 User-Agent 含联系方式（项目页 URL 即可）
    "User-Agent": "RussianTravelSurvivalKit/1.0 (https://russian-travel-tau.vercel.app; "
                  "personal hobby project; respects CC licensing)",
}

# 输出根目录（放在 scripts/ 下而不是 public/ 下——staging 是工作产物，
# 不应进 Astro build 输出。被 .gitignore 排除）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_ROOT / "scripts" / ".signs-staging"

# 每个 query 最多抓多少候选
PER_QUERY_LIMIT = 8

# 缩略图宽度（Wikimedia 服务器端 resize，省带宽）
THUMB_WIDTH = 1000

# 允许的 license 关键字（小写匹配 LicenseShortName）
LICENSE_ALLOWLIST = (
    "cc0",
    "cc-by",
    "cc by",
    "public domain",
    "pd",
)
# 拒绝（即便是 cc-by-* 子串里出现，但若整体含 nc/nd 则拒）
LICENSE_DENYLIST = (
    "nc",   # NonCommercial
    "nd",   # NoDerivatives
    "fair use",
    "fairuse",
)


# 每个 query 带 category 标签——后续人工挑选时按 category 归类
QUERIES: list[tuple[str, str]] = [
    # category, search query
    ("airport",    "Tashkent International Airport"),
    ("airport",    "Tashkent airport interior"),
    ("airport",    "airport sign Cyrillic Russian"),
    ("street",     "Tashkent Metro station"),
    ("street",     "Tashkent street sign"),
    ("street",     "Cyrillic street sign Russian"),
    ("street",     "Tashkent metro entrance"),
    ("market",     "Chorsu Bazaar Tashkent"),
    ("market",     "Tashkent bazaar"),
    ("market",     "Uzbek market signage"),
    ("restaurant", "Tashkent restaurant"),
    ("restaurant", "Uzbek chaikhana"),
    ("restaurant", "Russian restaurant menu sign"),
    ("public",     "Аптека pharmacy sign Russia"),
    ("public",     "Russian no smoking sign Cyrillic"),
    ("public",     "Cyrillic exit sign Выход"),
]


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:48]


def is_license_ok(short_name: str) -> bool:
    """LicenseShortName 是否在允许的 CC / PD 范围内"""
    if not short_name:
        return False
    s = short_name.lower()
    if any(deny in s for deny in LICENSE_DENYLIST):
        return False
    return any(allow in s for allow in LICENSE_ALLOWLIST)


def strip_html(s: Optional[str]) -> str:
    """Wikimedia 返回的 Artist / ImageDescription 字段是 HTML，简单去标签"""
    if not s:
        return ""
    # 去标签
    s = re.sub(r"<[^>]+>", " ", s)
    # 折叠空白
    s = re.sub(r"\s+", " ", s).strip()
    # 解码常见 entities
    s = s.replace("&amp;", "&").replace("&nbsp;", " ").replace("&quot;", '"').replace("&#39;", "'")
    return s[:200]


def search_commons(query: str, limit: int = PER_QUERY_LIMIT) -> list[dict]:
    """
    用 generator=search 搜文件 namespace (6)，附带 imageinfo + extmetadata。
    返回 [{title, url, thumburl, width, height, mime, license, artist, desc, source_url}]
    """
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,            # File:
        "gsrlimit": limit * 2,        # 多抓一些以防 license 过滤后不够
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": THUMB_WIDTH,
        "iiextmetadatafilter": (
            "LicenseShortName|Artist|LicenseUrl|ImageDescription|UsageTerms|Credit"
        ),
    }
    try:
        r = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ! API error for '{query}': {e}")
        return []

    pages = data.get("query", {}).get("pages", {}) or {}
    results: list[dict] = []

    for page in pages.values():
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        meta = info.get("extmetadata", {}) or {}
        title = page.get("title", "")
        license_short = meta.get("LicenseShortName", {}).get("value", "")
        if not is_license_ok(license_short):
            continue
        # 排除非图片（svg、ogg 等可以保留 svg，但 ogg/webm 排除）
        mime = info.get("mime", "")
        if not mime.startswith("image/"):
            continue
        # 限定 jpg/png/webp（避免 tiff / svg 中文字渲染问题）
        if not any(mime.endswith(x) for x in ("jpeg", "png", "webp")):
            continue

        results.append({
            "title": title,
            "thumburl": info.get("thumburl") or info.get("url"),
            "url": info.get("url"),
            "width": info.get("thumbwidth") or info.get("width"),
            "height": info.get("thumbheight") or info.get("height"),
            "mime": mime,
            "license": license_short,
            "license_url": meta.get("LicenseUrl", {}).get("value", ""),
            "artist": strip_html(meta.get("Artist", {}).get("value")),
            "credit": strip_html(meta.get("Credit", {}).get("value")),
            "desc": strip_html(meta.get("ImageDescription", {}).get("value")),
            "usage_terms": meta.get("UsageTerms", {}).get("value", ""),
            "source_url": f"https://commons.wikimedia.org/wiki/{quote(title)}",
        })
        if len(results) >= limit:
            break

    return results


def download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"  ! download failed {url}: {e}")
        return False


def main() -> int:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, list[dict]] = {}  # category → [entries]
    total_kept = 0

    for idx, (category, query) in enumerate(QUERIES, 1):
        slug = slugify(query)
        print(f"[{idx}/{len(QUERIES)}] [{category}] {query!r}")
        results = search_commons(query)
        if not results:
            print(f"  → 0 candidates after license filter")
            continue

        sub_dir = STAGING_DIR / category / slug
        sub_dir.mkdir(parents=True, exist_ok=True)

        kept_for_query: list[dict] = []
        for i, item in enumerate(results, 1):
            # 文件扩展名
            mime = item["mime"]
            ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime, "jpg")
            local = sub_dir / f"img_{i:02d}.{ext}"
            if local.exists():
                pass  # 已下载就跳过
            else:
                if not download(item["thumburl"], local):
                    continue
                time.sleep(0.4)  # 礼貌的限速
            entry = {
                "local_path": str(local.relative_to(PROJECT_ROOT)),
                "category": category,
                "query": query,
                **item,
            }
            kept_for_query.append(entry)
            total_kept += 1

        manifest.setdefault(category, []).extend(kept_for_query)
        print(f"  → kept {len(kept_for_query)} / {len(results)}")

    manifest_path = STAGING_DIR / "_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print()
    print(f"=== Done ===")
    print(f"Total kept: {total_kept}")
    print(f"By category:")
    for cat, entries in sorted(manifest.items()):
        print(f"  {cat:12s}  {len(entries)}")
    print(f"Manifest: {manifest_path.relative_to(PROJECT_ROOT)}")
    print()
    print(f"Next step: 人工浏览 {STAGING_DIR.relative_to(PROJECT_ROOT)}/ ，")
    print(f"           挑出 5 类 × 6 = 30 张最匹配的，转 webp，移到 public/signs/<cat>/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
