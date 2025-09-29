/**
 * Design System Tokens
 * Extracted from Figma: Cvety.kz Design System
 *
 * Sections:
 * 1. Colors
 * 2. Typography
 * 3. Spacing
 * 4. Border Radius
 */

export const colors = {
  // MAIN
  main: {
    pink: '#FF6666',
  },

  // BACKGROUNDS
  bg: {
    greyLight: '#ECECEC',
    greyExtraLight: '#F5F5F5',
    white: '#FFFFFF',
  },

  // STROKES / BORDERS
  stroke: {
    focused: '#FF6666',
    greyDark: '#FCFDFD',
    greyLight: '#EB8B8B',
  },

  // TEXT COLORS
  text: {
    black: '#000000',
    white: '#FFFFFF',
    greyDark: '#8F9F9F',
    pink: '#FF6666',
    validation: '#G9C5EC', // Note: This looks like an invalid color code in Figma
    error: '#F52E2E',
    success: '#01B56D',
  },

  // BUTTON STATES
  button: {
    primary: {
      default: '#FF6666',
      hover: '#CE3A3A',
      focused: '#8DBF8',
      disabled: '#FFF020',
      textDefault: '#FFFFFF',
      textFocused: '#FFFFFF',
    },
    secondary: {
      default: '#FF6666',
      hover: '#FF6666',
      focused: '#FF6666',
      textDefault: '#FF6666',
      textFocused: '#FF6666',
      textClick: '#FF6666',
      textDisabled: '#FBF3DE3',
    },
    tertiary: {
      default: '#000000',
      textDefault: '#FFFFFF',
    },
  },

  // FIELDS
  fields: {
    text: '#000000',
    description: '#AAAAAA',
    textDisabled: '#AAAAAA',
  },
};

export const typography = {
  fontFamily: {
    primary: ['Nunito Sans', 'sans-serif'],
    fallback: ['Open Sans', 'Noto Sans', 'sans-serif'],
  },

  // MOBILE TYPOGRAPHY
  mobile: {
    headline1: {
      fontSize: '32px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline2: {
      fontSize: '20px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline3: {
      fontSize: '18px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline4: {
      fontSize: '16px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline5: {
      fontSize: '14px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    body1: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: 1.3,
    },
    body2: {
      fontSize: '14px',
      fontWeight: 400,
      lineHeight: 1.3,
    },
  },

  // TABLET TYPOGRAPHY
  tablet: {
    headline1: {
      fontSize: '48px',
      fontWeight: 700,
      lineHeight: 1.1,
    },
    headline2: {
      fontSize: '32px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline3: {
      fontSize: '24px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline4: {
      fontSize: '18px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline5: {
      fontSize: '16px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    body1: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: 1.3,
    },
    body2: {
      fontSize: '14px',
      fontWeight: 400,
      lineHeight: 1.3,
    },
  },

  // DESKTOP TYPOGRAPHY
  desktop: {
    headline1: {
      fontSize: '56px',
      fontWeight: 700,
      lineHeight: 1.1,
    },
    headline2: {
      fontSize: '48px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline3: {
      fontSize: '32px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline4: {
      fontSize: '24px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    headline5: {
      fontSize: '18px',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    body1: {
      fontSize: '18px',
      fontWeight: 400,
      lineHeight: 1.4,
    },
    body2: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: 1.4,
    },
  },

  // BUTTONS & LINKS
  button: {
    large: {
      fontSize: '20px',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    normal: {
      fontSize: '20px',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    medium: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: 1.25,
    },
    small: {
      fontSize: '14px',
      fontWeight: 400,
      lineHeight: 1.29,
    },
    extraSmall: {
      fontSize: '14px',
      fontWeight: 400,
      lineHeight: 1.29,
    },
  },

  // FORM FIELDS
  fields: {
    placeholder: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    title: {
      fontSize: '12px',
      fontWeight: 400,
      lineHeight: 1.33,
    },
    description: {
      fontSize: '12px',
      fontWeight: 400,
      lineHeight: 1.33,
    },
  },
};

export const spacing = {
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
};

export const borderRadius = {
  sm: '4px',
  md: '8px',
  lg: '16px',
  xl: '24px',
  '2xl': '32px',
  full: '9999px',
  button: '64px', // Pills/rounded buttons
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
};