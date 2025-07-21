<template>
  <div class="max-w-4xl mx-auto">
    <!-- Selección de perfil -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
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
                  {{ account.name }} - {{ account.bankName }}
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

          <div v-if="selectedProfile" class="mt-4 p-3 bg-white rounded border">
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
              <div class="mt-2" v-if="selectedProfile.column_mappings?.length">
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
    <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
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

    <!-- Botón de importación -->
    <div class="flex justify-between items-center mb-6">
      <button
        @click="handleImport"
        :disabled="!selectedProfileId || !selectedFile || loading"
        class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="loading">Procesando...</span>
        <span v-else>Importar Transacciones</span>
      </button>

      <div v-if="loading" class="text-sm text-gray-600">
        Por favor espera mientras se procesa el archivo...
      </div>
    </div>

    <!-- Resultados de importación -->
    <div
      v-if="importResult"
      class="bg-white border border-gray-200 rounded-lg p-6"
    >
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        Resultados de la Importación
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="bg-blue-50 p-4 rounded">
          <div class="text-2xl font-bold text-blue-600">
            {{ importResult.total_records }}
          </div>
          <div class="text-sm text-blue-800">Total de registros</div>
        </div>

        <div class="bg-green-50 p-4 rounded">
          <div class="text-2xl font-bold text-green-600">
            {{ importResult.successful_imports }}
          </div>
          <div class="text-sm text-green-800">Importados exitosamente</div>
        </div>

        <div class="bg-red-50 p-4 rounded">
          <div class="text-2xl font-bold text-red-600">
            {{ importResult.failed_imports }}
          </div>
          <div class="text-sm text-red-800">Errores</div>
        </div>
      </div>

      <div v-if="importResult.errors?.length" class="mt-4">
        <h4 class="text-sm font-medium text-red-800 mb-2">
          Errores encontrados:
        </h4>
        <div
          class="bg-red-50 border border-red-200 rounded p-3 max-h-40 overflow-y-auto"
        >
          <ul class="text-sm text-red-700 space-y-1">
            <li v-for="error in importResult.errors" :key="error">
              {{ error }}
            </li>
          </ul>
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
const importResult = ref(null);
const error = ref(null);

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

// Computed
const selectedProfile = computed(() => {
  return profiles.value.find((p) => p.id === selectedProfileId.value);
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
    throw new Error(`Error ${response.status}: ${response.statusText}`);
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

  // Verificar si hay errores de GraphQL
  if (data.errors) {
    throw new Error(data.errors[0]?.message || "Error en la consulta GraphQL");
  }

  return data.data;
}

async function fetchAccounts() {
  loading.value = true;
  error.value = null;

  try {
    if (!authStore.accessToken) {
      window.location.href = "/auth/login?returnTo=/dashboard/accounts";
      return;
    }

    // Realizar consulta GraphQL
    const data = await graphqlRequest(GET_MY_ACCOUNTS_QUERY);
    accounts.value = data.myAccounts || [];
  } catch (err) {
    console.error("Error al obtener cuentas:", err);

    // Manejar errores de autenticación
    if (
      err.message.includes("401") ||
      err.message.includes("Credenciales inválidas")
    ) {
      const refreshed = await authStore.refreshAuthToken();
      if (refreshed) {
        return fetchAccounts();
      } else {
        window.location.href = "/auth/login?returnTo=/dashboard/accounts";
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

    // Auto-seleccionar perfil por defecto si existe
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
    importResult.value = null; // Limpiar resultados anteriores
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
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

async function handleImport() {
  if (!selectedProfileId.value || !selectedFile.value) {
    alert("Por favor selecciona un perfil de importación y un archivo");
    return;
  }

  loading.value = true;
  importResult.value = null;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    // Determinar el endpoint según el tipo de archivo
    const isExcel = selectedFile.value.name
      .toLowerCase()
      .endsWith((".xlsx", ".xls"));
    const endpoint = isExcel
      ? "/api/v1/transactions/import-excel"
      : "/api/v1/transactions/import-csv";

    const formData = new FormData();
    formData.append("profile_id", selectedProfileId.value);
    formData.append("file", selectedFile.value);

    const response = await fetch(`${apiUrl}${endpoint}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Error ${response.status}`);
    }

    importResult.value = await response.json();

    if (importResult.value.successful_imports > 0) {
      // Opcional: recargar datos o notificar éxito
      console.log("Importación completada exitosamente");
    }
  } catch (err) {
    console.error("Error en la importación:", err);
    alert(`Error al importar: ${err.message}`);
  } finally {
    loading.value = false;
  }
}

// Inicialización
onMounted(async () => {
  await fetchAccounts();
  await fetchProfiles();
});
</script>
