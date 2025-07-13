import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { jwtDecode } from "jwt-decode";

interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface Permission {
  id: number;
  name: string;
  resource: string;
  action: string;
  description?: string;
}

interface Role {
  id: number;
  name: string;
  description?: string;
  permissions?: Permission[];
}

interface User {
  id: number;
  email: string;
  name: string | null;
  profile_image: string | null;
  is_active: boolean;
  email_verified: boolean;
  role?: Role | null;
  permissions?: Permission[];
}

// Utility function for safe localStorage access
const safeLocalStorage = {
  getItem(key: string): string | null {
    if (typeof localStorage !== "undefined") {
      return localStorage.getItem(key);
    }
    return null;
  },
  setItem(key: string, value: string): void {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(key, value);
    }
  },
  removeItem(key: string): void {
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem(key);
    }
  },
};

export const useAuthStore = defineStore("auth", () => {
  // Estado
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const user = ref<User | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value);

  const tokenExpiration = computed(() => {
    if (!accessToken.value) return null;

    try {
      const decoded: any = jwtDecode(accessToken.value);
      return decoded.exp * 1000; // convertir a milisegundos
    } catch (e) {
      return null;
    }
  });

  const isTokenExpired = computed(() => {
    const exp = tokenExpiration.value;
    if (!exp) return true;

    // Dejar un margen de 10 segundos
    return Date.now() > exp - 10000;
  });

  // Getters para roles y permisos
  const isAdmin = computed(() => {
    return !!user.value?.role && user.value.role.name === "admin";
  });

  const hasPermission = computed(() => {
    return (permissionName: string) => {
      if (!user.value?.permissions) return false;
      return user.value.permissions.some((p) => p.name === permissionName);
    };
  });

  // Acciones
  function login(tokenData: TokenData) {
    accessToken.value = tokenData.access_token;
    refreshToken.value = tokenData.refresh_token;

    // Guardar en localStorage de forma segura
    safeLocalStorage.setItem("access_token", tokenData.access_token);
    safeLocalStorage.setItem("refresh_token", tokenData.refresh_token);
  }

  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;

    // Limpiar localStorage de forma segura
    safeLocalStorage.removeItem("access_token");
    safeLocalStorage.removeItem("refresh_token");
  }

  function updateTokens(tokenData: TokenData) {
    accessToken.value = tokenData.access_token;
    refreshToken.value = tokenData.refresh_token;

    // Actualizar en localStorage de forma segura
    safeLocalStorage.setItem("access_token", tokenData.access_token);
    safeLocalStorage.setItem("refresh_token", tokenData.refresh_token);
  }

  function setUser(userData: User) {
    user.value = userData;
  }

  /**
   * Carga la información del usuario, incluyendo su rol y permisos
   */
  async function fetchUserInfo() {
    if (!accessToken.value) return null;

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });

      if (!response.ok) {
        throw new Error("Error al obtener información del usuario");
      }

      const userData = await response.json();
      setUser(userData);
      return userData;
    } catch (error) {
      console.error("Error fetching user data:", error);
      return null;
    }
  }

  // Inicializar estado desde localStorage
  function init() {
    // Verificar que estamos en un entorno con localStorage
    if (typeof window === "undefined") {
      return; // No inicializar en SSR
    }

    const storedAccessToken = safeLocalStorage.getItem("access_token");
    const storedRefreshToken = safeLocalStorage.getItem("refresh_token");

    if (storedAccessToken) {
      accessToken.value = storedAccessToken;
      refreshToken.value = storedRefreshToken;

      // Verificar si el token está expirado
      if (isTokenExpired.value) {
        // Podríamos intentar un refresh automático aquí
        logout();
      } else {
        // Intentar cargar la información del usuario si tenemos un token válido
        fetchUserInfo().catch((error) => {
          console.error("Error al inicializar datos de usuario:", error);
        });
      }
    }
  }

  /**
   * Renueva el token de acceso utilizando el refresh token almacenado
   * @returns {Promise<boolean>} True si el token fue renovado con éxito, False en caso contrario
   */
  async function refreshAuthToken(): Promise<boolean> {
    // Si no hay refresh token, no podemos renovar
    if (!refreshToken.value) {
      console.error("No hay refresh token disponible para renovar la sesión");
      return false;
    }

    try {
      const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

      // Llamar al endpoint de refresh token
      const response = await fetch(`${apiUrl}/api/v1/auth/refresh-token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh_token: refreshToken.value,
        }),
      });

      if (!response.ok) {
        console.error(
          `Error al renovar token: ${response.status} ${response.statusText}`
        );
        // Si hay un error 401 o 403, el refresh token podría ser inválido
        if (response.status === 401 || response.status === 403) {
          logout(); // Cerrar sesión si el token ya no es válido
        }
        return false;
      }

      // Procesar la respuesta
      const tokenData = await response.json();

      // Actualizar los tokens en el store
      updateTokens({
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token || refreshToken.value, // Usar el actual si no viene uno nuevo
        token_type: tokenData.token_type || "bearer",
      });

      console.log("Token renovado exitosamente");
      return true;
    } catch (error) {
      console.error("Error al renovar el token de acceso:", error);
      return false;
    }
  }

  // Inicializar al crear el store solo si no es SSR
  if (typeof window !== "undefined") {
    init();
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    isTokenExpired,
    isAdmin,
    hasPermission,
    login,
    logout,
    updateTokens,
    setUser,
    fetchUserInfo,
    refreshAuthToken,
  };
});
