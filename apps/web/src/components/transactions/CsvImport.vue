<!-- filepath: /Users/juargo/Documents/GitHub/moneydiary/apps/web/src/components/transactions/CsvImport.vue -->
<template>
  <div class="max-w-4xl mx-auto">
    <!-- Información sobre el formato CSV -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-blue-800">
            Formato requerido para el archivo CSV
          </h3>
          <div class="mt-2 text-sm text-blue-700">
            <p>El archivo CSV debe contener las siguientes columnas:</p>
            <ul class="mt-2 list-disc list-inside space-y-1">
              <li>
                <strong>date o fecha:</strong> Fecha de la transacción
                (YYYY-MM-DD)
              </li>
              <li>
                <strong>amount o monto:</strong> Monto de la transacción
                (números, negativos para gastos)
              </li>
              <li>
                <strong>description o descripcion:</strong> Descripción de la
                transacción
              </li>
              <li>
                <strong>notes o notas:</strong> Notas adicionales (opcional)
              </li>
            </ul>
            <p class="mt-2">
              <strong>Ejemplo:</strong>
              <code class="bg-white px-1 rounded"
                >date,amount,description,notes</code
              >
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Formulario de importación -->
    <div class="bg-white shadow rounded-lg p-6">
      <form @submit.prevent="handleImport">
        <!-- Selección de cuenta -->
        <div class="mb-6">
          <label
            for="account"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            Cuenta de destino *
          </label>
          <select
            id="account"
            v-model="selectedAccountId"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            :disabled="loading"
          >
            <option value="">Selecciona una cuenta</option>
            <option
              v-for="account in accounts"
              :key="account.id"
              :value="account.id"
            >
              {{ account.name }} - {{ account.bank?.name || "Sin banco" }}
            </option>
          </select>
        </div>

        <!-- Subida de archivo -->
        <div class="mb-6">
          <label
            for="file"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            Archivo CSV *
          </label>
          <div
            class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md"
            :class="{ 'border-primary-400 bg-primary-50': dragOver }"
            @drop.prevent="handleFileDrop"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
          >
            <div class="space-y-1 text-center">
              <svg
                class="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <div class="flex text-sm text-gray-600">
                <label
                  for="file-upload"
                  class="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                >
                  <span>Sube un archivo</span>
                  <input
                    id="file-upload"
                    ref="fileInput"
                    type="file"
                    accept=".csv"
                    class="sr-only"
                    @change="handleFileSelect"
                    :disabled="loading"
                  />
                </label>
                <p class="pl-1">o arrastra y suelta</p>
              </div>
              <p class="text-xs text-gray-500">Solo archivos CSV hasta 10MB</p>
            </div>
          </div>

          <!-- Archivo seleccionado -->
          <div
            v-if="selectedFile"
            class="mt-3 flex items-center justify-between p-3 bg-gray-50 rounded-md"
          >
            <div class="flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-gray-400 mr-2"
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
              <span class="text-sm text-gray-700">{{ selectedFile.name }}</span>
              <span class="ml-2 text-xs text-gray-500"
                >({{ formatFileSize(selectedFile.size) }})</span
              >
            </div>
            <button
              type="button"
              @click="clearFile"
              class="text-red-600 hover:text-red-800"
              :disabled="loading"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Botones -->
        <div class="flex justify-end space-x-3">
          <a
            href="/dashboard/transactions"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancelar
          </a>
          <button
            type="submit"
            :disabled="!selectedAccountId || !selectedFile || loading"
            class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div v-if="loading" class="flex items-center">
              <div
                class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
              ></div>
              Importando...
            </div>
            <span v-else>Importar Transacciones</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Resultados de importación -->
    <div v-if="importResult" class="mt-8 bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        Resultado de la Importación
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">
            {{ importResult.total_records }}
          </div>
          <div class="text-sm text-blue-800">Registros totales</div>
        </div>
        <div class="bg-green-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-green-600">
            {{ importResult.successful_imports }}
          </div>
          <div class="text-sm text-green-800">Importaciones exitosas</div>
        </div>
        <div class="bg-red-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-red-600">
            {{ importResult.failed_imports }}
          </div>
          <div class="text-sm text-red-800">Importaciones fallidas</div>
        </div>
      </div>

      <!-- Errores -->
      <div
        v-if="importResult.errors && importResult.errors.length > 0"
        class="mt-4"
      >
        <h4 class="text-sm font-medium text-red-800 mb-2">
          Errores encontrados:
        </h4>
        <ul class="bg-red-50 border border-red-200 rounded-md p-3 space-y-1">
          <li
            v-for="error in importResult.errors"
            :key="error"
            class="text-sm text-red-700"
          >
            {{ error }}
          </li>
        </ul>
      </div>

      <!-- Acciones después de importar -->
      <div class="mt-6 flex justify-end space-x-3">
        <button
          @click="resetImport"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Nueva Importación
        </button>
        <a
          href="/dashboard/transactions"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          Ver Transacciones
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

const authStore = useAuthStore();

// Estado
const accounts = ref([]);
const selectedAccountId = ref("");
const selectedFile = ref(null);
const loading = ref(false);
const dragOver = ref(false);
const importResult = ref(null);
const fileInput = ref(null);

// GraphQL para obtener cuentas
const GET_ACCOUNTS_QUERY = `
  query GetMyAccounts {
    myAccounts {
      id
      name
      bank {
        id
        name
      }
    }
  }
`;

// Funciones
async function graphqlRequest(query, variables = {}) {
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  const response = await fetch(`${apiUrl}/graphql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authStore.accessToken}`,
    },
    body: JSON.stringify({ query, variables }),
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
  try {
    const data = await graphqlRequest(GET_ACCOUNTS_QUERY);
    accounts.value = data.myAccounts || [];
  } catch (err) {
    console.error("Error al obtener cuentas:", err);
    alert("Error al cargar las cuentas");
  }
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    validateAndSetFile(file);
  }
}

function handleFileDrop(event) {
  dragOver.value = false;
  const file = event.dataTransfer.files[0];
  if (file) {
    validateAndSetFile(file);
  }
}

function validateAndSetFile(file) {
  // Validar tipo de archivo
  if (!file.name.toLowerCase().endsWith(".csv")) {
    alert("Por favor selecciona un archivo CSV válido");
    return;
  }

  // Validar tamaño (10MB máximo)
  if (file.size > 10 * 1024 * 1024) {
    alert("El archivo es demasiado grande. Máximo 10MB.");
    return;
  }

  selectedFile.value = file;

  // Actualizar el input file
  if (fileInput.value) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.value.files = dataTransfer.files;
  }
}

function clearFile() {
  selectedFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

async function handleImport() {
  if (!selectedAccountId.value || !selectedFile.value) {
    alert("Por favor selecciona una cuenta y un archivo CSV");
    return;
  }

  loading.value = true;
  importResult.value = null;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    // Crear FormData para la subida del archivo
    const formData = new FormData();
    formData.append("account_id", selectedAccountId.value);
    formData.append("file", selectedFile.value);

    const response = await fetch(`${apiUrl}/api/transactions/import-csv`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Error HTTP: ${response.status}`);
    }

    const result = await response.json();
    importResult.value = result;

    // Limpiar formulario si fue exitoso
    if (result.successful_imports > 0) {
      selectedAccountId.value = "";
      clearFile();
    }
  } catch (err) {
    console.error("Error en la importación:", err);
    alert(`Error al importar: ${err.message}`);
  } finally {
    loading.value = false;
  }
}

function resetImport() {
  importResult.value = null;
  selectedAccountId.value = "";
  clearFile();
}

onMounted(() => {
  fetchAccounts();
});
</script>
