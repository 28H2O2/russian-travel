/** @type {import('tailwindcss').Config} */
// 功能：Tailwind 主题与扫描路径
// 输入：src/ 下所有 .astro / .ts / .tsx / .md / .html 文件
// 输出：构建期生成的 utility CSS
// 依赖：tailwindcss
// 在项目中的作用：把 design tokens（在 global.css 里以 CSS var 定义）暴露为 Tailwind 工具类

export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        // 西里尔字母与拉丁字母共用衬线，中文使用思源宋体
        serif: ['"PT Serif"', '"Noto Serif SC"', 'Georgia', 'serif'],
        sans: ['"Inter"', '"Noto Sans SC"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        paper: 'var(--paper)',
        ink: 'var(--ink)',
        muted: 'var(--muted)',
        accent: 'var(--accent)',
        scene: {
          essentials: 'var(--scene-essentials)',
          money: 'var(--scene-money)',
          transport: 'var(--scene-transport)',
          food: 'var(--scene-food)',
          lodging: 'var(--scene-lodging)',
          shopping: 'var(--scene-shopping)',
          emergency: 'var(--scene-emergency)',
          chat: 'var(--scene-chat)',
          uzbek: 'var(--scene-uzbek)',
        },
      },
      boxShadow: {
        card: '0 1px 0 var(--card-shadow), 0 2px 8px var(--card-shadow-soft)',
      },
      borderRadius: {
        card: '14px',
      },
    },
  },
  plugins: [],
};
