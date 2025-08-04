<template>
  <div class="max-w-6xl mx-auto">
    <!-- Selección de perfil y archivo -->
    <div v-if="!preview" class="space-y-6">
      <!-- Selección de perfil -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-blue-800 mb-3">
              Seleccionar Perfil de Importación
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-blue-700 mb-1">
                  Cuenta
                </label>
                <select
                  v-model="selectedAccountId"
                  @change="loadProfilesForAccount"
                  class="w-full border border-blue-300 rounded-md px-3 py-2 bg-white"
                >
                  <option value="">Selecciona una cuenta</option>
                  <option
                    v-for="account in accounts"
                    :key="account.id"
                    :value="account.id"
                  >
                    {{ account.name }} - {{ account.bank.name }} ({{
                      account.accountNumber
                    }})
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-blue-700 mb-1">
                  Perfil de Importación
                </label>
                <select
                  v-model="selectedProfileId"
                  :disabled="!selectedAccountId || !availableProfiles.length"
                  class="w-full border border-blue-300 rounded-md px-3 py-2 bg-white disabled:bg-gray-100"
                >
                  <option value="">Selecciona un perfil</option>
                  <option
                    v-for="profile in availableProfiles"
                    :key="profile.id"
                    :value="profile.id"
                  >
                    {{ profile.name }}
                    <span v-if="profile.is_default"> (Por defecto)</span>
                  </option>
                </select>
              </div>
            </div>

            <div
              v-if="selectedProfile"
              class="mt-4 p-3 bg-white rounded border"
            >
              <h4 class="text-sm font-medium text-gray-900 mb-2">
                Configuración del perfil:
              </h4>
              <div class="text-xs text-gray-600 space-y-1">
                <p>
                  <strong>Descripción:</strong>
                  {{ selectedProfile.description || "Sin descripción" }}
                </p>
                <p>
                  <strong>Formato:</strong> {{ selectedProfile.date_format }},
                  delimitador "{{ selectedProfile.delimiter }}"
                </p>
                <div
                  class="mt-2"
                  v-if="selectedProfile.column_mappings?.length"
                >
                  <strong>Mapeos:</strong>
                  <span
                    v-for="mapping in selectedProfile.column_mappings"
                    :key="mapping.id"
                    class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-800"
                  >
                    {{ mapping.source_column_name }} →
                    {{ getTargetFieldLabel(mapping.target_field_name) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="ml-4">
            <a
              href="/dashboard/transactions/profiles"
              class="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Gestionar perfiles
            </a>
          </div>
        </div>
      </div>

      <!-- Selección de archivo -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          Seleccionar Archivo
        </h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Archivo Excel o CSV
            </label>
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              @change="handleFileSelect"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <p class="mt-1 text-sm text-gray-500">
              Formatos soportados: .xlsx, .xls, .csv
            </p>
          </div>

          <div v-if="selectedFile" class="bg-gray-50 p-3 rounded">
            <p class="text-sm text-gray-700">
              <strong>Archivo seleccionado:</strong> {{ selectedFile.name }}
            </p>
            <p class="text-sm text-gray-500">
              Tamaño: {{ formatFileSize(selectedFile.size) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Botón de previsualización -->
      <div class="flex justify-between items-center">
        <button
          @click="generatePreview"
          :disabled="!selectedProfileId || !selectedFile || loading"
          class="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <svg
            v-if="loading"
            class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
            xmlns="http://www.w3.org/2000/svg"
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
          <span v-if="loading">Generando previsualización...</span>
          <span v-else>Generar Previsualización</span>
        </button>

        <div v-if="loading" class="text-sm text-gray-600">
          Analizando el archivo y validando datos...
        </div>
      </div>
    </div>

    <!-- Previsualización de transacciones -->
    <div v-if="preview && !finalResult" class="space-y-6">
      <!-- Header de previsualización -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 mb-2">
              Previsualización de Importación
            </h2>
            <p class="text-sm text-gray-600">
              Revisa las transacciones antes de confirmar la importación
            </p>
          </div>
          <button
            @click="startOver"
            class="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Cargar otro archivo
          </button>
        </div>

        <!-- Estadísticas -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div class="bg-blue-50 p-4 rounded">
            <div class="text-2xl font-bold text-blue-600">
              {{ preview.total_records }}
            </div>
            <div class="text-sm text-blue-800">Total registros</div>
          </div>

          <div class="bg-green-50 p-4 rounded">
            <div class="text-2xl font-bold text-green-600">
              {{ preview.valid_transactions }}
            </div>
            <div class="text-sm text-green-800">Válidas</div>
          </div>

          <div class="bg-red-50 p-4 rounded">
            <div class="text-2xl font-bold text-red-600">
              {{ preview.invalid_transactions }}
            </div>
            <div class="text-sm text-red-800">Con errores</div>
          </div>

          <div class="bg-purple-50 p-4 rounded">
            <div class="text-2xl font-bold text-purple-600">
              {{ selectedTransactionCount }}
            </div>
            <div class="text-sm text-purple-800">Seleccionadas</div>
          </div>
        </div>

        <div class="mt-4 text-sm text-gray-600">
          <strong>Cuenta:</strong> {{ preview.account_name }} |
          <strong>Perfil:</strong> {{ preview.profile_name }}
        </div>
      </div>

      <!-- Controles -->
      <div class="bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input
                type="checkbox"
                :checked="allValidSelected"
                @change="toggleAllValid"
                class="mr-2"
              />
              <span class="text-sm font-medium">
                Seleccionar todas las válidas ({{ preview.valid_transactions }})
              </span>
            </label>

            <label class="flex items-center">
              <input type="checkbox" v-model="showOnlyErrors" class="mr-2" />
              <span class="text-sm text-gray-600"> Mostrar solo errores </span>
            </label>
          </div>

          <button
            @click="confirmImport"
            :disabled="selectedTransactionCount === 0 || confirming"
            class="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg
              v-if="confirming"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
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
            <span v-if="confirming">Importando...</span>
            <span v-else
              >Confirmar Importación ({{ selectedTransactionCount }})</span
            >
          </button>
        </div>
      </div>

      <!-- Tabla de transacciones -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  <input
                    type="checkbox"
                    :checked="allVisibleSelected"
                    @change="toggleAllVisible"
                    class="mr-2"
                  />
                  Sel.
                </th>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Fila
                </th>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Estado
                </th>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Fecha
                </th>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Descripción
                </th>
                <th
                  class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Monto
                </th>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Errores
                </th>
                <th
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="transaction in filteredTransactions"
                :key="transaction.row_number"
                :class="{
                  'bg-red-50': !transaction.is_valid,
                  'bg-yellow-50': transaction.row_number === editingRow,
                }"
              >
                <td class="px-4 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    :disabled="
                      !transaction.is_valid &&
                      editingRow !== transaction.row_number
                    "
                    v-model="selectedTransactions"
                    :value="transaction.row_number"
                    class="disabled:opacity-50"
                  />
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ transaction.row_number }}
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                  <span
                    :class="{
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium': true,
                      'bg-green-100 text-green-800': transaction.is_valid,
                      'bg-red-100 text-red-800': !transaction.is_valid,
                    }"
                  >
                    {{ transaction.is_valid ? "Válida" : "Error" }}
                  </span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  <input
                    v-if="editingRow === transaction.row_number"
                    type="date"
                    v-model="editingData.transaction_date"
                    class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                  />
                  <span v-else>
                    {{
                      formatDate(transaction.transaction_date) || "Sin fecha"
                    }}
                  </span>
                </td>
                <td class="px-4 py-4 text-sm text-gray-900">
                  <input
                    v-if="editingRow === transaction.row_number"
                    type="text"
                    v-model="editingData.description"
                    class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    placeholder="Descripción"
                  />
                  <span v-else>
                    {{ transaction.description || "Sin descripción" }}
                  </span>
                </td>
                <td
                  class="px-4 py-4 whitespace-nowrap text-right text-sm font-medium"
                >
                  <input
                    v-if="editingRow === transaction.row_number"
                    type="number"
                    step="0.01"
                    v-model="editingData.amount"
                    class="w-full border border-gray-300 rounded px-2 py-1 text-sm text-right"
                    placeholder="0.00"
                  />
                  <span
                    v-else
                    :class="{
                      'text-green-600':
                        transaction.amount && transaction.amount > 0,
                      'text-red-600':
                        transaction.amount && transaction.amount < 0,
                      'text-gray-400': !transaction.amount,
                    }"
                  >
                    {{
                      transaction.amount
                        ? formatCurrency(transaction.amount)
                        : "Sin monto"
                    }}
                  </span>
                </td>
                <td class="px-4 py-4 text-sm text-red-600">
                  <div v-if="transaction.validation_errors?.length">
                    <ul class="text-xs space-y-1">
                      <li
                        v-for="error in transaction.validation_errors"
                        :key="error"
                      >
                        • {{ error }}
                      </li>
                    </ul>
                  </div>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm">
                  <div class="flex space-x-2">
                    <button
                      v-if="editingRow !== transaction.row_number"
                      @click="startEditing(transaction)"
                      class="text-blue-600 hover:text-blue-800 text-xs"
                    >
                      Editar
                    </button>
                    <template v-else>
                      <button
                        @click="saveEdit(transaction.row_number)"
                        class="text-green-600 hover:text-green-800 text-xs"
                      >
                        Guardar
                      </button>
                      <button
                        @click="cancelEdit"
                        class="text-gray-600 hover:text-gray-800 text-xs"
                      >
                        Cancelar
                      </button>
                    </template>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Resultado final -->
    <div
      v-if="finalResult"
      class="bg-white border border-gray-200 rounded-lg p-6"
    >
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        Importación Completada
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="bg-blue-50 p-4 rounded">
          <div class="text-2xl font-bold text-blue-600">
            {{ finalResult.total_records }}
          </div>
          <div class="text-sm text-blue-800">Total procesadas</div>
        </div>

        <div class="bg-green-50 p-4 rounded">
          <div class="text-2xl font-bold text-green-600">
            {{ finalResult.successful_imports }}
          </div>
          <div class="text-sm text-green-800">Importadas exitosamente</div>
        </div>

        <div class="bg-red-50 p-4 rounded">
          <div class="text-2xl font-bold text-red-600">
            {{ finalResult.failed_imports }}
          </div>
          <div class="text-sm text-red-800">Errores</div>
        </div>
      </div>

      <div v-if="finalResult.errors?.length" class="mt-4">
        <h4 class="text-sm font-medium text-red-800 mb-2">
          Errores encontrados:
        </h4>
        <div
          class="bg-red-50 border border-red-200 rounded p-3 max-h-40 overflow-y-auto"
        >
          <ul class="text-sm text-red-700 space-y-1">
            <li v-for="error in finalResult.errors" :key="error">
              {{ error }}
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-6 flex space-x-4">
        <button
          @click="startOver"
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
        >
          Importar Otro Archivo
        </button>
        <a
          href="/dashboard/transactions"
          class="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 inline-block"
        >
          Ver Transacciones
        </a>
      </div>
    </div>

    <!-- Error global -->
    <div
      v-if="error"
      class="bg-red-50 border border-red-200 rounded-lg p-4 mt-4"
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
          <div class="mt-2 text-sm text-red-700">
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

const authStore = useAuthStore();

// Estado
const accounts = ref([]);
const profiles = ref([]);
const selectedAccountId = ref("");
const selectedProfileId = ref("");
const availableProfiles = ref([]);
const selectedFile = ref(null);
const loading = ref(false);
const confirming = ref(false);
const error = ref(null);

// Estados de previsualización
const preview = ref(null);
const selectedTransactions = ref([]);
const finalResult = ref(null);

// Estados de edición
const editingRow = ref(null);
const editingData = ref({});
const modifications = ref({});

// Estados de filtro
const showOnlyErrors = ref(false);

// GraphQL query para obtener las cuentas del usuario
const GET_MY_ACCOUNTS_QUERY = `
  query GetMyAccounts {
    myAccounts {
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

// Computed properties
const selectedProfile = computed(() => {
  return profiles.value.find((p) => p.id === selectedProfileId.value);
});

const selectedTransactionCount = computed(() => {
  return selectedTransactions.value.length;
});

const filteredTransactions = computed(() => {
  if (!preview.value?.transactions) return [];

  if (showOnlyErrors.value) {
    return preview.value.transactions.filter((t) => !t.is_valid);
  }

  return preview.value.transactions;
});

const allValidSelected = computed(() => {
  if (!preview.value?.transactions) return false;

  const validTransactions = preview.value.transactions.filter(
    (t) => t.is_valid
  );
  return (
    validTransactions.length > 0 &&
    validTransactions.every((t) =>
      selectedTransactions.value.includes(t.row_number)
    )
  );
});

const allVisibleSelected = computed(() => {
  const visibleTransactions = filteredTransactions.value.filter(
    (t) => t.is_valid || editingRow.value === t.row_number
  );
  return (
    visibleTransactions.length > 0 &&
    visibleTransactions.every((t) =>
      selectedTransactions.value.includes(t.row_number)
    )
  );
});

// Funciones
async function apiRequest(url, options = {}) {
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${apiUrl}${url}`, {
    headers: {
      Authorization: `Bearer ${authStore.accessToken}`,
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Error ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}

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

async function fetchAccounts() {
  loading.value = true;

  try {
    if (!authStore.accessToken) {
      window.location.href =
        "/auth/login?returnTo=/dashboard/transactions/import";
      return;
    }

    const data = await graphqlRequest(GET_MY_ACCOUNTS_QUERY);
    accounts.value = data.myAccounts || [];
  } catch (err) {
    console.error("Error al obtener cuentas:", err);

    if (
      err.message.includes("401") ||
      err.message.includes("Credenciales inválidas")
    ) {
      const refreshed = await authStore.refreshAuthToken();
      if (refreshed) {
        return fetchAccounts();
      } else {
        window.location.href =
          "/auth/login?returnTo=/dashboard/transactions/import";
        return;
      }
    }

    error.value =
      err.message ||
      "No se pudieron cargar las cuentas. Por favor, intenta nuevamente.";
  } finally {
    loading.value = false;
  }
}

async function fetchProfiles() {
  try {
    profiles.value = await apiRequest("/api/v1/import-profiles");
  } catch (err) {
    console.error("Error al obtener perfiles:", err);
  }
}

function loadProfilesForAccount() {
  if (selectedAccountId.value) {
    availableProfiles.value = profiles.value.filter(
      (p) => p.account_id === parseInt(selectedAccountId.value)
    );

    const defaultProfile = availableProfiles.value.find((p) => p.is_default);
    if (defaultProfile) {
      selectedProfileId.value = defaultProfile.id;
    } else {
      selectedProfileId.value = "";
    }
  } else {
    availableProfiles.value = [];
    selectedProfileId.value = "";
  }
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    preview.value = null;
    finalResult.value = null;
    error.value = null;
  }
}

async function generatePreview() {
  if (!selectedProfileId.value || !selectedFile.value) {
    error.value = "Por favor selecciona un perfil de importación y un archivo";
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const formData = new FormData();
    formData.append("profile_id", selectedProfileId.value);
    formData.append("file", selectedFile.value);

    const response = await fetch(
      `${apiUrl}/api/v1/transactions/preview-import`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}`);
    }

    preview.value = await response.json();

    // Seleccionar automáticamente todas las transacciones válidas
    selectedTransactions.value = preview.value.transactions
      .filter((t) => t.is_valid)
      .map((t) => t.row_number);

    console.log("Previsualización generada:", preview.value);
  } catch (err) {
    console.error("Error generando previsualización:", err);
    error.value = `Error al generar previsualización: ${err.message}`;
  } finally {
    loading.value = false;
  }
}

async function confirmImport() {
  if (selectedTransactionCount.value === 0) {
    error.value = "Por favor selecciona al menos una transacción para importar";
    return;
  }

  confirming.value = true;
  error.value = null;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const confirmRequest = {
      preview_id: preview.value.preview_id,
      selected_transactions: selectedTransactions.value,
      modifications:
        Object.keys(modifications.value).length > 0
          ? modifications.value
          : null,
    };

    const response = await fetch(
      `${apiUrl}/api/v1/transactions/confirm-import`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authStore.accessToken}`,
        },
        body: JSON.stringify(confirmRequest),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}`);
    }

    finalResult.value = await response.json();
    preview.value = null; // Limpiar preview

    console.log("Importación completada:", finalResult.value);
  } catch (err) {
    console.error("Error confirmando importación:", err);
    error.value = `Error al confirmar importación: ${err.message}`;
  } finally {
    confirming.value = false;
  }
}

function toggleAllValid() {
  if (!preview.value?.transactions) return;

  const validTransactions = preview.value.transactions.filter(
    (t) => t.is_valid
  );

  if (allValidSelected.value) {
    // Deseleccionar todas las válidas
    selectedTransactions.value = selectedTransactions.value.filter(
      (rowNum) => !validTransactions.some((t) => t.row_number === rowNum)
    );
  } else {
    // Seleccionar todas las válidas
    const validRowNumbers = validTransactions.map((t) => t.row_number);
    const newSelected = [
      ...new Set([...selectedTransactions.value, ...validRowNumbers]),
    ];
    selectedTransactions.value = newSelected;
  }
}

function toggleAllVisible() {
  const visibleTransactions = filteredTransactions.value.filter(
    (t) => t.is_valid || editingRow.value === t.row_number
  );

  if (allVisibleSelected.value) {
    // Deseleccionar todas las visibles
    selectedTransactions.value = selectedTransactions.value.filter(
      (rowNum) => !visibleTransactions.some((t) => t.row_number === rowNum)
    );
  } else {
    // Seleccionar todas las visibles válidas
    const visibleRowNumbers = visibleTransactions.map((t) => t.row_number);
    const newSelected = [
      ...new Set([...selectedTransactions.value, ...visibleRowNumbers]),
    ];
    selectedTransactions.value = newSelected;
  }
}

function startEditing(transaction) {
  editingRow.value = transaction.row_number;
  editingData.value = {
    amount: transaction.amount,
    description: transaction.description,
    transaction_date: transaction.transaction_date,
    notes: transaction.notes,
  };
}

function saveEdit(rowNumber) {
  // Guardar modificaciones
  modifications.value[rowNumber] = { ...editingData.value };

  // Actualizar la transacción en el preview
  const transaction = preview.value.transactions.find(
    (t) => t.row_number === rowNumber
  );
  if (transaction) {
    Object.assign(transaction, editingData.value);

    // Re-validar la transacción
    transaction.validation_errors = [];
    if (!transaction.amount || transaction.amount === 0) {
      transaction.validation_errors.push("Monto requerido");
    }
    if (!transaction.transaction_date) {
      transaction.validation_errors.push("Fecha de transacción requerida");
    }
    if (!transaction.description) {
      transaction.validation_errors.push("Descripción requerida");
    }

    transaction.is_valid = transaction.validation_errors.length === 0;

    // Si ahora es válida y no estaba seleccionada, seleccionarla
    if (
      transaction.is_valid &&
      !selectedTransactions.value.includes(rowNumber)
    ) {
      selectedTransactions.value.push(rowNumber);
    }
  }

  cancelEdit();
}

function cancelEdit() {
  editingRow.value = null;
  editingData.value = {};
}

function startOver() {
  preview.value = null;
  finalResult.value = null;
  selectedTransactions.value = [];
  modifications.value = {};
  selectedFile.value = null;
  editingRow.value = null;
  editingData.value = {};
  error.value = null;

  // Reset file input
  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) {
    fileInput.value = "";
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function formatDate(dateString) {
  if (!dateString) return null;
  try {
    return new Date(dateString).toLocaleDateString("es-CL");
  } catch {
    return dateString;
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
  }).format(amount);
}

function getTargetFieldLabel(fieldName) {
  const labels = {
    date: "Fecha",
    description: "Descripción",
    amount: "Monto",
    debit_amount: "Débito",
    credit_amount: "Crédito",
    expense_amount: "Gasto",
    income_amount: "Ingreso",
    notes: "Notas",
    reference: "Referencia",
  };
  return labels[fieldName] || fieldName;
}

// Inicialización
onMounted(async () => {
  await fetchAccounts();
  await fetchProfiles();
});
</script>
