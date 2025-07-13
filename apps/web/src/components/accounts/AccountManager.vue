<template>
  <div class="max-w-4xl mx-auto">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-64">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
      ></div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-lg p-4"
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
          <h3 class="text-sm font-medium text-red-800">Error</h3>
          <p class="mt-1 text-sm text-red-700">{{ error }}</p>
          <div class="mt-4">
            <button
              @click="retryFetch"
              class="bg-red-100 hover:bg-red-200 text-red-800 font-medium py-2 px-4 rounded text-sm"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Account Details -->
    <div v-else-if="account" class="space-y-6">
      <!-- Header with Account Basic Info -->
      <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <!-- Bank Logo -->
              <div class="flex-shrink-0">
                <img
                  v-if="account.bank.logoUrl"
                  :src="account.bank.logoUrl"
                  :alt="account.bank.name"
                  class="h-12 w-12 rounded-lg object-cover"
                />
                <div
                  v-else
                  class="h-12 w-12 rounded-lg bg-gray-200 flex items-center justify-center"
                >
                  <span class="text-gray-500 font-medium text-sm">{{
                    account.bank.name.charAt(0)
                  }}</span>
                </div>
              </div>

              <!-- Account Info -->
              <div>
                <h1 class="text-2xl font-bold text-gray-900">
                  {{ account.name }}
                </h1>
                <p class="text-sm text-gray-600">{{ account.bank.name }}</p>
                <p class="text-sm text-gray-500">
                  {{ account.accountType.name }}
                </p>
              </div>
            </div>

            <!-- Edit Button -->
            <button
              @click="startEditing"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg
                class="h-4 w-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Editar
            </button>
          </div>
        </div>
      </div>

      <!-- Balance and Status -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Current Balance -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Saldo Actual</p>
              <p class="text-2xl font-semibold text-gray-900">
                ${{ formatCurrency(account.currentBalance) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Account Status -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center',
                  account.active ? 'bg-green-100' : 'bg-red-100',
                ]"
              >
                <svg
                  class="w-5 h-5"
                  :class="account.active ? 'text-green-600' : 'text-red-600'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    v-if="account.active"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                  <path
                    v-else
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Estado</p>
              <p
                :class="[
                  'text-sm font-semibold',
                  account.active ? 'text-green-600' : 'text-red-600',
                ]"
              >
                {{ account.active ? "Activa" : "Inactiva" }}
              </p>
            </div>
          </div>
        </div>

        <!-- Account Type -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Tipo de Cuenta</p>
              <p class="text-sm font-semibold text-gray-900">
                {{ account.accountType.name }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Account Details -->
      <div class="bg-white shadow-sm rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
            Detalles de la Cuenta
          </h3>

          <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt class="text-sm font-medium text-gray-500">
                Número de Cuenta
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ account.accountNumber || "No especificado" }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-gray-500">Banco</dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ account.bank.name }} ({{ account.bank.code }})
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-gray-500">Tipo de Cuenta</dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ account.accountType.name }}
                <span
                  v-if="account.accountType.description"
                  class="text-gray-500"
                >
                  - {{ account.accountType.description }}
                </span>
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-gray-500">Código del Tipo</dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ account.accountType.code }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-gray-500">
                Fecha de Creación
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ formatDate(account.createdAt) }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-gray-500">
                Última Actualización
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ formatDate(account.updatedAt) }}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Recent Transactions Section -->
      <div class="bg-white shadow-sm rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900">
              Transacciones Recientes
            </h3>
            <button class="text-sm text-blue-600 hover:text-blue-500">
              Ver todas
            </button>
          </div>

          <div class="text-center py-8 text-gray-500">
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p class="mt-2">No hay transacciones recientes</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div
      v-if="isEditing"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
      >
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Editar Cuenta</h3>

          <form @submit.prevent="updateAccount" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >Nombre</label
              >
              <input
                v-model="editForm.name"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700"
                >Número de Cuenta</label
              >
              <input
                v-model="editForm.account_number"
                type="text"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700"
                >Saldo Actual</label
              >
              <input
                v-model="editForm.current_balance"
                type="number"
                step="0.01"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div class="flex items-center">
              <input
                v-model="editForm.active"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label class="ml-2 block text-sm text-gray-900"
                >Cuenta activa</label
              >
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="cancelEdit"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {{ saving ? "Guardando..." : "Guardar" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

// Props - ID de la cuenta a mostrar/editar
const props = defineProps({
  accountId: {
    type: [String, Number],
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

// GraphQL Queries
const GET_MY_ACCOUNT_QUERY = `
  query GetMyAccount($accountId: Int!) {
    myAccount(accountId: $accountId) {
      id
      name
      accountNumber
      currentBalance
      active
      createdAt
      updatedAt
      bank {
        id
        name
        code
        logoUrl
      }
      accountType {
        id
        name
        code
        description
      }
    }
  }
`;

// Formulario de edición
const editForm = reactive({
  name: "",
  account_number: "",
  bank_id: null,
  account_type_id: null,
  current_balance: 0,
  active: true,
});

// Función para realizar consultas GraphQL
async function graphqlRequest(query, variables = {}) {
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  const response = await fetch(`${apiUrl}/graphql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authStore.accessToken}`,
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();

  if (data.errors) {
    throw new Error(data.errors[0]?.message || "Error en la consulta GraphQL");
  }

  return data.data;
}

// Obtener datos de la cuenta específica usando el ID
async function fetchAccount() {
  try {
    loading.value = true;
    error.value = null;

    const accountId = parseInt(props.accountId);
    const data = await graphqlRequest(GET_MY_ACCOUNT_QUERY, { accountId });

    if (data.myAccount) {
      account.value = data.myAccount;

      // Poblar formulario de edición
      editForm.name = data.myAccount.name;
      editForm.account_number = data.myAccount.accountNumber || "";
      editForm.bank_id = data.myAccount.bank.id;
      editForm.account_type_id = data.myAccount.accountType.id;
      editForm.current_balance = data.myAccount.currentBalance;
      editForm.active = data.myAccount.active;
    } else {
      error.value = "Cuenta no encontrada";
    }
  } catch (err) {
    console.error("Error al cargar cuenta:", err);
    error.value = "No se pudo cargar la cuenta.";
  } finally {
    loading.value = false;
  }
}

// Funciones de utilidad
function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("es-CL", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Funciones de edición
function startEditing() {
  isEditing.value = true;
}

function cancelEdit() {
  isEditing.value = false;

  // Restaurar valores originales
  if (account.value) {
    editForm.name = account.value.name;
    editForm.account_number = account.value.accountNumber || "";
    editForm.bank_id = account.value.bank.id;
    editForm.account_type_id = account.value.accountType.id;
    editForm.current_balance = account.value.currentBalance;
    editForm.active = account.value.active;
  }
}

async function updateAccount() {
  try {
    saving.value = true;

    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(
      `${apiUrl}/api/v1/accounts/${props.accountId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authStore.accessToken}`,
        },
        body: JSON.stringify(editForm),
      }
    );

    if (!response.ok) {
      throw new Error(`Error al actualizar cuenta: ${response.statusText}`);
    }

    // Recargar datos de la cuenta
    await fetchAccount();
    isEditing.value = false;
  } catch (err) {
    console.error("Error al actualizar cuenta:", err);
    error.value = "No se pudo actualizar la cuenta.";
  } finally {
    saving.value = false;
  }
}

function retryFetch() {
  fetchAccount();
}

// Inicializar
onMounted(async () => {
  if (!authStore.accessToken) {
    window.location.href =
      "/auth/login?returnTo=/dashboard/accounts/" + props.accountId;
    return;
  }

  if (!props.accountId) {
    error.value = "No se especificó un ID de cuenta válido";
    loading.value = false;
    return;
  }

  await fetchAccount();
});
</script>
