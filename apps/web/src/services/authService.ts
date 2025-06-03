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
interface GoogleCallbackTokenData {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
  [key: string]: any; // For any additional fields returned by backend
}

interface GoogleCallbackError {
  detail?: string;
  [key: string]: any;
}

export async function processGoogleCallback(code: string): Promise<boolean> {
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

    console.log("Respuesta del servidor al procesar callback:", response);

    if (!response.ok) {
      const errorData: GoogleCallbackError = await response.json();
      throw new Error(errorData.detail || "Error al procesar autenticación");
    }

    const tokenData: GoogleCallbackTokenData = await response.json();

    // Guardar tokens en el store de autenticación
    authStore.updateTokens({
      access_token: tokenData.accessToken,
      refresh_token: tokenData.refreshToken,
      token_type: tokenData.tokenType,
      expires_in: tokenData.expiresIn as number, // Make sure TokenData type includes expires_in if needed
    } as {
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
    });

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
  console.log("Cargando información del usuario...");
  const authStore = useAuthStore();
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  console.log("Token de acceso:", authStore.accessToken);
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

    console.log("Respuesta del servidor:", response);

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

    console.log("Información del usuario recibida correctamente");
    const userData = await response.json();
    console.log("Datos del usuario:", userData);
    authStore.setUser(userData);
    return userData;
  } catch (error) {
    console.error("Error al cargar información del usuario:", error);
    return null;
  }
}
