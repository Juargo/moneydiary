<template>
  <div class="max-w-lg mx-auto mt-16 p-6 bg-white rounded-lg shadow-lg">
    <h1 class="text-2xl font-bold text-red-600 mb-4">Error de autenticación</h1>

    <div
      v-if="errorMessage"
      class="bg-red-50 border-l-4 border-red-500 p-4 mb-6"
    >
      <div class="flex">
        <div class="flex-shrink-0">
          <svg
            class="h-5 w-5 text-red-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ errorMessage }}
          </p>
          <p class="mt-2 text-xs text-red-600" v-if="errorDetails">
            Detalles técnicos: {{ errorDetails }}
          </p>
        </div>
      </div>
    </div>

    <p class="mb-6 text-gray-600">
      Ha ocurrido un error durante el proceso de autenticación. Por favor,
      intenta nuevamente o contacta al soporte si el problema persiste.
    </p>

    <div class="flex justify-between">
      <button
        @click="goHome"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition duration-200"
      >
        Volver al inicio
      </button>

      <button
        @click="tryAgain"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition duration-200"
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
const errorDetails = ref("");

onMounted(() => {
  if (typeof window !== "undefined") {
    // Obtener el mensaje de error de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get("error");

    // Intentar analizar el error si es un objeto serializado
    try {
      if (error && error.includes("{")) {
        const errorObj = JSON.parse(error);
        errorMessage.value = errorObj.message || "Error desconocido";
        errorDetails.value = errorObj.details || "";
      } else {
        errorMessage.value = error || "Error desconocido";
      }
    } catch (e) {
      console.error("Error al procesar el mensaje de error:", e);
      errorMessage.value = error || "Error desconocido";
    }

    // Para depuración
    console.error("Error de autenticación:", errorMessage.value);
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
