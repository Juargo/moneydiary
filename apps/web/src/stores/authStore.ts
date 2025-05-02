import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { jwtDecode } from "jwt-decode";

interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface User {
  id: number;
  email: string;
  name: string | null;
  profile_image: string | null;
  is_active: boolean;
  email_verified: boolean;
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
      }
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
    login,
    logout,
    updateTokens,
    setUser,
  };
});
