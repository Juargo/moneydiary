import { createSSRGraphQLClient } from "../utils/graphql/client";
import {
  ME_QUERY,
  REFRESH_TOKEN_MUTATION,
  LOGOUT_MUTATION,
} from "../utils/graphql/auth";

// Cliente para SSR (sin autenticación)
const ssrClient = createSSRGraphQLClient();

// Función para obtener el cliente apropiado
function getClient() {
  if (typeof window === "undefined") {
    return ssrClient;
  }

  // Importación dinámica solo en cliente
  const { createGraphQLClient } = require("../utils/graphql/client");
  return createGraphQLClient();
}

// Obtener la URL para iniciar sesión con Google
export function getGoogleLoginUrl() {
  return `${
    import.meta.env.PUBLIC_API_URL || "http://localhost:8000"
  }/auth/google/login`;
}

// Iniciar sesión con Google (redirecciona al usuario)
export function loginWithGoogle() {
  if (typeof window !== "undefined") {
    window.location.href = getGoogleLoginUrl();
  }
}

// Procesar la redirección de callback después de auth con Google
export async function handleAuthCallback() {
  if (typeof window === "undefined") return false;

  const { useAuthStore } = await import("../stores/authStore");
  const authStore = useAuthStore();

  const params = new URLSearchParams(window.location.search);
  const accessToken = params.get("access_token");
  const refreshToken = params.get("refresh_token");

  if (accessToken && refreshToken) {
    authStore.login({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: "bearer",
    });

    // Cargar información del usuario
    await loadUserInfo();

    return true;
  }

  const error = params.get("error");
  if (error) {
    console.error("Error de autenticación:", error);
  }

  return false;
}

// Cargar información del usuario autenticado
export async function loadUserInfo() {
  if (typeof window === "undefined") return false;

  const { useAuthStore } = await import("../stores/authStore");
  const authStore = useAuthStore();
  const client = getClient();

  try {
    const result = await client.query(ME_QUERY, {}).toPromise();

    if (result.error) {
      console.error("Error al cargar información del usuario:", result.error);
      return false;
    }

    if (result.data?.me) {
      authStore.setUser(result.data.me);
      return true;
    }
  } catch (error) {
    console.error("Error al consultar información de usuario:", error);
  }

  return false;
}

// Cerrar sesión
export async function logout() {
  if (typeof window === "undefined") return false;

  const { useAuthStore } = await import("../stores/authStore");
  const authStore = useAuthStore();
  const client = getClient();

  try {
    // Intentar hacer logout en el servidor
    await client.mutation(LOGOUT_MUTATION, {}).toPromise();
  } catch (error) {
    // Incluso si falla, continuamos con el logout local
    console.error("Error al cerrar sesión en el servidor:", error);
  }

  // Cerrar sesión localmente (borra tokens y datos de usuario)
  authStore.logout();

  // Opcional: Redirigir al usuario a la página principal
  if (typeof window !== "undefined") {
    window.location.href = "/";
  }

  return true;
}
