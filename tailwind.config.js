/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./**/*.{ts,tsx,html}'],
  theme: {
    extend: {},
  },
  plugins: [require('tailwindcss-animate')],
}


