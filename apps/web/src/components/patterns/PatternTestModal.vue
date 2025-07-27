<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
  >
    <div
      class="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto"
    >
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">
          Probar Patrones de Descripción
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          Ingresa una descripción de transacción para ver qué patrones coinciden
        </p>
      </div>

      <div class="p-6 space-y-6">
        <!-- Formulario de prueba -->
        <div>
          <label
            for="testDescription"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            Descripción a Probar
          </label>
          <div class="flex space-x-3">
            <input
              id="testDescription"
              v-model="testDescription"
              type="text"
              class="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Ej: COMPRA JUMBO MAIPU, NETFLIX CHILE, TRANSFERENCIA..."
              @keyup.enter="runTest"
            />
            <button
              @click="runTest"
              :disabled="!testDescription.trim() || loading"
              class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {{ loading ? "Probando..." : "Probar" }}
            </button>
          </div>

          <!-- Ejemplos rápidos -->
          <div class="mt-3">
            <p class="text-sm text-gray-600 mb-2">Ejemplos rápidos:</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="example in examples"
                :key="example"
                @click="
                  testDescription = example;
                  runTest();
                "
                class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                {{ example }}
              </button>
            </div>
          </div>
        </div>

        <!-- Opciones de filtrado -->
        <div class="flex items-center space-x-4">
          <label class="flex items-center">
            <input
              v-model="includeInactive"
              type="checkbox"
              class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span class="ml-2 text-sm text-gray-700"
              >Incluir patrones inactivos</span
            >
          </label>

          <label class="flex items-center">
            <input
              v-model="onlyMatches"
              type="checkbox"
              class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span class="ml-2 text-sm text-gray-700"
              >Solo mostrar coincidencias</span
            >
          </label>
        </div>

        <!-- Resultados -->
        <div v-if="testResults">
          <!-- Resumen -->
          <div class="bg-blue-50 p-4 rounded-lg mb-4">
            <h3 class="font-medium text-blue-900 mb-2">
              Resultados para: "{{ testResults.description }}"
            </h3>
            <div class="flex items-center space-x-4 text-sm text-blue-700">
              <span>{{ matchCount }} coincidencia(s) encontrada(s)</span>
              <span>{{ totalPatterns }} patrón(es) evaluado(s)</span>
            </div>

            <!-- Mejor coincidencia -->
            <div
              v-if="testResults.bestMatch"
              class="mt-3 p-3 bg-green-100 rounded border-l-4 border-green-500"
            >
              <p class="text-sm font-medium text-green-800">
                🏆 Mejor Coincidencia (se aplicaría automáticamente):
              </p>
              <p class="text-sm text-green-700">
                <strong>{{ testResults.bestMatch.patternName }}</strong>
                → {{ testResults.bestMatch.subcategory.categoryName }} →
                {{ testResults.bestMatch.subcategory.name }}
              </p>
              <p class="text-xs text-green-600 mt-1">
                Patrón: "{{ testResults.bestMatch.pattern }}" ({{
                  getPatternTypeLabel(testResults.bestMatch.patternType)
                }})
              </p>
            </div>
          </div>

          <!-- Lista detallada de resultados -->
          <div class="space-y-3">
            <h4 class="font-medium text-gray-900">Detalle de Evaluación</h4>

            <div
              v-if="filteredResults.length === 0"
              class="text-center py-8 text-gray-500"
            >
              <svg
                class="w-12 h-12 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <p>No hay resultados que mostrar</p>
            </div>

            <div
              v-for="result in filteredResults"
              :key="result.patternId"
              class="border rounded-lg p-4"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <!-- Indicador de coincidencia -->
                    <div class="flex-shrink-0">
                      <div
                        v-if="result.matched"
                        class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
                      >
                        <svg
                          class="w-4 h-4 text-white"
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
                      <div
                        v-else
                        class="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center"
                      >
                        <svg
                          class="w-4 h-4 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M6 18L18 6M6 6l12 12"
                          ></path>
                        </svg>
                      </div>
                    </div>

                    <!-- Información del patrón -->
                    <div>
                      <h5 class="font-medium text-gray-900">
                        {{ result.patternName }}
                      </h5>
                      <p class="text-sm text-gray-600">
                        {{ result.subcategory.categoryName }} →
                        {{ result.subcategory.name }}
                      </p>
                    </div>
                  </div>

                  <!-- Detalles del patrón -->
                  <div class="ml-9 space-y-1">
                    <div class="flex items-center space-x-2 text-sm">
                      <span class="text-gray-500">Patrón:</span>
                      <code
                        class="px-2 py-1 bg-gray-100 rounded text-xs font-mono"
                        >{{ result.pattern }}</code
                      >
                      <span class="text-xs text-gray-400"
                        >({{ getPatternTypeLabel(result.patternType) }})</span
                      >
                    </div>

                    <div
                      v-if="result.matched && result.matchedText"
                      class="flex items-center space-x-2 text-sm"
                    >
                      <span class="text-gray-500">Texto coincidente:</span>
                      <span
                        class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-mono"
                      >
                        "{{ result.matchedText }}"
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Estado del resultado -->
                <div class="flex-shrink-0 text-right">
                  <span
                    v-if="result.matched"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    ✓ Coincide
                  </span>
                  <span
                    v-else
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    ✗ No coincide
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Estado de carga -->
        <div v-if="loading" class="text-center py-8">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"
          ></div>
          <p class="mt-2 text-gray-600">Evaluando patrones...</p>
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
                Error al probar patrones
              </h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
              <button
                @click="runTest"
                class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { usePatternStore } from "../../stores/patternStore";

defineEmits(["close"]);

const patternStore = usePatternStore();
const { loading, error, testResults } = patternStore;

// Estado local
const testDescription = ref("");
const includeInactive = ref(false);
const onlyMatches = ref(false);

// Ejemplos para pruebas rápidas
const examples = [
  "COMPRA JUMBO MAIPU",
  "NETFLIX CHILE",
  "TRANSFERENCIA BANCARIA",
  "PAG UBER",
  "SUSCRIPCION SPOTIFY",
  "COMPRA LIDER EXPRESS",
  "ABONO NOMINA",
  "GIRO ATM BCI",
];

// Computed
const matchCount = computed(() => {
  if (!testResults) return 0;
  return testResults.results.filter((r) => r.matched).length;
});

const totalPatterns = computed(() => {
  if (!testResults) return 0;
  return testResults.results.length;
});

const filteredResults = computed(() => {
  if (!testResults) return [];

  let results = testResults.results;

  // Filtrar por estado activo/inactivo si es necesario
  // (esto requeriría información adicional del patrón)

  // Filtrar solo coincidencias si está marcado
  if (onlyMatches.value) {
    results = results.filter((r) => r.matched);
  }

  // Ordenar: coincidencias primero, luego por nombre
  return results.sort((a, b) => {
    if (a.matched && !b.matched) return -1;
    if (!a.matched && b.matched) return 1;
    return a.patternName.localeCompare(b.patternName);
  });
});

// Métodos
function getPatternTypeLabel(type) {
  const labels = {
    contains: "Contiene",
    starts_with: "Inicia con",
    ends_with: "Termina con",
    regex: "Regex",
    exact: "Exacto",
  };
  return labels[type] || type;
}

async function runTest() {
  if (!testDescription.value.trim()) return;

  try {
    await patternStore.testPatterns({
      description: testDescription.value.trim(),
    });
  } catch (err) {
    console.error("Error testing patterns:", err);
  }
}

onMounted(() => {
  // Limpiar resultados previos
  patternStore.clearTestResults();
});
</script>
