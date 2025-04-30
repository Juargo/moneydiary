import { useAuthStore } from "../stores/authStore";
import { ME_QUERY, REFRESH_TOKEN_MUTATION } from "../utils/graphql/auth";
import { createGraphQLClient } from "../utils/graphql/client";

const client = createGraphQLClient();

// Obtener la URL para iniciar sesión con Google
export function getGoogleLoginUrl() {
  return `${
    import.meta.env.PUBLIC_API_URL || "http://localhost:8000"
  }/auth/google/login`;
}

// Iniciar sesión con Google (redirecciona al usuario)
export function loginWithGoogle() {
  window.location.href = getGoogleLoginUrl();
}

// Procesar la redirección de callback después de auth con Google
export async function handleAuthCallback() {
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
  const authStore = useAuthStore();

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

// Refrescar token cuando expire
export async function refreshAuthToken() {
  const authStore = useAuthStore();

  if (!authStore.refreshToken) {
    return false;
  }

  try {
    const result = await client
      .mutation(REFRESH_TOKEN_MUTATION, {
        refreshToken: authStore.refreshToken,
      })
      .toPromise();

    if (result.error) {
      console.error("Error al refrescar token:", result.error);
      return false;
    }

    if (result.data?.refreshToken) {
      authStore.updateTokens(result.data.refreshToken);
      return true;
    }
  } catch (error) {
    console.error("Error al refrescar token:", error);
  }

  return false;
}

// Cerrar sesión
export function logout() {
  const authStore = useAuthStore();
  authStore.logout();
  window.location.href = "/";
}
