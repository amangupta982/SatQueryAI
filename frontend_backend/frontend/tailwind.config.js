/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#050a12',
          900: '#080f1a',
          850: '#0b1420',
          800: '#0f1b2a',
          700: '#152438',
          600: '#1c3049',
          500: '#25405f',
        },
        cyan: {
          accent: '#3fd4d0',
          soft: '#7be6e2',
          dim: '#1f8a86',
        },
        signal: {
          amber: '#e8a94f',
          rose: '#e8637a',
          lime: '#7fd88f',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        body: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        panel: '0 1px 0 0 rgba(255,255,255,0.03) inset, 0 20px 40px -20px rgba(0,0,0,0.6)',
        glow: '0 0 0 1px rgba(63,212,208,0.15), 0 0 24px -4px rgba(63,212,208,0.25)',
      },
      backgroundImage: {
        'grid-faint': 'linear-gradient(rgba(63,212,208,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(63,212,208,0.05) 1px, transparent 1px)',
      },
      animation: {
        scan: 'scan 2.4s linear infinite',
        pulseSlow: 'pulseSlow 2.6s ease-in-out infinite',
        fadeUp: 'fadeUp 0.35s ease-out',
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        pulseSlow: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.4 },
        },
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(6px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
