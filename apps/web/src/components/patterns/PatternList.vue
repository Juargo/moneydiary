<template>
  <div class="space-y-6">
    <!-- Header con estadísticas -->
    <div class="bg-white p-6 rounded-lg shadow">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold text-gray-900">
          Patrones de Descripción
        </h1>
        <button
          @click="showCreateModal = true"
          class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 flex items-center space-x-2"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            ></path>
          </svg>
          <span>Nuevo Patrón</span>
        </button>
      </div>

      <!-- Estadísticas -->
      <div v-if="statistics" class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  ></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-blue-600">Total Patrones</p>
              <p class="text-2xl font-semibold text-blue-900">
                {{ statistics.totalPatterns }}
              </p>
            </div>
          </div>
        </div>

        <div class="bg-green-50 p-4 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-green-600">Activos</p>
              <p class="text-2xl font-semibold text-green-900">
                {{ statistics.activePatterns }}
              </p>
            </div>
          </div>
        </div>

        <div class="bg-purple-50 p-4 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  ></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-purple-600">Auto-aplicar</p>
              <p class="text-2xl font-semibold text-purple-900">
                {{ statistics.autoApplyPatterns }}
              </p>
            </div>
          </div>
        </div>

        <div class="bg-yellow-50 p-4 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  ></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-yellow-600">Coincidencias</p>
              <p class="text-2xl font-semibold text-yellow-900">
                {{ statistics.totalMatches }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Acciones Rápidas</h2>
      <div class="flex flex-wrap gap-3">
        <button
          @click="showTestModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <span>Probar Patrones</span>
        </button>

        <button
          @click="fetchSuggestions"
          class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center space-x-2"
          :disabled="loading"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            ></path>
          </svg>
          <span>{{ loading ? "Generando..." : "Generar Sugerencias" }}</span>
        </button>

        <button
          @click="toggleShowInactive"
          class="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 flex items-center space-x-2"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            ></path>
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            ></path>
          </svg>
          <span>{{
            showInactive ? "Ocultar Inactivos" : "Mostrar Inactivos"
          }}</span>
        </button>
      </div>
    </div>

    <!-- Lista de patrones -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading && patterns.length === 0" class="p-8 text-center">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"
        ></div>
        <p class="mt-2 text-gray-600">Cargando patrones...</p>
      </div>

      <div v-else-if="error" class="p-8 text-center text-red-600">
        {{ error }}
        <button
          @click="fetchPatterns()"
          class="mt-2 block mx-auto text-sm text-primary-600 hover:text-primary-800"
        >
          Reintentar
        </button>
      </div>

      <div
        v-else-if="filteredPatterns.length === 0"
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
            d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          />
        </svg>
        <p>No hay patrones creados</p>
        <p class="text-sm mt-1">
          Crea tu primer patrón para categorizar transacciones automáticamente
        </p>
      </div>

      <div v-else>
        <div class="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <p class="text-sm text-gray-700">
            {{ filteredPatterns.length }} patrón(es) encontrado(s)
          </p>
        </div>

        <div class="divide-y divide-gray-200">
          <PatternCard
            v-for="pattern in filteredPatterns"
            :key="pattern.id"
            :pattern="pattern"
            @edit="editPattern"
            @delete="deletePatternConfirm"
            @toggle-active="togglePatternActive"
            @apply="applyPatternToTransactions"
          />
        </div>
      </div>
    </div>

    <!-- Modales -->
    <PatternFormModal
      v-if="showCreateModal"
      :pattern="null"
      @close="showCreateModal = false"
      @save="onPatternSaved"
    />

    <PatternFormModal
      v-if="showEditModal && editingPattern"
      :pattern="editingPattern"
      @close="showEditModal = false"
      @save="onPatternSaved"
    />

    <PatternTestModal v-if="showTestModal" @close="showTestModal = false" />

    <PatternSuggestionsModal
      v-if="suggestions"
      :suggestions="suggestions"
      @close="clearSuggestions"
      @create-pattern="createPatternFromSuggestion"
    />

    <!-- Modal de confirmación para eliminar -->
    <ConfirmationModal
      v-if="patternToDelete"
      title="Eliminar Patrón"
      :message="`¿Estás seguro de que quieres eliminar el patrón '${patternToDelete.name}'?`"
      confirm-text="Eliminar"
      confirm-class="bg-red-600 hover:bg-red-700"
      @confirm="deletePatternConfirmed"
      @cancel="patternToDelete = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { usePatternStore } from "../../stores/patternStore";
import PatternCard from "./PatternCard.vue";
import PatternFormModal from "./PatternFormModal.vue";
import PatternTestModal from "./PatternTestModal.vue";
import PatternSuggestionsModal from "./PatternSuggestionsModal.vue";
import ConfirmationModal from "./ConfirmationModal.vue";

const patternStore = usePatternStore();

// Estado del componente
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showTestModal = ref(false);
const showInactive = ref(false);
const editingPattern = ref(null);
const patternToDelete = ref(null);

// Computed
const { patterns, loading, error, statistics, suggestions } = patternStore;

const {
  fetchPatterns,
  fetchStatistics,
  fetchSuggestions,
  deletePattern,
  updatePattern,
  createPattern,
  clearSuggestions,
} = patternStore;

const filteredPatterns = computed(() => {
  if (showInactive.value) {
    return patterns;
  }
  return patterns.filter((p) => p.isActive);
});

// Métodos
function toggleShowInactive() {
  showInactive.value = !showInactive.value;
}

function editPattern(pattern) {
  editingPattern.value = pattern;
  showEditModal.value = true;
}

function deletePatternConfirm(pattern) {
  patternToDelete.value = pattern;
}

async function deletePatternConfirmed() {
  if (patternToDelete.value) {
    try {
      await deletePattern(patternToDelete.value.id);
      patternToDelete.value = null;
    } catch (error) {
      console.error("Error deleting pattern:", error);
    }
  }
}

async function togglePatternActive(pattern) {
  try {
    await updatePattern(pattern.id, { isActive: !pattern.isActive });
  } catch (error) {
    console.error("Error toggling pattern:", error);
  }
}

async function applyPatternToTransactions(pattern) {
  try {
    const result = await patternStore.applyPattern(pattern.id);
    // Mostrar notificación de éxito
    alert(`Patrón aplicado a ${result.applied_count} transacciones`);
  } catch (error) {
    console.error("Error applying pattern:", error);
  }
}

function onPatternSaved() {
  showCreateModal.value = false;
  showEditModal.value = false;
  editingPattern.value = null;
  fetchPatterns(!showInactive.value);
}

function createPatternFromSuggestion(suggestion) {
  // Abrir modal de creación con datos pre-llenos
  editingPattern.value = {
    name: `Patrón para: ${suggestion.descriptionSample}`,
    pattern: suggestion.suggestedPattern,
    patternType: suggestion.patternType,
    subcategoryId: suggestion.suggestedSubcategoryId,
    priority: 50,
    isCaseSensitive: false,
    isActive: true,
    autoApply: true,
    notes: `Generado automáticamente. Confianza: ${(
      suggestion.confidenceScore * 100
    ).toFixed(1)}%`,
  };
  showCreateModal.value = true;
  clearSuggestions();
}

// Inicialización
onMounted(async () => {
  await Promise.all([fetchPatterns(true), fetchStatistics()]);
});
</script>
