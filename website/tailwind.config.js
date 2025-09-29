import { colors, typography, spacing, borderRadius } from './src/designTokens.js';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Font Family from Design System
      fontFamily: {
        'sans': typography.fontFamily.primary,
        'fallback': typography.fontFamily.fallback,
      },

      // Colors from Design System
      colors: {
        // Main brand color
        'main': colors.main.pink,
        'pink': colors.main.pink,

        // Backgrounds
        'bg': {
          light: colors.bg.greyLight,
          'extra-light': colors.bg.greyExtraLight,
          white: colors.bg.white,
        },

        // Borders/Strokes
        'border': {
          focused: colors.stroke.focused,
          'grey-dark': colors.stroke.greyDark,
          'grey-light': colors.stroke.greyLight,
        },

        // Text colors
        'text': {
          black: colors.text.black,
          white: colors.text.white,
          'grey-dark': colors.text.greyDark,
          pink: colors.text.pink,
          error: colors.text.error,
          success: colors.text.success,
        },

        // Button states
        'btn': {
          'primary': colors.button.primary.default,
          'primary-hover': colors.button.primary.hover,
          'primary-disabled': colors.button.primary.disabled,
          'secondary': colors.button.secondary.default,
          'secondary-hover': colors.button.secondary.hover,
          'tertiary': colors.button.tertiary.default,
        },

        // Form fields
        'field': {
          text: colors.fields.text,
          description: colors.fields.description,
          disabled: colors.fields.textDisabled,
        },
      },

      // Typography - Mobile first (default)
      fontSize: {
        // Mobile Headlines
        'h1': [typography.mobile.headline1.fontSize, { lineHeight: typography.mobile.headline1.lineHeight, fontWeight: typography.mobile.headline1.fontWeight }],
        'h2': [typography.mobile.headline2.fontSize, { lineHeight: typography.mobile.headline2.lineHeight, fontWeight: typography.mobile.headline2.fontWeight }],
        'h3': [typography.mobile.headline3.fontSize, { lineHeight: typography.mobile.headline3.lineHeight, fontWeight: typography.mobile.headline3.fontWeight }],
        'h4': [typography.mobile.headline4.fontSize, { lineHeight: typography.mobile.headline4.lineHeight, fontWeight: typography.mobile.headline4.fontWeight }],
        'h5': [typography.mobile.headline5.fontSize, { lineHeight: typography.mobile.headline5.lineHeight, fontWeight: typography.mobile.headline5.fontWeight }],

        // Mobile Body
        'body-1': [typography.mobile.body1.fontSize, { lineHeight: typography.mobile.body1.lineHeight, fontWeight: typography.mobile.body1.fontWeight }],
        'body-2': [typography.mobile.body2.fontSize, { lineHeight: typography.mobile.body2.lineHeight, fontWeight: typography.mobile.body2.fontWeight }],

        // Buttons
        'btn-large': [typography.button.large.fontSize, { lineHeight: typography.button.large.lineHeight }],
        'btn-normal': [typography.button.normal.fontSize, { lineHeight: typography.button.normal.lineHeight }],
        'btn-medium': [typography.button.medium.fontSize, { lineHeight: typography.button.medium.lineHeight }],
        'btn-small': [typography.button.small.fontSize, { lineHeight: typography.button.small.lineHeight }],

        // Fields
        'field-placeholder': [typography.fields.placeholder.fontSize, { lineHeight: typography.fields.placeholder.lineHeight }],
        'field-title': [typography.fields.title.fontSize, { lineHeight: typography.fields.title.lineHeight }],
      },

      // Spacing from Design System (multiples of 8px)
      spacing: spacing,

      // Border Radius
      borderRadius: borderRadius,

      // Max width for mobile container
      maxWidth: {
        'mobile': '375px',
      },
    },
  },
  plugins: [],
}