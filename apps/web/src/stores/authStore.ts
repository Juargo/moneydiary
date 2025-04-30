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

    // Guardar en localStorage
    localStorage.setItem("access_token", tokenData.access_token);
    localStorage.setItem("refresh_token", tokenData.refresh_token);
  }

  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;

    // Limpiar localStorage
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  function updateTokens(tokenData: TokenData) {
    accessToken.value = tokenData.access_token;
    refreshToken.value = tokenData.refresh_token;

    // Actualizar en localStorage
    localStorage.setItem("access_token", tokenData.access_token);
    localStorage.setItem("refresh_token", tokenData.refresh_token);
  }

  function setUser(userData: User) {
    user.value = userData;
  }

  // Inicializar estado desde localStorage
  function init() {
    const storedAccessToken = localStorage.getItem("access_token");
    const storedRefreshToken = localStorage.getItem("refresh_token");

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

  // Inicializar al crear el store
  init();

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
