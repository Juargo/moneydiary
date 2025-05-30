import { useAuthStore } from "../stores/authStore";

/**
 * Obtiene la URL para el inicio de sesión con Google
 * @returns {string} URL para iniciar el flujo de OAuth con Google
 */
export function getGoogleLoginUrl() {
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
  // Especificar la URL de callback en el frontend
  const redirectUri = `${window.location.origin}/auth/callback`;
  return `${apiUrl}/api/v1/auth/google/login?redirect_uri=${encodeURIComponent(
    redirectUri
  )}`;
}

/**
 * Procesa el callback de Google OAuth y almacena los tokens
 * @param {string} code - Código de autorización recibido de Google
 */
export async function processGoogleCallback(code) {
  const authStore = useAuthStore();
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  try {
    // Intercambiar el código por tokens
    const response = await fetch(`${apiUrl}/api/v1/auth/google/callback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        redirect_uri: `${window.location.origin}/auth/callback`,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error al procesar autenticación");
    }

    const tokenData = await response.json();

    // Guardar tokens en el store de autenticación
    authStore.updateTokens(tokenData);

    // Cargar información del usuario
    await loadUserInfo();

    return true;
  } catch (error) {
    console.error("Error en el proceso de autenticación:", error);
    throw error;
  }
}

/**
 * Carga la información del usuario autenticado
 */
export async function loadUserInfo() {
  const authStore = useAuthStore();
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  try {
    // Si no hay token de acceso, no hacer nada
    if (!authStore.accessToken) {
      return null;
    }

    // Obtener información del usuario
    const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expirado, intentar refresh
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          // Reintentar con el nuevo token
          return await loadUserInfo();
        } else {
          // Si no se pudo refrescar, limpiar autenticación
          authStore.logout();
          return null;
        }
      }
      throw new Error(
        `Error al obtener información del usuario: ${response.statusText}`
      );
    }

    const userData = await response.json();
    authStore.setUser(userData);
    return userData;
  } catch (error) {
    console.error("Error al cargar información del usuario:", error);
    return null;
  }
}
