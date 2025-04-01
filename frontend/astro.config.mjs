// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcssPostcss from '@tailwindcss/postcss';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  base: '/', // Añadimos este prefijo para todas las URLs generadas
  vite: {
    plugins: [],
    css: {
      postcss: {
        plugins: [tailwindcssPostcss()]
      }
    },
    define: {
      // Exponemos la variable de entorno al cliente
      'import.meta.env.PUBLIC_BACKEND_URL': JSON.stringify(process.env.BACKEND_URL || 'http://localhost:3001')
    }
  }
});