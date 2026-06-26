import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    browser: {
      connectTimeout: 120_000
    }
  }
});
