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
        'purple-hover': '#7A39E3',

        // State colors
        'green-success': '#34C759',
        'success': '#0BBC87',
        'status-new': '#EB5757',
        'status-assembled': '#F8C20B',
        'status-blue': '#5E81DC',
        'status-pink': '#DC5EC0',
        'status-green': '#7FC663',
        'error-primary': '#DF1D4C',
        'whatsapp': '#25D366',

        // Neutral colors
        'gray-disabled': '#6B6773',
        'gray-placeholder': '#828282',
        'gray-neutral': '#C4C4C4',
        'gray-border': '#E0E0E0',
        'gray-secondary': '#8E8E93',

        // Background colors
        'gray-input': '#F2F2F2',
        'gray-input-alt': '#EEEDF2',
        'background-light': '#F2F2F7',
        'background-hover': '#F5F5F5',
        'background-section': '#EEEDF2',

        // Border colors
        'border-input': '#E2E2E2',
        'border-dashed': '#C7C7CC',
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