<template>
  <div class="bg-white shadow overflow-hidden sm:rounded-lg">
    <div class="px-4 py-5 sm:px-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900">
        Crear nueva cuenta
      </h3>
      <p class="mt-1 max-w-2xl text-sm text-gray-500">
        Ingresa los datos de tu cuenta bancaria
      </p>
    </div>

    <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
      <form @submit.prevent="createAccount">
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
          <div class="sm:col-span-3">
            <label for="name" class="block text-sm font-medium text-gray-700"
              >Nombre de la cuenta</label
            >
            <div class="mt-1">
              <input
                type="text"
                id="name"
                v-model="form.name"
                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                required
                placeholder="Ej: Cuenta Corriente Personal"
              />
            </div>
          </div>

          <div class="sm:col-span-3">
            <label
              for="account_number"
              class="block text-sm font-medium text-gray-700"
              >Número de cuenta</label
            >
            <div class="mt-1">
              <input
                type="text"
                id="account_number"
                v-model="form.account_number"
                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                placeholder="Opcional"
              />
            </div>
          </div>

          <div class="sm:col-span-3">
            <label for="bank_id" class="block text-sm font-medium text-gray-700"
              >Banco</label
            >
            <div class="mt-1">
              <select
                id="bank_id"
                v-model="form.bank_id"
                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                required
              >
                <option value="" disabled>Selecciona un banco</option>
                <option v-for="bank in banks" :key="bank.id" :value="bank.id">
                  {{ bank.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="sm:col-span-3">
            <label
              for="account_type_id"
              class="block text-sm font-medium text-gray-700"
              >Tipo de cuenta</label
            >
            <div class="mt-1">
              <select
                id="account_type_id"
                v-model="form.account_type_id"
                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                required
              >
                <option value="" disabled>Selecciona un tipo</option>
                <option
                  v-for="type in accountTypes"
                  :key="type.id"
                  :value="type.id"
                >
                  {{ type.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="sm:col-span-3">
            <label
              for="current_balance"
              class="block text-sm font-medium text-gray-700"
              >Saldo actual</label
            >
            <div class="mt-1 relative rounded-md shadow-sm">
              <div
                class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
              >
                <span class="text-gray-500 sm:text-sm">$</span>
              </div>
              <input
                type="number"
                step="0.01"
                id="current_balance"
                v-model="form.current_balance"
                class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 sm:text-sm border-gray-300 rounded-md"
                required
                placeholder="0.00"
              />
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end space-x-3">
          <a
            href="/dashboard/accounts"
            class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancelar
          </a>
          <button
            type="submit"
            :disabled="saving"
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg
              v-if="saving"
              class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Crear cuenta
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

// Estado
const authStore = useAuthStore();
const banks = ref([]);
const accountTypes = ref([]);
const saving = ref(false);
const error = ref(null);

// Formulario
const form = reactive({
  name: "",
  account_number: "",
  bank_id: "",
  account_type_id: "",
  current_balance: 0,
  active: true,
});

// Obtener datos para los selectores
async function fetchBanks() {
  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(`${apiUrl}/api/v1/banks`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error al obtener bancos: ${response.statusText}`);
    }

    const data = await response.json();
    banks.value = data.items || data;
  } catch (err) {
    console.error("Error al cargar bancos:", err);
    error.value = "No se pudieron cargar los bancos disponibles.";
  }
}

async function fetchAccountTypes() {
  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(`${apiUrl}/api/v1/account-types`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error(
        `Error al obtener tipos de cuenta: ${response.statusText}`
      );
    }

    const data = await response.json();
    accountTypes.value = data.items || data;
  } catch (err) {
    console.error("Error al cargar tipos de cuenta:", err);
    error.value = "No se pudieron cargar los tipos de cuenta disponibles.";
  }
}

// Crear nueva cuenta
async function createAccount() {
  saving.value = true;
  error.value = null;

  try {
    // Si no hay token de acceso, redirigir al login
    if (!authStore.accessToken) {
      window.location.href = "/auth/login?returnTo=/dashboard/accounts/new";
      return;
    }

    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const response = await fetch(`${apiUrl}/api/v1/accounts`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expirado, intentar refresh
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          // Reintentar con el nuevo token
          return await createAccount();
        } else {
          throw new Error(
            "Sesión expirada. Por favor, inicia sesión nuevamente."
          );
        }
      }

      const errorData = await response.json();
      throw new Error(
        errorData.message || `Error al crear cuenta: ${response.statusText}`
      );
    }

    const newAccount = await response.json();

    // Redirigir a la página de la cuenta recién creada
    window.location.href = `/dashboard/accounts/${newAccount.id}`;
  } catch (err) {
    console.error("Error al crear cuenta:", err);
    error.value =
      err.message ||
      "No se pudo crear la cuenta. Por favor, intenta nuevamente.";
    alert(error.value);
  } finally {
    saving.value = false;
  }
}

// Inicializar
onMounted(async () => {
  // Si no hay token de acceso, redirigir al login
  if (!authStore.accessToken) {
    window.location.href = "/auth/login?returnTo=/dashboard/accounts/new";
    return;
  }

  // Cargar datos para los selectores
  await Promise.all([fetchBanks(), fetchAccountTypes()]);
});
</script>
