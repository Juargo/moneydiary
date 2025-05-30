<template>
  <div>
    <div v-if="authStore.isAuthenticated && authStore.user">
      <div class="relative inline-block text-left">
        <button
          @click="toggleDropdown"
          class="flex items-center space-x-2 text-gray-700 hover:text-gray-900"
          id="user-menu-button"
          aria-expanded="false"
          aria-haspopup="true"
        >
          <img
            v-if="authStore.user.profileImage"
            :src="authStore.user.profileImage"
            class="w-8 h-8 rounded-full"
            alt="Avatar"
          />
          <span>{{ authStore.user?.name || "Usuario" }}</span>
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            ></path>
          </svg>
        </button>

        <!-- Dropdown menu -->
        <div
          v-show="showDropdown"
          class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="user-menu-button"
          tabindex="-1"
        >
          <div class="py-1" role="none">
            <a
              href="/dashboard"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              role="menuitem"
              >Dashboard</a
            >

            <!-- Enlace específico para administradores -->
            <a
              v-if="isAdmin"
              href="/admin"
              class="block px-4 py-2 text-sm text-blue-600 hover:bg-gray-100"
              role="menuitem"
              >Panel de Administración</a
            >

            <a
              href="/profile"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              role="menuitem"
              >Perfil</a
            >

            <button
              @click="logout"
              class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              role="menuitem"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="authStore.isLoading">
      <span class="text-gray-600">Cargando...</span>
    </div>
    <div v-else>
      <a href="/auth/login" class="text-blue-600 hover:text-blue-800">
        Iniciar sesión
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";
import { isAdmin as checkAdmin } from "../../utils/auth";
import { loadUserInfo } from "../../services/authService";

const showDropdown = ref(false);
const authStore = useAuthStore();

// Comprobar si el usuario es administrador
const isAdmin = computed(() => {
  return checkAdmin();
});

onMounted(async () => {
  // Cargar información del usuario si está autenticado pero no tenemos sus datos
  if (authStore.isAuthenticated && !authStore.user) {
    await loadUserInfo();
  }
});

function toggleDropdown() {
  showDropdown.value = !showDropdown.value;
}

function logout() {
  authStore.logout();
  window.location.href = "/";
}

// Cerrar el menú al hacer clic fuera
if (typeof window !== "undefined") {
  window.addEventListener("click", (event) => {
    const userMenuButton = document.getElementById("user-menu-button");
    if (userMenuButton && !userMenuButton.contains(event.target)) {
      showDropdown.value = false;
    }
  });
}
</script>
