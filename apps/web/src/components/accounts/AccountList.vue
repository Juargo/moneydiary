<template>
  <div>
    <!-- Indicador de carga -->
    <div v-if="loading" class="flex justify-center py-10">
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"
      ></div>
    </div>

    <!-- Mensaje de error -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 p-4 rounded-md"
    >
      <p class="text-red-700">{{ error }}</p>
      <button
        @click="fetchAccounts"
        class="mt-2 text-sm text-primary-600 hover:text-primary-800"
      >
        Reintentar
      </button>
    </div>

    <!-- Lista de cuentas -->
    <div
      v-else-if="accounts.length"
      class="bg-white shadow overflow-hidden sm:rounded-lg"
    >
      <ul class="divide-y divide-gray-200">
        <li
          v-for="account in accounts"
          :key="account.id"
          class="hover:bg-gray-50"
        >
          <!-- Enlace al detalle de la cuenta usando el ID -->
          <a :href="`/dashboard/accounts/${account.id}`" class="block">
            <div class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div
                    class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full"
                    :class="
                      account.active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-500'
                    "
                  >
                    <img
                      v-if="account.bank?.logo_url"
                      :src="account.bank.logo_url"
                      class="h-6 w-6"
                      :alt="account.bank.name"
                    />
                    <span v-else class="text-sm font-medium">{{
                      getBankInitials(account.bank?.name)
                    }}</span>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ account.name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ account.bank?.name || "Sin banco" }} ·
                      {{ account.account_type?.name || "Sin tipo" }}
                    </div>
                  </div>
                </div>
                <div class="flex flex-col items-end">
                  <div
                    class="text-sm font-semibold"
                    :class="
                      account.current_balance >= 0
                        ? 'text-green-700'
                        : 'text-red-700'
                    "
                  >
                    {{ formatCurrency(account.current_balance) }}
                  </div>
                </div>
              </div>
            </div>
          </a>
        </li>
      </ul>
    </div>

    <!-- Estado sin cuentas -->
    <div v-else class="bg-white shadow sm:rounded-lg p-6 text-center">
      <p class="text-gray-700">No tienes ninguna cuenta registrada.</p>
      <a
        href="/dashboard/accounts/new"
        class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
      >
        Añadir primera cuenta
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

const authStore = useAuthStore();
const accounts = ref([]);
const loading = ref(true);
const error = ref(null);

// Función para obtener las cuentas del usuario
async function fetchAccounts() {
  loading.value = true;
  error.value = null;

  try {
    if (!authStore.accessToken) {
      window.location.href = "/auth/login?returnTo=/dashboard/accounts";
      return;
    }

    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    // URL correcta para obtener todas las cuentas del usuario autenticado
    const response = await fetch(`${apiUrl}/api/v1/accounts`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          return fetchAccounts();
        } else {
          window.location.href = "/auth/login?returnTo=/dashboard/accounts";
          return;
        }
      }
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    accounts.value = data.items || data;
  } catch (err) {
    console.error("Error al obtener cuentas:", err);
    error.value =
      "No se pudieron cargar las cuentas. Por favor, intenta nuevamente.";
  } finally {
    loading.value = false;
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
  }).format(amount);
}

function getBankInitials(bankName) {
  if (!bankName) return "??";
  return bankName
    .split(" ")
    .map((word) => word.charAt(0))
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

onMounted(() => {
  fetchAccounts();
});
</script>
