// 功能：Astro 站点构建配置
// 输入：本仓库 src/ 与 public/ 下的资源
// 输出：dist/ 静态站（含 service worker + manifest.webmanifest，构建时由 @vite-pwa/astro 生成）
// 如何运行：npm run dev / npm run build
// 依赖：astro, @astrojs/tailwind, @vite-pwa/astro
// 在项目中的作用：声明站点元数据、注入 Tailwind、注入 PWA + workbox 预缓存策略

import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import AstroPWA from '@vite-pwa/astro';

export default defineConfig({
  site: 'https://russian-travel-tau.vercel.app',
  integrations: [
    tailwind({
      applyBaseStyles: false, // 自己控制 base，不让 Tailwind 注入它的 preflight
    }),
    AstroPWA({
      registerType: 'autoUpdate',         // 检测到新版自动更新（无 reload prompt）
      injectRegister: 'script-defer',     // 自动在 <head> 注入 SW 注册脚本
      includeAssets: [
        'favicon.svg',
        'apple-touch-icon.png',
        'icon-192.png',
        'icon-512.png',
        'icon-512-maskable.png',
      ],
      manifest: {
        name: 'Русский для Узбекистана · 俄语生存包',
        short_name: 'РусUZ',
        description: '~250 张俄语生存短语卡，给乌兹别克斯坦旅行者。含发音、对方可能的回话、当地注脚。离线可用。',
        theme_color: '#faf5ec',
        background_color: '#faf5ec',
        display: 'standalone',
        orientation: 'portrait',
        lang: 'zh-CN',
        start_url: '/',
        scope: '/',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icon-512-maskable.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // 预缓存：HTML / CSS / JS / SVG / PNG / 字体 / 所有 mp3
        //   注意：cards.json 不在 dist/ —— 它在 src/data/ 被 Vite 打进 hoisted JS chunk，
        //   走 JS 入口直接 import。glob 里的 ',json' 实际只匹配 manifest.webmanifest 等元数据。
        globPatterns: [
          '**/*.{html,css,js,svg,png,webp,woff,woff2,json}',
          '**/audio/**/*.mp3',
        ],
        // 默认 2MB 上限会过滤掉某些资源；放宽到 5MB 以兼容未来更长的句子音频
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
        navigateFallback: '/',
        navigateFallbackDenylist: [/^\/api\//],
        // 不主动接管尚未访问的 URL，避免 SPA 行为误伤
        cleanupOutdatedCaches: true,
      },
      devOptions: {
        enabled: false, // 开发时关 SW，避免缓存阻塞热更新
      },
    }),
  ],
  server: {
    host: true,
    port: 4321,
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
