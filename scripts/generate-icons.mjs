/**
 * 功能：用 sharp 把 public/favicon.svg 光栅化为 PWA 所需 PNG 图标
 * 输入：public/favicon.svg
 * 输出：public/icon-192.png（Android manifest）
 *      public/icon-512.png（Android splash / install prompt）
 *      public/icon-512-maskable.png（带 safe area padding，适合 Android adaptive icon）
 *      public/apple-touch-icon.png（iOS 主屏图标，180×180）
 * 如何运行：node scripts/generate-icons.mjs
 * 依赖：sharp（已作为 Astro 间接依赖装好）
 * 在项目中的作用：PWA 安装到主屏所需图标的一次性生成器
 */

import sharp from 'sharp';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SVG_PATH = resolve(ROOT, 'public/favicon.svg');
const PUBLIC = resolve(ROOT, 'public');

const svg = await readFile(SVG_PATH);

// 普通版（边缘留极少 padding，让"Р"撑满）
async function generate(size, out) {
  const buf = await sharp(svg, { density: 384 })
    .resize(size, size, { fit: 'contain', background: { r: 250, g: 245, b: 236, alpha: 1 } })
    .png()
    .toBuffer();
  await writeFile(resolve(PUBLIC, out), buf);
  console.log(`  ✓ ${out}  (${size}×${size})`);
}

// Maskable 版：Android adaptive icon 要求 logo 在中心 80%，外圈是 safe zone
async function generateMaskable(out, size = 512) {
  const inner = Math.round(size * 0.7);
  // 把 SVG 缩到 inner 大小、然后嵌进 size×size 的纯背景画布
  const innerBuf = await sharp(svg, { density: 384 })
    .resize(inner, inner)
    .png()
    .toBuffer();
  await sharp({
    create: {
      width: size,
      height: size,
      channels: 4,
      background: { r: 250, g: 245, b: 236, alpha: 1 },
    },
  })
    .composite([{ input: innerBuf, gravity: 'center' }])
    .png()
    .toFile(resolve(PUBLIC, out));
  console.log(`  ✓ ${out}  (${size}×${size}, maskable)`);
}

console.log('生成 PWA 图标...');
await Promise.all([
  generate(192, 'icon-192.png'),
  generate(512, 'icon-512.png'),
  generate(180, 'apple-touch-icon.png'),
  generateMaskable('icon-512-maskable.png', 512),
]);
console.log('完成。');
