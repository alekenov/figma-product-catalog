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
        main: {
          pink: brandPink,
        },
        pink: brandPink,
        brand: {
          primary: brandPink,
          success: brandSuccess,
          warning: brandWarning,
          error: brandError,
        },
        bg: {
          primary: bgWhite,
          secondary: bgSecondary,
          tertiary: bgTertiary,
          light: bgTertiary,
          'extra-light': bgSecondary,
          white: bgWhite,
        },
        border: {
          default: borderDefault,
          focus: borderFocus,
          error: borderError,
          focused: borderFocus,
          'grey-dark': bgTertiary,
          'grey-light': borderDefault,
        },
        text: {
          primary: textPrimary,
          secondary: textSecondary,
          muted: textMuted,
          'on-primary': textOnPrimary,
          black: textPrimary,
          white: textOnPrimary,
          'grey-dark': textSecondary,
          pink: brandPink,
          error: brandError,
          success: brandSuccess,
        },
        btn: {
          primary: brandPink,
          'primary-hover': brandPink,
          'primary-disabled': textMuted,
          secondary: brandPink,
          'secondary-hover': brandPink,
          tertiary: textPrimary,
        },
        field: {
          text: textPrimary,
          description: textMuted,
          disabled: textMuted,
        },
      },
      fontSize: {
        h1: ['32px', { lineHeight: '1.2', fontWeight: '700' }],
        h2: ['20px', { lineHeight: '1.2', fontWeight: '700' }],
        h3: ['18px', { lineHeight: '1.2', fontWeight: '700' }],
        h4: ['16px', { lineHeight: '1.2', fontWeight: '700' }],
        h5: ['14px', { lineHeight: '1.2', fontWeight: '700' }],
        'body-1': ['16px', { lineHeight: '1.3', fontWeight: '400' }],
        'body-2': ['14px', { lineHeight: '1.3', fontWeight: '400' }],
        'btn-large': ['20px', { lineHeight: '1.2' }],
        'btn-normal': ['20px', { lineHeight: '1.2' }],
        'btn-medium': ['16px', { lineHeight: '1.25' }],
        'btn-small': ['14px', { lineHeight: '1.29' }],
        'field-placeholder': ['16px', { lineHeight: '1.5' }],
        'field-title': ['12px', { lineHeight: '1.33' }],
      },
      spacing: {
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
        sm: '4px',
        md: '8px',
        lg: '16px',
        xl: '24px',
        '2xl': '32px',
        full: '9999px',
        button: '64px',
      },
      maxWidth: {
        mobile: '375px',
      },
    },
  },
  plugins: [],
};
