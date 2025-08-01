import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['**/__tests__/**/*.{js,ts,jsx,tsx}', '**/*.{spec,test}.{js,ts,jsx,tsx}']
  }
});
