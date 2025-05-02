import { createSSRGraphQLClient } from "../utils/graphql/client";
import {
  ME_QUERY,
  REFRESH_TOKEN_MUTATION,
  LOGOUT_MUTATION,
} from "../utils/graphql/auth";

// Debug flag - set to true to enable debugging
const DEBUG_AUTH = false;

// Helper function for debug logging
const debugLog = (message: string, data?: any) => {
  if (DEBUG_AUTH) {
    if (data) {
      console.log(`[Auth Debug] ${message}`, data);
    } else {
      console.log(`[Auth Debug] ${message}`);
    }
  }
};

// Cliente para SSR (sin autenticación)
const ssrClient = createSSRGraphQLClient();

// Función para obtener el cliente apropiado
async function getClient() {
  if (typeof window === "undefined") {
    return ssrClient;
  }

  // Usar importación dinámica en lugar de require
  const { createGraphQLClient } = await import("../utils/graphql/client");
  return createGraphQLClient();
}

// Obtener la URL para iniciar sesión con Google
export function getGoogleLoginUrl() {
  const url = `${
    import.meta.env.PUBLIC_API_URL || "http://localhost:8000"
  }/api/v1/auth/google/login`;

  debugLog(`Google login URL: ${url}`);
  return url;
}

// Iniciar sesión con Google (redirecciona al usuario)
export function loginWithGoogle() {
  debugLog("Attempting to login with Google");
  if (typeof window !== "undefined") {
    const redirectUrl = getGoogleLoginUrl();
    debugLog(`Redirecting to: ${redirectUrl}`);
    window.location.href = redirectUrl;
  } else {
    debugLog("Login with Google called server-side, ignoring");
  }
}

// Procesar la redirección de callback después de auth con Google
export async function handleAuthCallback() {
  debugLog("Handling auth callback");
  if (typeof window === "undefined") {
    debugLog("Called server-side, returning false");
    return false;
  }

  const { useAuthStore } = await import("../stores/authStore");
  const authStore = useAuthStore();

  const params = new URLSearchParams(window.location.search);
  const accessToken = params.get("access_token");
  const refreshToken = params.get("refresh_token");

  debugLog("Auth callback URL parameters", {
    hasAccessToken: !!accessToken,
    hasRefreshToken: !!refreshToken,
  });

  if (accessToken && refreshToken) {
    debugLog("Tokens found, logging in user");
    authStore.login({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: "bearer",
    });

    // Cargar información del usuario
    debugLog("Loading user information");
    const success = await loadUserInfo();
    debugLog(`User info loading ${success ? "succeeded" : "failed"}`);

    return true;
  }

  const error = params.get("error");
  if (error) {
    debugLog("Authentication error", error);
    console.error("Error de autenticación:", error);
  } else {
    debugLog("No tokens and no error in callback");
  }

  return false;
}

// Cargar información del usuario autenticado
export async function loadUserInfo() {
  debugLog("Loading user information");
  if (typeof window === "undefined") {
    debugLog("Called server-side, returning false");
    return false;
  }

  const { useAuthStore } = await import("../stores/authStore");
  const authStore = useAuthStore();

  // Llamar a getClient de forma asíncrona
  const client = await getClient();

  try {
    const result = await client.query(ME_QUERY, {}).toPromise();

    if (result.error) {
      debugLog("Error loading user information", result.error);
      console.error("Error al cargar información del usuario:", result.error);
      return false;
    }

    if (result.data?.me) {
      debugLog("User information loaded successfully", result.data.me);
      authStore.setUser(result.data.me);
      return true;
    }
  } catch (error) {
    debugLog("Error querying user information", error);
    console.error("Error al consultar información de usuario:", error);
  }

  debugLog("Failed to load user information");
  return false;
}

// Cerrar sesión
export async function logout() {
  debugLog("Attempting to logout");
  if (typeof window === "undefined") {
    debugLog("Called server-side, returning false");
    return false;
  }

  const { useAuthStore } = await import("../stores/authStore");
  const authStore = useAuthStore();
  const client = await getClient();

  try {
    // Intentar hacer logout en el servidor
    debugLog("Attempting server-side logout");
    await client.mutation(LOGOUT_MUTATION, {}).toPromise();
    debugLog("Server-side logout succeeded");
  } catch (error) {
    // Incluso si falla, continuamos con el logout local
    debugLog("Error during server-side logout", error);
    console.error("Error al cerrar sesión en el servidor:", error);
  }

  // Cerrar sesión localmente (borra tokens y datos de usuario)
  debugLog("Performing local logout");
  authStore.logout();

  // Opcional: Redirigir al usuario a la página principal
  if (typeof window !== "undefined") {
    debugLog("Redirecting to home page");
    window.location.href = "/";
  }

  debugLog("Logout process completed");
  return true;
}
