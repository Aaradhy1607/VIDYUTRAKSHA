/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#080C14',
          card: '#0F172A',
          cardHover: '#1E293B',
          border: '#1E293B',
          borderHighlight: '#334155',
          accent: '#38BDF8',
          accentGlow: 'rgba(56, 189, 248, 0.15)',
        },
        radar: {
          green: '#22c55e',
          yellow: '#eab308',
          orange: '#f97316',
          red: '#ef4444',
          magenta: '#d946ef',
          purple: '#a855f7'
        },
        alert: {
          green: '#10B981',
          yellow: '#F59E0B',
          orange: '#F97316',
          red: '#EF4444'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
