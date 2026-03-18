/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      colors: {
        regime: {
          'risk-on': '#10b981',
          'neutral': '#6b7280',
          'defensive': '#ef4444',
        }
      }
    },
  },
  plugins: [],
}
