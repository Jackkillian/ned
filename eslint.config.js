import { defineConfig, globalIgnores } from "eslint/config";
import neostandard from "neostandard";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import unusedImportsPlugin from "eslint-plugin-unused-imports";
import importXPlugin from "eslint-plugin-import-x";
import eslintConfigPrettier from "eslint-config-prettier";
import tsParser from "@typescript-eslint/parser";
import pluginQuery from "@tanstack/eslint-plugin-query";
import globals from "globals";

export default defineConfig([
  globalIgnores(["**/node_modules/", "**/build/", "**/.bun-cache/"]),
  {
    settings: {
      react: {
        version: "19.0",
      },
    },
  },
  ...neostandard({
    semi: true,
    noStyle: true,
  }),
  reactPlugin.configs.flat.recommended,
  reactPlugin.configs.flat["jsx-runtime"],
  reactHooksPlugin.configs.flat.recommended,
  {
    files: ["**/*.{ts,tsx,mjs,cjs}"],
    plugins: {
      "unused-imports": unusedImportsPlugin,
      import: importXPlugin,
      "@tanstack/query": pluginQuery,
    },
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2020,
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      indent: "off",
      "no-undef": "off",
      "lines-between-class-members": [
        "error",
        "always",
        { exceptAfterSingleLine: true },
      ],
      "prefer-promise-reject-errors": ["error", { allowEmptyReject: true }],
      "react/jsx-indent": ["error", 4],
      semi: ["error", "always", { omitLastInOneLineBlock: true }],
      "quote-props": "off",
      "dot-notation": "off",
      "prefer-const": "off",
      "no-var": "off",
      "array-callback-return": "off",
      "array-bracket-spacing": "off",
      "no-loss-of-precision": "off",
      "object-shorthand": "off",
      "no-useless-escape": "off",
      "no-trailing-spaces": "off",
      "no-return-assign": "off",
      "no-eval": "off",
      "no-unused-vars": "off",
      camelcase: "off",
      "comma-dangle": "off",
      curly: "off",
      "jsx-quotes": "off",
      "key-spacing": "off",
      "no-console": "off",
      quotes: "off",
      "react/jsx-curly-spacing": "off",
      "react/jsx-indent-props": "off",
      "react/prop-types": "off",
      "space-before-function-paren": "off",
      eqeqeq: "off",
      "import/no-webpack-loader-syntax": "off",
      "object-property-newline": "off",
      "react/jsx-no-bind": "off",
      "react/jsx-space-before-closing": "off",
      "react/jsx-tag-spacing": ["error", { beforeSelfClosing: "always" }],
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
          caughtErrors: "all",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "import/no-duplicates": "error",
      "@tanstack/query/exhaustive-deps": "error",
      "@tanstack/query/no-deprecated-options": "error",
      "@tanstack/query/prefer-query-object-syntax": "error",
      "@tanstack/query/stable-query-client": "error",
    },
  },
  eslintConfigPrettier,
]);
