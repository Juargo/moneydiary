import { defineConfig } from "astro/config";
import vue from "@astrojs/vue";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  integrations: [
    vue({
      appEntrypoint: "/src/pages/_app", // Archivo para configurar Vue globalmente
    }),
    tailwind(),
  ],
  vite: {
    ssr: {
      noExternal: ["@urql/vue", "@urql/core"], // Para evitar problemas de hydration
    },
  },
});
