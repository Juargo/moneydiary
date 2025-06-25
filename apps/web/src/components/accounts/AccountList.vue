<template>
  <div>
    <div v-if="loading" class="flex justify-center py-10">
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"
      ></div>
    </div>

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
                      {{ account.bank?.name }} ·
                      {{ account.account_type?.name }}
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
                  <div class="text-xs text-gray-500">
                    {{
                      account.account_number
                        ? formatAccountNumber(account.account_number)
                        : "Sin número"
                    }}
                  </div>
                </div>
              </div>
            </div>
          </a>
        </li>
      </ul>
    </div>

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

// Estado
const authStore = useAuthStore();
const loading = ref(true);
const error = ref(null);
const accounts = ref([]);

// Obtener datos de las cuentas
async function fetchAccounts() {
  loading.value = true;
  error.value = null;

  try {
    // Si no hay token de acceso, redirigir al login
    if (!authStore.accessToken) {
      window.location.href = "/auth/login?returnTo=/dashboard/accounts";
      return;
    }

    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const response = await fetch(`${apiUrl}/api/v1/accounts`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expirado, intentar refresh
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          // Reintentar con el nuevo token
          return await fetchAccounts();
        } else {
          // Si no se pudo refrescar, redirigir al login
          window.location.href = "/auth/login?returnTo=/dashboard/accounts";
          return;
        }
      }

      throw new Error(`Error al obtener cuentas: ${response.statusText}`);
    }

    const data = await response.json();
    accounts.value = data.items || data;
    loading.value = false;
  } catch (err) {
    console.error("Error al cargar cuentas:", err);
    error.value =
      "No se pudieron cargar tus cuentas. Por favor, intenta nuevamente.";
    loading.value = false;
  }
}

// Funciones de formato
function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
  }).format(amount);
}

function formatAccountNumber(accountNumber) {
  if (!accountNumber) return "";
  // Mostrar sólo los últimos 4 dígitos
  if (accountNumber.length > 4) {
    return "••••" + accountNumber.slice(-4);
  }
  return accountNumber;
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

// Inicializar
onMounted(() => {
  fetchAccounts();
});
</script>
