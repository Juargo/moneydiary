import { createClient } from "@urql/vue";
import { cacheExchange, fetchExchange } from "@urql/core";

// URL de la API GraphQL
const API_URL =
  import.meta.env.PUBLIC_API_URL || "http://localhost:8000/graphql";

// Cliente básico para uso en SSR (sin autenticación)
export const createSSRGraphQLClient = () => {
  return createClient({
    url: API_URL,
    exchanges: [cacheExchange, fetchExchange],
  });
};

// Cliente con autenticación para uso solo en el cliente
export function createGraphQLClient() {
  // Comprobación para ejecutarse solo en el cliente
  if (typeof window === "undefined") {
    return createSSRGraphQLClient();
  }

  // Importación dinámica para evitar evaluación SSR
  const { useAuthStore } = require("../../stores/authStore");
  const authStore = useAuthStore();

  return createClient({
    url: API_URL,
    exchanges: [cacheExchange, fetchExchange],
    fetchOptions: () => {
      const token = authStore.accessToken;

      return {
        headers: {
          authorization: token ? `Bearer ${token}` : "",
        },
      };
    },
  });
}
