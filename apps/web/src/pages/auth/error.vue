<template>
  <div class="max-w-lg mx-auto mt-16 p-6 bg-white rounded-lg shadow-lg">
    <h1 class="text-2xl font-bold text-red-600 mb-4">Error de autenticación</h1>

    <div
      v-if="errorMessage"
      class="bg-red-50 border-l-4 border-red-500 p-4 mb-6"
    >
      <p class="text-red-700">{{ errorMessage }}</p>
    </div>

    <p class="mb-6">
      Ha ocurrido un error durante el proceso de autenticación. Por favor,
      intenta nuevamente.
    </p>

    <div class="flex justify-between">
      <button
        @click="goHome"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
      >
        Volver al inicio
      </button>

      <button
        @click="tryAgain"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Intentar de nuevo
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { loginWithGoogle } from "../../services/authService";

const errorMessage = ref("");

onMounted(() => {
  // Obtener el mensaje de error de la URL
  if (typeof window !== "undefined") {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get("error");
    errorMessage.value = error || "Error desconocido";
  }
});

function goHome() {
  if (typeof window !== "undefined") {
    window.location.href = "/";
  }
}

function tryAgain() {
  loginWithGoogle();
}
</script>
