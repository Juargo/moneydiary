<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
  >
    <div class="bg-white rounded-lg max-w-md w-full">
      <div class="px-6 py-4">
        <div class="flex items-center">
          <!-- Icono -->
          <div class="flex-shrink-0">
            <svg
              v-if="type === 'danger'"
              class="h-6 w-6 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              ></path>
            </svg>

            <svg
              v-else-if="type === 'warning'"
              class="h-6 w-6 text-yellow-600"
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
              v-else-if="type === 'info'"
              class="h-6 w-6 text-blue-600"
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

            <svg
              v-else
              class="h-6 w-6 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
          </div>

          <div class="ml-3 flex-1">
            <h3 class="text-lg font-medium text-gray-900">
              {{ title }}
            </h3>
            <div v-if="message" class="mt-2 text-sm text-gray-600">
              {{ message }}
            </div>
          </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3 rounded-b-lg">
        <button
          @click="$emit('cancel')"
          class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          {{ cancelText }}
        </button>
        <button
          @click="$emit('confirm')"
          :disabled="loading"
          class="px-4 py-2 rounded-md text-white font-medium"
          :class="buttonClasses"
        >
          {{ loading ? "Procesando..." : confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    default: "",
  },
  type: {
    type: String,
    default: "default",
    validator: (value) =>
      ["default", "danger", "warning", "info"].includes(value),
  },
  confirmText: {
    type: String,
    default: "Confirmar",
  },
  cancelText: {
    type: String,
    default: "Cancelar",
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["confirm", "cancel"]);

const buttonClasses = computed(() => {
  const baseClasses = "disabled:opacity-50";

  switch (props.type) {
    case "danger":
      return `${baseClasses} bg-red-600 hover:bg-red-700`;
    case "warning":
      return `${baseClasses} bg-yellow-600 hover:bg-yellow-700`;
    case "info":
      return `${baseClasses} bg-blue-600 hover:bg-blue-700`;
    default:
      return `${baseClasses} bg-primary-600 hover:bg-primary-700`;
  }
});
</script>
