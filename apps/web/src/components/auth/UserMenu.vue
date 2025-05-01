<template>
  <div>
    <div v-if="authStore.isAuthenticated" class="relative">
      <button @click="isOpen = !isOpen" class="flex items-center space-x-2">
        <img
          v-if="authStore.user?.profile_image"
          :src="authStore.user.profile_image"
          class="h-8 w-8 rounded-full"
          alt="Foto de perfil"
        />
        <div
          v-else
          class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center"
        >
          <span class="text-gray-600">{{ userInitials }}</span>
        </div>
        <span class="hidden md:block text-sm font-medium text-gray-700">{{
          userName
        }}</span>
      </button>

      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10"
        @click.outside="isOpen = false"
      >
        <a
          href="/dashboard"
          class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >Dashboard</a
        >
        <a
          href="/profile"
          class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >Mi perfil</a
        >
        <button
          @click="handleLogout"
          class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
        >
          Cerrar sesión
        </button>
      </div>
    </div>
    <LoginButton v-else />
  </div>
</template>

<!-- /**
 * This Vue component represents a user menu for authentication-related actions.
 *
 * Script Setup:
 * - Imports:
 *   - `ref` and `computed` from Vue for reactive state and computed properties.
 *   - `useAuthStore` from the authentication store to access user data.
 *   - `logout` from the authentication service to handle user logout.
 *   - `LoginButton` component for rendering a login button.
 *
 * - Reactive State:
 *   - `isOpen`: A boolean ref to track whether the user menu is open or closed.
 *
 * - Computed Properties:
 *   - `userName`: Computes the display name of the user. It prioritizes the user's name, 
 *     falls back to the email username (before the "@" symbol), or defaults to "Usuario".
 *   - `userInitials`: Computes the initials of the user's name. If the name has multiple parts, 
 *     it uses the first letter of the first two parts. Otherwise, it uses the first two letters 
 *     of the name or email username. Defaults to "U" if no user data is available.
 *
 * - Methods:
 *   - `handleLogout`: Logs the user out by calling the `logout` function and closes the user menu.
 */ -->
<script setup lang="ts">
import { ref, computed } from "vue";
import { useAuthStore } from "../../stores/authStore";
import { logout } from "../../services/authService";
import LoginButton from "./LoginButton.vue";

const authStore = useAuthStore();
const isOpen = ref(false);

const userName = computed(() => {
  return (
    authStore.user?.name || authStore.user?.email?.split("@")[0] || "Usuario"
  );
});

const userInitials = computed(() => {
  if (authStore.user?.name) {
    const nameParts = authStore.user.name.split(" ");
    return nameParts.length > 1
      ? `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase()
      : authStore.user.name.slice(0, 2).toUpperCase();
  }
  return authStore.user?.email?.slice(0, 2).toUpperCase() || "U";
});

const handleLogout = () => {
  logout();
  isOpen.value = false;
};
</script>
