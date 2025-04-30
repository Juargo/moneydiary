import { createClient } from "@urql/vue";
import { cacheExchange, fetchExchange } from "@urql/core";
import { useAuthStore } from "../../stores/authStore";

// URL de la API GraphQL
const API_URL =
  import.meta.env.PUBLIC_API_URL || "http://localhost:8000/graphql";

export function createGraphQLClient() {
  const authStore = useAuthStore();

  return createClient({
    url: API_URL,
    exchanges: [cacheExchange, fetchExchange], // Añadir los exchanges explícitamente
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
