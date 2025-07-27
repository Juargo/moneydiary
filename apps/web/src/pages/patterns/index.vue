<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">
                Gestión de Patrones
              </h1>
              <p class="mt-1 text-sm text-gray-600">
                Administra patrones para la categorización automática de
                transacciones
              </p>
            </div>

            <div class="flex space-x-3">
              <button
                @click="showTestModal = true"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg
                  class="w-4 h-4 mr-2"
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
                Probar Patrones
              </button>

              <button
                @click="showSuggestionsModal = true"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg
                  class="w-4 h-4 mr-2"
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
                Ver Sugerencias
              </button>

              <button
                @click="showFormModal = true"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
              >
                <svg
                  class="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                  ></path>
                </svg>
                Nuevo Patrón
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Lista de patrones -->
      <PatternList
        @edit="editPattern"
        @delete="confirmDeletePattern"
        @toggle="togglePattern"
        @test="testPattern"
      />
    </div>

    <!-- Modales -->

    <!-- Modal de formulario (crear/editar) -->
    <PatternFormModal
      v-if="showFormModal"
      :pattern="selectedPattern"
      @close="closeFormModal"
      @saved="handlePatternSaved"
    />

    <!-- Modal de prueba de patrones -->
    <PatternTestModal v-if="showTestModal" @close="showTestModal = false" />

    <!-- Modal de sugerencias -->
    <PatternSuggestionsModal
      v-if="showSuggestionsModal"
      @close="showSuggestionsModal = false"
      @patterns-created="handlePatternsCreated"
    />

    <!-- Modal de confirmación de eliminación -->
    <ConfirmationModal
      v-if="showDeleteModal"
      :title="`Eliminar patrón '${patternToDelete?.name}'`"
      message="¿Estás seguro de que deseas eliminar este patrón? Esta acción no se puede deshacer."
      type="danger"
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      :loading="deletingPattern"
      @confirm="deletePattern"
      @cancel="cancelDelete"
    />

    <!-- Toast notifications -->
    <div class="fixed bottom-4 right-4 z-50 space-y-2">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="bg-white rounded-lg shadow-lg border-l-4 p-4 max-w-sm"
        :class="{
          'border-green-500': notification.type === 'success',
          'border-red-500': notification.type === 'error',
          'border-yellow-500': notification.type === 'warning',
          'border-blue-500': notification.type === 'info',
        }"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg
              v-if="notification.type === 'success'"
              class="h-5 w-5 text-green-400"
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

            <svg
              v-else-if="notification.type === 'error'"
              class="h-5 w-5 text-red-400"
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

            <svg
              v-else-if="notification.type === 'warning'"
              class="h-5 w-5 text-yellow-400"
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

            <svg
              v-else
              class="h-5 w-5 text-blue-400"
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
          </div>

          <div class="ml-3 flex-1">
            <p class="text-sm font-medium text-gray-900">
              {{ notification.title }}
            </p>
            <p v-if="notification.message" class="mt-1 text-sm text-gray-500">
              {{ notification.message }}
            </p>
          </div>

          <div class="ml-4 flex-shrink-0">
            <button
              @click="removeNotification(notification.id)"
              class="inline-flex text-gray-400 hover:text-gray-600"
            >
              <svg
                class="h-4 w-4"
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
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { usePatternStore } from "../stores/patternStore";
import PatternList from "../components/patterns/PatternList.vue";
import PatternFormModal from "../components/patterns/PatternFormModal.vue";
import PatternTestModal from "../components/patterns/PatternTestModal.vue";
import PatternSuggestionsModal from "../components/patterns/PatternSuggestionsModal.vue";
import ConfirmationModal from "../components/patterns/ConfirmationModal.vue";

const patternStore = usePatternStore();

// Estado de modales
const showFormModal = ref(false);
const showTestModal = ref(false);
const showSuggestionsModal = ref(false);
const showDeleteModal = ref(false);

// Estado para edición/eliminación
const selectedPattern = ref(null);
const patternToDelete = ref(null);
const deletingPattern = ref(false);

// Sistema de notificaciones
const notifications = ref([]);

// Métodos para manejo de patrones
function editPattern(pattern) {
  selectedPattern.value = pattern;
  showFormModal.value = true;
}

function confirmDeletePattern(pattern) {
  patternToDelete.value = pattern;
  showDeleteModal.value = true;
}

async function deletePattern() {
  if (!patternToDelete.value) return;

  deletingPattern.value = true;

  try {
    await patternStore.deletePattern(patternToDelete.value.id);

    addNotification({
      type: "success",
      title: "Patrón eliminado",
      message: `El patrón "${patternToDelete.value.name}" ha sido eliminado exitosamente.`,
    });

    showDeleteModal.value = false;
    patternToDelete.value = null;
  } catch (error) {
    console.error("Error deleting pattern:", error);
    addNotification({
      type: "error",
      title: "Error al eliminar",
      message: "No se pudo eliminar el patrón. Por favor intenta nuevamente.",
    });
  } finally {
    deletingPattern.value = false;
  }
}

function cancelDelete() {
  showDeleteModal.value = false;
  patternToDelete.value = null;
}

async function togglePattern(pattern) {
  try {
    await patternStore.updatePattern(pattern.id, {
      ...pattern,
      isActive: !pattern.isActive,
    });

    addNotification({
      type: "success",
      title: pattern.isActive ? "Patrón desactivado" : "Patrón activado",
      message: `El patrón "${pattern.name}" ha sido ${
        pattern.isActive ? "desactivado" : "activado"
      }.`,
    });
  } catch (error) {
    console.error("Error toggling pattern:", error);
    addNotification({
      type: "error",
      title: "Error al cambiar estado",
      message: "No se pudo cambiar el estado del patrón.",
    });
  }
}

function testPattern(pattern) {
  // Implementar lógica de prueba específica para un patrón
  showTestModal.value = true;
}

// Métodos para manejo de modales
function closeFormModal() {
  showFormModal.value = false;
  selectedPattern.value = null;
}

function handlePatternSaved(pattern) {
  const isEdit = selectedPattern.value !== null;

  addNotification({
    type: "success",
    title: isEdit ? "Patrón actualizado" : "Patrón creado",
    message: `El patrón "${pattern.name}" ha sido ${
      isEdit ? "actualizado" : "creado"
    } exitosamente.`,
  });

  closeFormModal();
}

function handlePatternsCreated(patterns) {
  addNotification({
    type: "success",
    title: "Patrones creados",
    message: `Se han creado ${patterns.length} patrón(es) exitosamente desde las sugerencias.`,
  });
}

// Sistema de notificaciones
function addNotification(notification) {
  const id = Date.now() + Math.random();
  notifications.value.push({
    id,
    ...notification,
  });

  // Auto-remover después de 5 segundos
  setTimeout(() => {
    removeNotification(id);
  }, 5000);
}

function removeNotification(id) {
  const index = notifications.value.findIndex((n) => n.id === id);
  if (index > -1) {
    notifications.value.splice(index, 1);
  }
}

// Ciclo de vida
onMounted(async () => {
  try {
    // Cargar datos iniciales
    await Promise.all([
      patternStore.loadPatterns(),
      patternStore.loadCategories(),
    ]);
  } catch (error) {
    console.error("Error loading initial data:", error);
    addNotification({
      type: "error",
      title: "Error de carga",
      message:
        "No se pudieron cargar los datos iniciales. Por favor recarga la página.",
    });
  }
});
</script>
