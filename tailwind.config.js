/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Open Sans', 'Noto Sans', 'sans-serif'],
      },
      colors: {
        // Brand colors
        'purple-primary': '#8A49F3',
        'purple-light': '#EFEBF6',

        // State colors
        'green-success': '#34C759',
        'success': '#0BBC87',
        'status-new': '#EB5757',
        'status-assembled': '#F8C20B',
        'error-primary': '#DF1D4C',
        'whatsapp': '#25D366',

        // Neutral colors
        'gray-disabled': '#6B6773',
        'gray-placeholder': '#828282',
        'gray-neutral': '#C4C4C4',
        'gray-border': '#E0E0E0',

        // Background colors
        'gray-input': '#F2F2F2',
        'gray-input-alt': '#EEEDF2',
      },
      fontSize: {
        'xs': '12px',
        'sm': '13px',
        'base': '16px',
        'lg': '18px',
        'xl': '20px',
        '2xl': '24px',
      }
    },
  },
  plugins: [],
}