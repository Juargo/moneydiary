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
        @click="fetchAccount"
        class="mt-2 text-sm text-primary-600 hover:text-primary-800"
      >
        Reintentar
      </button>
    </div>

    <div
      v-else-if="account"
      class="bg-white shadow overflow-hidden sm:rounded-lg"
    >
      <!-- Vista de información de la cuenta -->
      <div v-if="!isEditing" class="account-view">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">
              {{ account.name }}
            </h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">
              {{ account.bank.name }} - {{ account.account_type.name }}
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="toggleEditing"
              class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
            >
              <svg
                class="h-4 w-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                />
              </svg>
              Editar
            </button>
          </div>
        </div>

        <div class="border-t border-gray-200">
          <dl>
            <div
              class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">
                Número de cuenta
              </dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ account.account_number || "No especificado" }}
              </dd>
            </div>
            <div
              class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">Saldo actual</dt>
              <dd
                class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 font-semibold"
              >
                {{ formatCurrency(account.current_balance) }}
              </dd>
            </div>
            <div
              class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">Banco</dt>
              <dd
                class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 flex items-center"
              >
                <img
                  v-if="account.bank.logo_url"
                  :src="account.bank.logo_url"
                  class="h-5 w-5 mr-2"
                  :alt="account.bank.name"
                />
                {{ account.bank.name }}
              </dd>
            </div>
            <div
              class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">Tipo de cuenta</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ account.account_type.name }}
              </dd>
            </div>
            <div
              class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">Estado</dt>
              <dd class="mt-1 text-sm sm:mt-0 sm:col-span-2">
                <span
                  v-if="account.active"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                >
                  Activa
                </span>
                <span
                  v-else
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                >
                  Inactiva
                </span>
              </dd>
            </div>
            <div
              class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">Creada</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(account.created_at) }}
              </dd>
            </div>
            <div
              class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
            >
              <dt class="text-sm font-medium text-gray-500">
                Última actualización
              </dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(account.updated_at) }}
              </dd>
            </div>
          </dl>
        </div>

        <div class="px-4 py-5 sm:px-6">
          <h4 class="text-lg font-medium text-gray-900 mb-4">
            Últimas transacciones
          </h4>
          <div v-if="recentTransactions.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th
                    class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Fecha
                  </th>
                  <th
                    class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Descripción
                  </th>
                  <th
                    class="px-6 py-3 bg-gray-50 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Monto
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="txn in recentTransactions" :key="txn.id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(txn.date) }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-500">
                    {{ txn.description }}
                  </td>
                  <td
                    class="px-6 py-4 whitespace-nowrap text-sm text-right"
                    :class="txn.amount >= 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ formatCurrency(txn.amount) }}
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="px-6 py-3 flex justify-center">
              <a
                href="#"
                class="text-sm text-primary-600 hover:text-primary-800"
                >Ver todas las transacciones</a
              >
            </div>
          </div>
          <div v-else class="text-center py-10 text-gray-500">
            No hay transacciones recientes.
          </div>
        </div>
      </div>

      <!-- Formulario de edición -->
      <div v-else class="account-edit">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Editar cuenta
          </h3>
          <button
            @click="cancelEdit"
            class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>

        <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
          <form @submit.prevent="saveAccount">
            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div class="sm:col-span-3">
                <label
                  for="name"
                  class="block text-sm font-medium text-gray-700"
                  >Nombre de la cuenta</label
                >
                <div class="mt-1">
                  <input
                    type="text"
                    id="name"
                    v-model="editForm.name"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    required
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
                    v-model="editForm.account_number"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div class="sm:col-span-3">
                <label
                  for="bank_id"
                  class="block text-sm font-medium text-gray-700"
                  >Banco</label
                >
                <div class="mt-1">
                  <select
                    id="bank_id"
                    v-model="editForm.bank_id"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    required
                  >
                    <option
                      v-for="bank in banks"
                      :key="bank.id"
                      :value="bank.id"
                    >
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
                    v-model="editForm.account_type_id"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    required
                  >
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
                    v-model="editForm.current_balance"
                    class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 sm:text-sm border-gray-300 rounded-md"
                    required
                  />
                </div>
              </div>

              <div class="sm:col-span-3">
                <label
                  for="active"
                  class="block text-sm font-medium text-gray-700"
                  >Estado</label
                >
                <div class="mt-1">
                  <select
                    id="active"
                    v-model="editForm.active"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  >
                    <option :value="true">Activa</option>
                    <option :value="false">Inactiva</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                @click="cancelEdit"
                class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Cancelar
              </button>
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
                Guardar cambios
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-else class="bg-white shadow sm:rounded-lg p-6 text-center">
      <p class="text-gray-700">No se encontró la cuenta especificada.</p>
      <a
        href="/dashboard/accounts"
        class="mt-4 inline-block text-primary-600 hover:text-primary-800"
      >
        Volver al listado de cuentas
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useAuthStore } from "../../stores/authStore";

// Props
const props = defineProps({
  accountId: {
    type: String,
    required: true,
  },
});

// Estado
const authStore = useAuthStore();
const loading = ref(true);
const error = ref(null);
const account = ref(null);
const banks = ref([]);
const accountTypes = ref([]);
const recentTransactions = ref([]);
const isEditing = ref(false);
const saving = ref(false);

// Formulario de edición
const editForm = reactive({
  name: "",
  account_number: "",
  bank_id: null,
  account_type_id: null,
  current_balance: 0,
  active: true,
});

// Obtener datos de la cuenta
async function fetchAccount() {
  loading.value = true;
  error.value = null;

  try {
    // Si no hay token de acceso, redirigir al login
    if (!authStore.accessToken) {
      window.location.href =
        "/auth/login?returnTo=" + encodeURIComponent(window.location.pathname);
      return;
    }

    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    // Obtener datos de la cuenta
    const response = await fetch(
      `${apiUrl}/api/v1/accounts/${props.accountId}`,
      {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        // Token expirado, intentar refresh
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          // Reintentar con el nuevo token
          return await fetchAccount();
        } else {
          // Si no se pudo refrescar, redirigir al login
          window.location.href =
            "/auth/login?returnTo=" +
            encodeURIComponent(window.location.pathname);
          return;
        }
      }

      throw new Error(
        `Error al obtener datos de la cuenta: ${response.statusText}`
      );
    }

    const accountData = await response.json();
    account.value = accountData;

    // Cargar datos para el formulario de edición
    resetForm();

    // Obtener bancos y tipos de cuentas para el formulario
    await Promise.all([
      fetchBanks(),
      fetchAccountTypes(),
      fetchRecentTransactions(),
    ]);

    loading.value = false;
  } catch (err) {
    console.error("Error al cargar la cuenta:", err);
    error.value =
      "No se pudo cargar la información de la cuenta. Por favor, intenta nuevamente.";
    loading.value = false;
  }
}

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
  }
}

async function fetchRecentTransactions() {
  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(
      `${apiUrl}/api/v1/accounts/${props.accountId}/transactions?limit=5`,
      {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error al obtener transacciones: ${response.statusText}`);
    }

    const data = await response.json();
    recentTransactions.value = data.items || data;
  } catch (err) {
    console.error("Error al cargar transacciones:", err);
    // No mostramos error para no interrumpir la experiencia
    recentTransactions.value = [];
  }
}

function resetForm() {
  if (account.value) {
    editForm.name = account.value.name;
    editForm.account_number = account.value.account_number || "";
    editForm.bank_id = account.value.bank_id;
    editForm.account_type_id = account.value.account_type_id;
    editForm.current_balance = account.value.current_balance;
    editForm.active = account.value.active;
  }
}

function toggleEditing() {
  isEditing.value = !isEditing.value;
  if (isEditing.value) {
    resetForm();
  }
}

function cancelEdit() {
  isEditing.value = false;
}

async function saveAccount() {
  saving.value = true;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(
      `${apiUrl}/api/v1/accounts/${props.accountId}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(editForm),
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        // Token expirado, intentar refresh
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          // Reintentar con el nuevo token
          return await saveAccount();
        } else {
          throw new Error(
            "Sesión expirada. Por favor, inicia sesión nuevamente."
          );
        }
      }

      throw new Error(`Error al guardar cambios: ${response.statusText}`);
    }

    // Actualizar datos de la cuenta
    await fetchAccount();
    isEditing.value = false;
  } catch (err) {
    console.error("Error al guardar la cuenta:", err);
    alert("No se pudieron guardar los cambios: " + err.message);
  } finally {
    saving.value = false;
  }
}

// Funciones de formato
function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
  }).format(amount);
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("es-CL", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

// Inicializar
onMounted(() => {
  fetchAccount();
});
</script>
