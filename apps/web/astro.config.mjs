import { defineConfig } from "astro/config";
import vue from "@astrojs/vue";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  server: {
    port: parseInt(process.env.PORT) || 3000,
    host: process.env.HOST || "0.0.0.0",
  },
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
  output: "static", // Changed to static for now to avoid adapter issues
});
