import js from '@eslint/js';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx}'],
    plugins: {
      react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off', // Not needed with new JSX transform
      'react/prop-types': 'off', // Disable prop-types since we're not using TypeScript

      // Custom rule to prevent raw hex colors will be defined in second config
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        fetch: 'readonly',
        URLSearchParams: 'readonly',
        FormData: 'readonly',
      },
    },
  },
  {
    // Custom rule definition for detecting hex colors
    plugins: {
      'design-system': {
        rules: {
          'no-hex-colors': {
            meta: {
              type: 'problem',
              docs: {
                description: 'Disallow raw hex color values in favor of design tokens',
                category: 'Design System',
                recommended: true,
              },
              fixable: null,
              schema: [],
            },
            create(context) {
              // Regex patterns for different hex color formats
              const hexColorPatterns = [
                /bg-\[#[0-9A-Fa-f]{3,6}\]/g,       // bg-[#ffffff]
                /text-\[#[0-9A-Fa-f]{3,6}\]/g,     // text-[#ffffff]
                /border-\[#[0-9A-Fa-f]{3,6}\]/g,   // border-[#ffffff]
                /stroke=["']#[0-9A-Fa-f]{3,6}["']/g, // stroke="#ffffff"
                /fill=["']#[0-9A-Fa-f]{3,6}["']/g,   // fill="#ffffff"
                /#[0-9A-Fa-f]{6}\b/g,              // Direct hex values
              ];

              const allowedHexColors = [
                // Allow hex colors in comments or documentation
                // Could add specific exceptions here if needed
              ];

              function checkForHexColors(node, value) {
                if (typeof value !== 'string') return;

                hexColorPatterns.forEach(pattern => {
                  const matches = value.match(pattern);
                  if (matches) {
                    matches.forEach(match => {
                      if (!allowedHexColors.includes(match)) {
                        context.report({
                          node,
                          message: `Raw hex color '${match}' found. Use design tokens instead (e.g., 'bg-purple-primary', 'text-gray-disabled', 'stroke-gray-placeholder').`,
                        });
                      }
                    });
                  }
                });
              }

              return {
                Literal(node) {
                  if (typeof node.value === 'string') {
                    checkForHexColors(node, node.value);
                  }
                },
                TemplateElement(node) {
                  checkForHexColors(node, node.value.raw);
                },
                JSXAttribute(node) {
                  if (node.value && node.value.type === 'Literal') {
                    checkForHexColors(node, node.value.value);
                  }
                  if (node.value && node.value.type === 'JSXExpressionContainer'
                      && node.value.expression.type === 'Literal') {
                    checkForHexColors(node, node.value.expression.value);
                  }
                },
              };
            },
          },
        },
      },
    },
    rules: {
      'design-system/no-hex-colors': 'error',
    },
  },
];