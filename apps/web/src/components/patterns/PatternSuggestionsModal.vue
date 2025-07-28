<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
  >
    <div
      class="bg-white rounded-lg max-w-6xl w-full max-h-screen overflow-y-auto"
    >
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">
          Sugerencias de Patrones
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          Patrones sugeridos basados en las transacciones existentes
        </p>
      </div>

      <div class="p-6">
        <!-- Controles de filtrado -->
        <div class="mb-6 flex flex-wrap gap-4 items-center">
          <div class="flex items-center space-x-2">
            <label class="text-sm font-medium text-gray-700"
              >Mínimo de transacciones:</label
            >
            <select
              v-model="filters.minTransactions"
              @change="applySuggestions"
              class="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
          </div>

          <div class="flex items-center space-x-2">
            <label class="text-sm font-medium text-gray-700"
              >Ordenar por:</label
            >
            <select
              v-model="filters.sortBy"
              @change="applySuggestions"
              class="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value="frequency">Frecuencia</option>
              <option value="confidence">Confianza</option>
            </select>
          </div>

          <label class="flex items-center">
            <input
              v-model="filters.showWithSubcategory"
              @change="applySuggestions"
              type="checkbox"
              class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span class="ml-2 text-sm text-gray-700"
              >Incluir patrones con subcategoría sugerida</span
            >
          </label>

          <button
            @click="loadSuggestions"
            :disabled="loading"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 text-sm"
          >
            {{ loading ? "Cargando..." : "Actualizar" }}
          </button>
        </div>

        <!-- Estadísticas -->
        <div
          v-if="suggestions.length > 0"
          class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"
        >
          <div class="bg-blue-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-blue-900">
              {{ suggestions.length }}
            </div>
            <div class="text-sm text-blue-700">Sugerencias encontradas</div>
          </div>
          <div class="bg-green-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-green-900">
              {{ totalTransactions }}
            </div>
            <div class="text-sm text-green-700">Transacciones analizadas</div>
          </div>
          <div class="bg-yellow-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-yellow-900">
              {{ selectedCount }}
            </div>
            <div class="text-sm text-yellow-700">Sugerencias seleccionadas</div>
          </div>
          <div class="bg-purple-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-purple-900">
              {{ estimatedSavings }}
            </div>
            <div class="text-sm text-purple-700">
              Horas de categorización ahorradas
            </div>
          </div>
        </div>

        <!-- Lista de sugerencias -->
        <div v-if="suggestions.length > 0" class="space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">
              Patrones Sugeridos
            </h3>
            <div class="flex space-x-2">
              <button
                @click="selectAll"
                class="px-3 py-1 text-sm text-primary-600 hover:text-primary-800"
              >
                Seleccionar todo
              </button>
              <button
                @click="selectNone"
                class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Deseleccionar todo
              </button>
              <button
                @click="createSelectedPatterns"
                :disabled="selectedCount === 0 || creating"
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 text-sm"
              >
                {{
                  creating ? "Creando..." : `Crear ${selectedCount} patrón(es)`
                }}
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <div
              v-for="suggestion in sortedSuggestions"
              :key="suggestion.id"
              class="border rounded-lg p-4 hover:bg-gray-50"
              :class="{ 'ring-2 ring-primary-500': suggestion.selected }"
            >
              <div class="flex items-start space-x-4">
                <!-- Checkbox de selección -->
                <div class="flex-shrink-0 pt-1">
                  <input
                    v-model="suggestion.selected"
                    type="checkbox"
                    class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                </div>

                <!-- Contenido principal -->
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-start justify-between gap-4">
                    <!-- Información del patrón -->
                    <div class="flex-1 min-w-0">
                      <h4 class="font-medium text-gray-900 mb-2">
                        {{ suggestion.suggested_pattern }}
                      </h4>

                      <!-- Estadísticas -->
                      <div
                        class="flex flex-wrap gap-4 text-sm text-gray-600 mb-3"
                      >
                        <span class="flex items-center">
                          <svg
                            class="w-4 h-4 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            ></path>
                          </svg>
                          {{ suggestion.occurrence_count }} transacciones
                        </span>

                        <span class="flex items-center">
                          <svg
                            class="w-4 h-4 mr-1"
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
                          Tipo:
                          {{ getPatternTypeLabel(suggestion.pattern_type) }}
                        </span>

                        <span class="flex items-center">
                          <svg
                            class="w-4 h-4 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            ></path>
                          </svg>
                          Ejemplo: {{ suggestion.description_sample }}
                        </span>
                      </div>

                      <!-- Configuración del patrón -->
                      <div
                        v-if="suggestion.selected"
                        class="bg-gray-50 p-3 rounded border-l-4 border-primary-500"
                      >
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label
                              class="block text-sm font-medium text-gray-700 mb-1"
                            >
                              Nombre del patrón
                            </label>
                            <input
                              v-model="suggestion.patternName"
                              type="text"
                              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                              :placeholder="`Patrón para ${suggestion.suggested_pattern}`"
                            />
                          </div>

                          <div>
                            <label
                              class="block text-sm font-medium text-gray-700 mb-1"
                            >
                              Subcategoría
                            </label>
                            <select
                              v-model="suggestion.subcategoryId"
                              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            >
                              <option value="">Seleccionar subcategoría</option>
                              <optgroup
                                v-for="category in patternStore.categories"
                                :key="category.id"
                                :label="category.name"
                              >
                                <option
                                  v-for="subcategory in category.subcategories"
                                  :key="subcategory.id"
                                  :value="subcategory.id"
                                >
                                  {{ subcategory.name }}
                                </option>
                              </optgroup>
                            </select>
                          </div>

                          <div>
                            <label
                              class="block text-sm font-medium text-gray-700 mb-1"
                            >
                              Tipo de patrón
                            </label>
                            <select
                              v-model="suggestion.patternType"
                              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            >
                              <option value="contains">Contiene</option>
                              <option value="starts_with">Inicia con</option>
                              <option value="ends_with">Termina con</option>
                              <option value="exact">Exacto</option>
                            </select>
                          </div>

                          <div class="flex items-center space-x-4">
                            <label class="flex items-center">
                              <input
                                v-model="suggestion.autoApply"
                                type="checkbox"
                                class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                              />
                              <span class="ml-2 text-sm text-gray-700"
                                >Aplicar automáticamente</span
                              >
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Puntuación de confianza -->
                    <div class="flex-shrink-0">
                      <div class="text-center">
                        <div class="text-lg font-bold text-gray-900">
                          {{ Math.round(suggestion.confidence_score * 100) }}%
                        </div>
                        <div class="text-xs text-gray-500">Confianza</div>
                        <div class="w-16 bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            class="h-2 rounded-full"
                            :class="
                              getConfidenceColor(
                                Math.round(suggestion.confidence_score * 100)
                              )
                            "
                            :style="{
                              width:
                                Math.round(suggestion.confidence_score * 100) +
                                '%',
                            }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Estado de carga -->
        <div v-if="loading" class="text-center py-12">
          <div
            class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"
          ></div>
          <p class="mt-4 text-gray-600">
            Analizando transacciones para generar sugerencias...
          </p>
        </div>

        <!-- Estado vacío -->
        <div
          v-if="!loading && suggestions.length === 0"
          class="text-center py-12"
        >
          <svg
            class="w-16 h-16 mx-auto mb-4 text-gray-300"
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
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            No se encontraron sugerencias
          </h3>
          <p class="text-gray-600 mb-4">
            No hay suficientes transacciones repetidas para generar sugerencias
            de patrones.
          </p>
          <button
            @click="loadSuggestions"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Reintentar
          </button>
        </div>

        <!-- Estado de error -->
        <div v-if="error" class="bg-red-50 p-4 rounded-lg">
          <div class="flex">
            <svg
              class="h-5 w-5 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                Error al cargar sugerencias
              </h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
              <button
                @click="loadSuggestions"
                class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-between">
        <div class="text-sm text-gray-600">
          {{ selectedCount }} de {{ suggestions.length }} sugerencias
          seleccionadas
        </div>
        <div class="flex space-x-3">
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cerrar
          </button>
          <button
            @click="createSelectedPatterns"
            :disabled="selectedCount === 0 || creating"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            {{ creating ? "Creando..." : `Crear ${selectedCount} patrón(es)` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from "vue";
import { usePatternStore } from "../../stores/patternStore";

const emit = defineEmits(["close", "patternsCreated"]);

const patternStore = usePatternStore();
const { loading, error } = patternStore;

// Estado local
const suggestions = ref([]);
const creating = ref(false);

const filters = reactive({
  minTransactions: 2,
  sortBy: "frequency",
  showWithSubcategory: true,
});

// Computed
const selectedCount = computed(() => {
  return suggestions.value.filter((s) => s.selected).length;
});

const totalTransactions = computed(() => {
  return suggestions.value.reduce((total, s) => total + s.occurrence_count, 0);
});

const estimatedSavings = computed(() => {
  // Estimar 30 segundos por transacción categorizada manualmente
  const minutes = (totalTransactions.value * 0.5) / 60;
  return Math.round(minutes * 10) / 10;
});

const sortedSuggestions = computed(() => {
  const sorted = [...suggestions.value];

  switch (filters.sortBy) {
    case "frequency":
      return sorted.sort((a, b) => b.occurrence_count - a.occurrence_count);
    case "confidence":
      return sorted.sort((a, b) => b.confidence_score - a.confidence_score);
    default:
      return sorted.sort((a, b) => b.occurrence_count - a.occurrence_count);
  }
});

// Métodos
function getPatternTypeLabel(type) {
  const labels = {
    contains: "Contiene",
    starts_with: "Inicia con",
    ends_with: "Termina con",
    exact: "Exacto",
    regex: "Expresión regular",
  };
  return labels[type] || type;
}

function getConfidenceColor(confidence) {
  if (confidence >= 80) return "bg-green-500";
  if (confidence >= 60) return "bg-yellow-500";
  return "bg-red-500";
}

function selectAll() {
  suggestions.value.forEach((s) => (s.selected = true));
}

function selectNone() {
  suggestions.value.forEach((s) => (s.selected = false));
}

async function loadSuggestions() {
  try {
    const response = await patternStore.getPatternSuggestions({
      limit: 20,
      min_occurrences: filters.minTransactions,
    });

    // Procesar y enriquecer las sugerencias con el formato correcto del backend
    suggestions.value = response.suggestions.map((suggestion) => ({
      ...suggestion,
      id: Math.random().toString(36).substr(2, 9),
      selected: false,
      patternName: `Patrón ${suggestion.suggested_pattern}`,
      patternType: suggestion.pattern_type,
      autoApply: true,
      subcategoryId: suggestion.suggested_subcategory_id,
    }));
  } catch (err) {
    console.error("Error loading suggestions:", err);
  }
}

function applySuggestions() {
  // Recargar con los nuevos filtros
  loadSuggestions();
}

async function createSelectedPatterns() {
  const selected = suggestions.value.filter((s) => s.selected);

  if (selected.length === 0) return;

  // Validar que todas las sugerencias seleccionadas tengan subcategoría
  const invalid = selected.filter(
    (s) => !s.subcategoryId || !s.patternName.trim()
  );
  if (invalid.length > 0) {
    alert(
      `Por favor completa la información de ${invalid.length} patrón(es) seleccionado(s)`
    );
    return;
  }

  creating.value = true;

  try {
    const createdPatterns = [];

    for (const suggestion of selected) {
      const patternData = {
        name: suggestion.patternName.trim(),
        pattern: suggestion.suggested_pattern,
        patternType: suggestion.patternType,
        subcategoryId: suggestion.subcategoryId,
        isActive: true,
        autoApply: suggestion.autoApply,
        priority: 1,
        isCaseSensitive: false,
      };

      const created = await patternStore.createPattern(patternData);
      createdPatterns.push(created);
    }

    // Recargar patrones y cerrar modal
    await patternStore.loadPatterns();
    emit("patternsCreated", createdPatterns);
    emit("close");
  } catch (err) {
    console.error("Error creating patterns:", err);
    alert(
      "Error al crear algunos patrones. Por favor revisa e intenta nuevamente."
    );
  } finally {
    creating.value = false;
  }
}

onMounted(async () => {
  // Cargar categorías si no están cargadas
  if (!patternStore.categories.length) {
    await patternStore.loadCategories();
  }

  // Cargar sugerencias
  await loadSuggestions();
});
</script>
