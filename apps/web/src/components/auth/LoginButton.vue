<template>
  <button
    @click="handleLogin"
    class="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
  >
    <svg
      class="h-5 w-5 mr-2"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- SVG path for Google icon -->
    </svg>
    Inicia sesión con Google
  </button>
</template>

<script setup>
import { getGoogleLoginUrl } from "../../services/authService";

// Método seguro para SSR
function handleLogin() {
  if (typeof window !== "undefined") {
    window.location.href = getGoogleLoginUrl();
  }
}
</script>
