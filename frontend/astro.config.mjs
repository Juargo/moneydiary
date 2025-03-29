// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcssPostcss from '@tailwindcss/postcss';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  base: '/moneydiary', // Añadimos este prefijo para todas las URLs generadas
  vite: {
    plugins: [],
    css: {
      postcss: {
        plugins: [tailwindcssPostcss()]
      }
    }
  }
});