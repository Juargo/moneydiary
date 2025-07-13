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
                Banco
              </label>
              <select
                v-model="selectedBankId"
                @change="loadProfilesForBank"
                class="w-full border border-blue-300 rounded-md px-3 py-2 bg-white"
              >
                <option value="">Selecciona un banco</option>
                <option v-for="bank in banks" :key="bank.id" :value="bank.id">
                  {{ bank.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-blue-700 mb-1">
                Perfil
              </label>
              <select
                v-model="selectedProfileId"
                :disabled="!selectedBankId || !availableProfiles.length"
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
              <div class="mt-2">
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

    <!-- Resto del formulario existente -->
    <!-- ... (mantener el resto del formulario de importación) ... -->

    <!-- En la función handleImport, agregar el profile_id -->
  </div>
</template>

<script setup>
// ... existing imports ...

// Estado adicional para perfiles
const profiles = ref([]);
const selectedBankId = ref("");
const selectedProfileId = ref("");
const availableProfiles = ref([]);

const selectedProfile = computed(() => {
  return profiles.value.find((p) => p.id === selectedProfileId.value);
});

// ... existing functions ...

async function fetchProfiles() {
  try {
    profiles.value = await apiRequest("/api/v1/import-profiles");
  } catch (err) {
    console.error("Error al obtener perfiles:", err);
  }
}

function loadProfilesForBank() {
  if (selectedBankId.value) {
    availableProfiles.value = profiles.value.filter(
      (p) => p.bank_id === parseInt(selectedBankId.value)
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

async function handleImport() {
  if (!selectedAccountId.value || !selectedFile.value) {
    alert("Por favor selecciona una cuenta y un archivo Excel");
    return;
  }

  if (!selectedProfileId.value) {
    alert("Por favor selecciona un perfil de importación");
    return;
  }

  loading.value = true;
  importResult.value = null;

  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const formData = new FormData();
    formData.append("account_id", selectedAccountId.value);
    formData.append("profile_id", selectedProfileId.value); // Agregar profile_id
    formData.append("file", selectedFile.value);

    const response = await fetch(`${apiUrl}/api/transactions/import-excel`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
      body: formData,
    });

    // ... resto del manejo de respuesta
  } catch (err) {
    console.error("Error en la importación:", err);
    alert(`Error al importar: ${err.message}`);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchAccounts();
  await fetchProfiles();
});
</script>
