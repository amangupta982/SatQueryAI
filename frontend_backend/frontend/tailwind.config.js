/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#f8fafc',
          900: '#ffffff',
          850: '#f8fafc',
          800: '#f1f5f9',
          700: '#e2e8f0',
          600: '#cbd5e1',
          500: '#94a3b8',
        },
        cyan: {
          accent: '#0284c7',
          soft: '#0369a1',
          dim: '#0284c7',
        },
        signal: {
          amber: '#d97706',
          rose: '#e11d48',
          lime: '#16a34a',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        body: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        panel: '0 1px 3px 0 rgba(0,0,0,0.06), 0 4px 12px -2px rgba(0,0,0,0.04)',
        glow: '0 0 0 1px rgba(2,132,199,0.2), 0 0 20px -2px rgba(2,132,199,0.15)',
      },
      backgroundImage: {
        'grid-faint': 'linear-gradient(rgba(2,132,199,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(2,132,199,0.05) 1px, transparent 1px)',
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
