<template>
  <div class="max-w-6xl mx-auto">
    <!-- Header -->
    <div class="bg-white shadow sm:rounded-lg mb-6">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">
              Perfiles de Importación
            </h3>
            <p class="mt-1 text-sm text-gray-500">
              Configura cómo mapear las columnas de tus archivos CSV, Excel
              según el banco
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="createDefaultProfiles"
              :disabled="creatingDefaults"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <span v-if="creatingDefaults">Creando...</span>
              <span v-else>Crear Perfiles por Defecto</span>
            </button>
            <button
              @click="showCreateModal = true"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Nuevo Perfil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="bg-white shadow sm:rounded-lg mb-6 p-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Filtrar por cuenta
          </label>
          <select
            v-model="selectedAccountFilter"
            @change="fetchProfiles"
            class="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">Todas las cuentas</option>
            <option
              v-for="account in accounts"
              :key="account.id"
              :value="account.id"
            >
              {{ account.name }} ({{ account.bank?.name }})
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Lista de perfiles -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div v-if="loading" class="p-8 text-center">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"
        ></div>
      </div>

      <div v-else-if="error" class="p-8 text-center text-red-600">
        {{ error }}
        <button
          @click="fetchProfiles"
          class="mt-2 block mx-auto text-sm text-primary-600 hover:text-primary-800"
        >
          Reintentar
        </button>
      </div>

      <div v-else-if="!profiles.length" class="p-8 text-center text-gray-500">
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
        <p>No tienes perfiles de importación configurados</p>
        <p class="text-sm mt-1">
          Crea uno nuevo o usa los perfiles por defecto
        </p>
      </div>

      <div v-else>
        <ul class="divide-y divide-gray-200">
          <li
            v-for="profile in profiles"
            :key="profile.id"
            class="hover:bg-gray-50"
          >
            <div class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center">
                    <h4 class="text-sm font-medium text-gray-900">
                      {{ profile.name }}
                      <span
                        v-if="profile.is_default"
                        class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                      >
                        Por defecto
                      </span>
                    </h4>
                  </div>
                  <div class="mt-1 text-sm text-gray-500">
                    <p>{{ profile.description || "Sin descripción" }}</p>
                    <p class="mt-1">
                      <strong>Cuenta:</strong>
                      {{ getAccountName(profile.account_id) }} •
                      <strong>Delimitador:</strong> "{{ profile.delimiter }}" •
                      <strong>Formato fecha:</strong> {{ profile.date_format }}
                      <span v-if="profile.sheet_name">
                        • <strong>Hoja:</strong> {{ profile.sheet_name }}
                      </span>
                      <span v-if="profile.header_row && profile.header_row > 1">
                        • <strong>Fila encabezado:</strong>
                        {{ profile.header_row }}
                      </span>
                    </p>
                  </div>

                  <!-- Mapeos de columnas -->
                  <div class="mt-3">
                    <h5 class="text-xs font-medium text-gray-700 mb-2">
                      Mapeo de columnas:
                    </h5>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="mapping in profile.column_mappings"
                        :key="mapping.id"
                        class="inline-flex items-center px-2 py-1 rounded text-xs"
                        :class="
                          mapping.is_required
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        "
                      >
                        {{ mapping.source_column_name }} →
                        {{ getTargetFieldLabel(mapping.target_field_name) }}
                        <span
                          v-if="mapping.is_required"
                          class="ml-1 text-blue-600"
                          >*</span
                        >
                      </span>
                    </div>
                  </div>
                </div>

                <div class="ml-4 flex items-center space-x-2">
                  <button
                    @click="editProfile(profile)"
                    class="text-primary-600 hover:text-primary-900 text-sm font-medium"
                  >
                    Editar
                  </button>
                  <button
                    @click="confirmDelete(profile)"
                    class="text-red-600 hover:text-red-900 text-sm font-medium"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Modal de crear/editar perfil -->
    <ImportProfileModal
      v-if="showCreateModal || editingProfile"
      :profile="editingProfile"
      :accounts="accounts"
      @close="closeModal"
      @saved="onProfileSaved"
    />

    <!-- Modal de confirmación de eliminación -->
    <div
      v-if="profileToDelete"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
      >
        <div class="mt-3 text-center">
          <h3 class="text-lg font-medium text-gray-900">Eliminar Perfil</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">
              ¿Estás seguro de que quieres eliminar el perfil "{{
                profileToDelete.name
              }}"? Esta acción no se puede deshacer.
            </p>
          </div>
          <div class="items-center px-4 py-3">
            <div class="flex justify-center space-x-3">
              <button
                @click="profileToDelete = null"
                class="px-4 py-2 bg-gray-300 text-gray-800 text-base font-medium rounded-md shadow-sm hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"
              >
                Cancelar
              </button>
              <button
                @click="deleteProfile"
                :disabled="deleting"
                class="px-4 py-2 bg-red-600 text-white text-base font-medium rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
              >
                {{ deleting ? "Eliminando..." : "Eliminar" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";
import ImportProfileModal from "./ImportProfileModal.vue";

const authStore = useAuthStore();

// Estado
const profiles = ref([]);
const accounts = ref([]);
const loading = ref(false);
const error = ref(null);
const showCreateModal = ref(false);
const editingProfile = ref(null);
const profileToDelete = ref(null);
const deleting = ref(false);
const creatingDefaults = ref(false);
const selectedAccountFilter = ref("");

// Funciones de API
async function apiRequest(url, options = {}) {
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  const response = await fetch(`${apiUrl}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authStore.accessToken}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Error HTTP: ${response.status}`);
  }

  return response.json();
}

async function fetchProfiles() {
  loading.value = true;
  error.value = null;

  try {
    const params = selectedAccountFilter.value
      ? `?account_id=${selectedAccountFilter.value}`
      : "";
    profiles.value = await apiRequest(`/api/v1/import-profiles${params}`);
  } catch (err) {
    console.error("Error al obtener perfiles:", err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

// GraphQL query para obtener las cuentas
const GET_ACCOUNTS_QUERY = `
  query GetAccounts($activeOnly: Boolean = true) {
    accounts(activeOnly: $activeOnly) {
      id
      name
      accountNumber
      accountType {
        id
        name
      }
      bank {
        id
        name
        code
        logoUrl
      }
      balance
      active
      createdAt
      updatedAt
    }
  }
`;

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
  try {
    // Realizar consulta GraphQL para obtener cuentas activas
    const data = await graphqlRequest(GET_ACCOUNTS_QUERY, { activeOnly: true });
    accounts.value = data.accounts || [];
  } catch (err) {
    console.error("Error al cargar cuentas:", err);

    // Manejar errores de autenticación
    if (
      err.message.includes("401") ||
      err.message.includes("Credenciales inválidas")
    ) {
      const refreshed = await authStore.refreshAuthToken();
      if (refreshed) {
        return fetchAccounts(); // Reintentar con el nuevo token
      } else {
        window.location.href =
          "/auth/login?returnTo=/dashboard/transactions/profiles";
        return;
      }
    }

    error.value = "No se pudieron cargar las cuentas disponibles.";
  }
}

async function createDefaultProfiles() {
  creatingDefaults.value = true;

  try {
    await apiRequest("/api/import-profiles/create-defaults", {
      method: "POST",
    });
    await fetchProfiles();
    alert("Perfiles por defecto creados exitosamente");
  } catch (err) {
    console.error("Error creando perfiles por defecto:", err);
    alert(`Error: ${err.message}`);
  } finally {
    creatingDefaults.value = false;
  }
}

async function deleteProfile() {
  if (!profileToDelete.value) return;

  deleting.value = true;

  try {
    await apiRequest(`/api/import-profiles/${profileToDelete.value.id}`, {
      method: "DELETE",
    });
    await fetchProfiles();
    profileToDelete.value = null;
  } catch (err) {
    console.error("Error eliminando perfil:", err);
    alert(`Error: ${err.message}`);
  } finally {
    deleting.value = false;
  }
}

// Funciones auxiliares
function getAccountName(accountId) {
  const account = accounts.value.find((a) => a.id === accountId);
  return account
    ? `${account.name} (${account.bank?.name})`
    : "Cuenta desconocida";
}

function getTargetFieldLabel(field) {
  const labels = {
    date: "Fecha",
    amount: "Monto",
    description: "Descripción",
    notes: "Notas",
    category: "Categoría",
    reference: "Referencia",
    account_number: "Número de Cuenta",
  };
  return labels[field] || field;
}

function editProfile(profile) {
  editingProfile.value = { ...profile };
}

function confirmDelete(profile) {
  profileToDelete.value = profile;
}

function closeModal() {
  showCreateModal.value = false;
  editingProfile.value = null;
}

function onProfileSaved() {
  closeModal();
  fetchProfiles();
}

onMounted(async () => {
  await fetchAccounts();
  await fetchProfiles();
});
</script>
