import type { App } from "vue";
import { createPinia } from "pinia";
import urql from "@urql/vue";

import { createSSRGraphQLClient } from "../utils/graphql/client";

// Esta función se ejecutará durante la hidratación de Vue en el cliente
export default (app: App) => {
  // Inicializar Pinia
  const pinia = createPinia();
  app.use(pinia);

  // Inicializar urql con el cliente GraphQL sin autenticación
  // El cliente con autenticación se usará en componentes cuando sea necesario
  app.use(urql, createSSRGraphQLClient());

  // Si necesitas registrar componentes globales, hazlo aquí
  // app.component('GlobalComponent', GlobalComponent);

  console.log("Vue inicializado con Pinia y urql");
};
