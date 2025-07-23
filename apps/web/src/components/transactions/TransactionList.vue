<!-- filepath: /Users/juargo/Documents/GitHub/moneydiary/apps/web/src/components/transactions/TransactionList.vue -->
<template>
  <div>
    <!-- Filtros -->
    <div class="bg-white p-4 rounded-lg shadow mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Cuenta
          </label>
          <select
            v-model="filters.accountId"
            @change="resetAndFetch"
            class="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">Todas las cuentas</option>
            <option
              v-for="account in accounts"
              :key="account.id"
              :value="account.id"
            >
              {{ account.name }} - {{ account.bank?.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Desde
          </label>
          <input
            v-model="filters.startDate"
            @change="resetAndFetch"
            type="date"
            class="w-full border border-gray-300 rounded-md px-3 py-2"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Hasta
          </label>
          <input
            v-model="filters.endDate"
            @change="resetAndFetch"
            type="date"
            class="w-full border border-gray-300 rounded-md px-3 py-2"
          />
        </div>

        <div class="flex items-end">
          <button
            @click="resetAndFetch"
            class="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
          >
            Filtrar
          </button>
        </div>
      </div>
    </div>

    <!-- Lista de transacciones -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"
        ></div>
      </div>

      <div v-else-if="error" class="p-8 text-center text-red-600">
        {{ error }}
        <button
          @click="fetchTransactions"
          class="mt-2 block mx-auto text-sm text-primary-600 hover:text-primary-800"
        >
          Reintentar
        </button>
      </div>

      <div
        v-else-if="!transactions.length"
        class="p-8 text-center text-gray-500"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-12 w-12 mx-auto mb-4 text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <p>No se encontraron transacciones</p>
        <p class="text-sm mt-1">
          Prueba ajustando los filtros o importa algunas transacciones
        </p>
      </div>

      <div v-else>
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Fecha
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Descripción
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Cuenta
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Monto
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="transaction in transactions"
              :key="transaction.id"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDate(transaction.transaction_date) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">
                <div>{{ transaction.description || "Sin descripción" }}</div>
                <div
                  v-if="transaction.notes"
                  class="text-xs text-gray-500 mt-1"
                >
                  {{ transaction.notes }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ getAccountName(transaction.account_id) }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                :class="
                  transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
                "
              >
                {{ formatCurrency(transaction.amount) }}
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Paginación simple -->
        <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex justify-between items-center">
            <button
              @click="previousPage"
              :disabled="currentPage <= 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Anterior
            </button>
            <span class="text-sm text-gray-700">
              Página {{ currentPage }}
            </span>
            <button
              @click="nextPage"
              :disabled="currentPage * pageSize >= totalCount"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

const authStore = useAuthStore();

// Estado
const transactions = ref([]);
const accounts = ref([]);
const loading = ref(false);
const error = ref(null);
const currentPage = ref(1);
const totalCount = ref(0);
const pageSize = 50;

// Filtros
const filters = reactive({
  accountId: "",
  startDate: "",
  endDate: "",
});

// Funciones
async function fetchTransactions() {
  loading.value = true;
  error.value = null;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    // Construir filtros para la query
    const queryFilters = {};
    if (filters.accountId) {
      queryFilters.accountId = parseInt(filters.accountId);
    }
    if (filters.startDate) {
      queryFilters.startDate = filters.startDate;
    }
    if (filters.endDate) {
      queryFilters.endDate = filters.endDate;
    }

    // Calcular skip para paginación
    const skip = (currentPage.value - 1) * pageSize;

    const response = await fetch(`${apiUrl}/graphql`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authStore.accessToken}`,
      },
      body: JSON.stringify({
        query: `
          query GetMyTransactions($filters: TransactionFilters, $skip: Int, $limit: Int) {
            myTransactions(filters: $filters, skip: $skip, limit: $limit) {
              transactions {
                id
                amount
                description
                notes
                transactionDate
                accountId
                userId
                statusId
                isRecurring
                isPlanned
              }
              totalCount
            }
          }
        `,
        variables: {
          filters: Object.keys(queryFilters).length > 0 ? queryFilters : null,
          skip: skip,
          limit: pageSize,
        },
      }),
    });

    const data = await response.json();

    if (data.errors) {
      throw new Error(data.errors[0].message);
    }

    if (data.data && data.data.myTransactions) {
      transactions.value = data.data.myTransactions.transactions.map((t) => ({
        id: t.id,
        amount: parseFloat(t.amount),
        description: t.description,
        notes: t.notes,
        transaction_date: t.transactionDate,
        account_id: t.accountId,
        user_id: t.userId,
        status_id: t.statusId,
        is_recurring: t.isRecurring,
        is_planned: t.isPlanned,
      }));
      totalCount.value = data.data.myTransactions.totalCount || 0;
      console.log(
        `Transacciones cargadas: ${transactions.value.length} de ${totalCount.value} total`
      );
    } else {
      transactions.value = [];
      totalCount.value = 0;
    }
  } catch (err) {
    console.error("Error al obtener transacciones:", err);
    error.value = err.message || "Error al cargar transacciones";
  } finally {
    loading.value = false;
  }
}

async function fetchAccounts() {
  try {
    // Reutilizar la lógica del AccountList
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const response = await fetch(`${apiUrl}/graphql`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authStore.accessToken}`,
      },
      body: JSON.stringify({
        query: `
          query GetMyAccounts {
            myAccounts {
              id
              name
              bank {
                name
              }
            }
          }
        `,
      }),
    });

    const data = await response.json();
    if (data.data) {
      accounts.value = data.data.myAccounts || [];
    }
  } catch (err) {
    console.error("Error al obtener cuentas:", err);
  }
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("es-CL");
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
  }).format(amount);
}

function getAccountName(accountId) {
  const account = accounts.value.find((a) => a.id === accountId);
  return account
    ? `${account.name} - ${account.bank?.name}`
    : "Cuenta desconocida";
}

function resetAndFetch() {
  currentPage.value = 1;
  fetchTransactions();
}

function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchTransactions();
  }
}

function nextPage() {
  const hasMorePages = currentPage.value * pageSize < totalCount.value;
  if (hasMorePages) {
    currentPage.value++;
    fetchTransactions();
  }
}

onMounted(async () => {
  await fetchAccounts();
  await fetchTransactions();
});
</script>
