import js from '@eslint/js';
import next from 'eslint-config-next';
import tsPlugin from '@typescript-eslint/eslint-plugin';

export default [
  js.configs.recommended,   // base JS rules
  ...next(),                // Next.js “core-web-vitals” preset
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { parser: '@typescript-eslint/parser' },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
];
