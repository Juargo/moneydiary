<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    @click.self="$emit('close')"
  >
    <div
      class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
    >
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            Editar Grupo de Categorías
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg
              class="w-6 h-6"
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

        <!-- Form -->
        <form @submit.prevent="updateGroup" class="space-y-4">
          <!-- Nombre -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700"
              >Nombre</label
            >
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ej: Gastos del hogar"
            />
          </div>

          <!-- Icono -->
          <div>
            <label for="icon" class="block text-sm font-medium text-gray-700"
              >Icono (opcional)</label
            >
            <div class="mt-1 flex items-center space-x-2">
              <input
                id="icon"
                v-model="form.icon"
                type="text"
                class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="🏠"
                maxlength="2"
              />
              <div class="text-xl">{{ form.icon || "📁" }}</div>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              Usa un emoji para representar este grupo
            </p>
          </div>

          <!-- Tipo -->
          <div>
            <label class="block text-sm font-medium text-gray-700">Tipo</label>
            <div class="mt-2 space-y-2">
              <label class="flex items-center">
                <input
                  v-model="form.isExpense"
                  type="radio"
                  :value="true"
                  class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">Gastos</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="form.isExpense"
                  type="radio"
                  :value="false"
                  class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">Ingresos</span>
              </label>
            </div>
          </div>

          <!-- Orden de visualización -->
          <div>
            <label
              for="displayOrder"
              class="block text-sm font-medium text-gray-700"
              >Orden de visualización</label
            >
            <input
              id="displayOrder"
              v-model.number="form.displayOrder"
              type="number"
              min="0"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <p class="mt-1 text-xs text-gray-500">
              Número más bajo aparece primero
            </p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="rounded-md bg-red-50 p-4">
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
                <p class="text-sm font-medium text-red-800">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Botones -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isLoading"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isLoading" class="flex items-center">
                <svg
                  class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
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
                Actualizando...
              </span>
              <span v-else>Actualizar Grupo</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import {
  categoryGroupService,
  type CategoryGroup,
} from "../../services/categoryService";

// Props
const props = defineProps<{
  group: CategoryGroup;
}>();

// Eventos
const emit = defineEmits<{
  close: [];
  updated: [];
}>();

// Estado
const isLoading = ref(false);
const error = ref<string | null>(null);

// Formulario
const form = reactive({
  name: "",
  icon: "",
  isExpense: true,
  displayOrder: 0,
});

// Métodos
function initializeForm() {
  form.name = props.group.name;
  form.icon = props.group.icon || "";
  form.isExpense = props.group.isExpense;
  form.displayOrder = props.group.displayOrder;
}

async function updateGroup() {
  if (!form.name.trim()) {
    error.value = "El nombre es requerido";
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    await categoryGroupService.update(props.group.id, {
      name: form.name.trim(),
      icon: form.icon || undefined,
      isExpense: form.isExpense,
      displayOrder: form.displayOrder,
    });

    emit("updated");
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Error actualizando grupo";
    console.error("Error updating group:", err);
  } finally {
    isLoading.value = false;
  }
}

// Lifecycle
onMounted(() => {
  initializeForm();
});
</script>
