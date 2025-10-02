// Use CSS variables from design-system.css
const brandPink = 'var(--brand-primary)';
const brandSuccess = 'var(--brand-success)';
const brandWarning = 'var(--brand-warning)';
const brandError = 'var(--brand-error)';
const bgWhite = 'var(--bg-primary)';
const bgSecondary = 'var(--bg-secondary)';
const bgTertiary = 'var(--bg-tertiary)';
const borderDefault = 'var(--border-default)';
const borderFocus = 'var(--border-focus)';
const borderError = 'var(--border-error)';
const textPrimary = 'var(--text-primary)';
const textSecondary = 'var(--text-secondary)';
const textMuted = 'var(--text-muted)';
const textOnPrimary = 'var(--text-on-primary)';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Open Sans', 'sans-serif'],
        system: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      colors: {
        // Simplified color system - prefer CSS variables directly in classes
        // Keep essential mappings for backward compatibility
        border: borderDefault,
        background: bgWhite,
        foreground: textPrimary,
        primary: brandPink,
        secondary: bgSecondary,
        muted: textMuted,
        accent: 'var(--accent)',
        // Legacy aliases
        pink: brandPink,
      },
      fontSize: {
        // Remove deprecated body-* and btn-* presets
        // Use standard Tailwind text-* utilities instead (text-sm, text-base, text-lg, etc.)
      },
      letterSpacing: {
        tighter: '-0.025em',  // -2.5%
        tight: '-0.01em',      // -1% (Figma standard)
        normal: '0',
        wide: '0.025em',
      },
      spacing: {
        // Custom spacing scale - consider migrating to Tailwind defaults (4px base)
        // Current scale uses 8px increments for legacy compatibility
        2: '8px',
        4: '16px',
        8: '24px',
        12: '32px',
        16: '40px',
        20: '48px',
        24: '56px',
        28: '64px',
        32: '80px',
        40: '120px',
      },
      borderRadius: {
        // Aligned with CSS variables (4/8/12/16px)
        sm: 'var(--radius-sm)',    // 4px
        md: 'var(--radius-md)',    // 8px
        lg: 'var(--radius-lg)',    // 12px
        xl: 'var(--radius-xl)',    // 16px
        '2xl': 'var(--radius-2xl)', // 20px
        full: 'var(--radius-full)',
      },
      maxWidth: {
        mobile: '375px',
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s infinite',
        fadeIn: 'fadeIn 0.3s ease-out',
      },
    },
  },
  plugins: [],
};
