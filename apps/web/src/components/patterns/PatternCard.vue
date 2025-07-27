<template>
  <div class="p-6 hover:bg-gray-50 transition-colors">
    <div class="flex items-start justify-between">
      <!-- Información principal del patrón -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center space-x-3 mb-2">
          <h3 class="text-lg font-medium text-gray-900 truncate">
            {{ pattern.name }}
          </h3>

          <!-- Badges de estado -->
          <div class="flex space-x-2">
            <span
              v-if="pattern.isActive"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
            >
              Activo
            </span>
            <span
              v-else
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
            >
              Inactivo
            </span>

            <span
              v-if="pattern.autoApply"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              Auto-aplicar
            </span>

            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="getPatternTypeClass(pattern.patternType)"
            >
              {{ getPatternTypeLabel(pattern.patternType) }}
            </span>
          </div>
        </div>

        <!-- Patrón y detalles -->
        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500">Patrón:</span>
            <code
              class="px-2 py-1 bg-gray-100 rounded text-sm font-mono text-gray-800"
            >
              {{ pattern.pattern }}
            </code>
          </div>

          <div class="flex items-center space-x-4 text-sm text-gray-600">
            <div class="flex items-center space-x-1">
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
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                ></path>
              </svg>
              <span
                >{{ pattern.subcategory.categoryName }} →
                {{ pattern.subcategory.name }}</span
              >
            </div>

            <div class="flex items-center space-x-1">
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
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                ></path>
              </svg>
              <span>Prioridad: {{ pattern.priority }}</span>
            </div>

            <div
              v-if="pattern.isCaseSensitive"
              class="flex items-center space-x-1"
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <span>Sensible a mayúsculas</span>
            </div>
          </div>

          <!-- Notas -->
          <div v-if="pattern.notes" class="text-sm text-gray-600">
            <span class="font-medium">Notas:</span> {{ pattern.notes }}
          </div>

          <!-- Fechas -->
          <div class="text-xs text-gray-500">
            Creado: {{ formatDate(pattern.createdAt) }}
            <span
              v-if="
                pattern.updatedAt && pattern.updatedAt !== pattern.createdAt
              "
            >
              • Actualizado: {{ formatDate(pattern.updatedAt) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Acciones -->
      <div class="ml-4 flex-shrink-0">
        <div class="flex items-center space-x-2">
          <!-- Toggle activo/inactivo -->
          <button
            @click="$emit('toggle-active', pattern)"
            class="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
            :title="pattern.isActive ? 'Desactivar patrón' : 'Activar patrón'"
          >
            <svg
              v-if="pattern.isActive"
              class="w-5 h-5 text-green-600"
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
            <svg
              v-else
              class="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
              ></path>
            </svg>
          </button>

          <!-- Aplicar patrón -->
          <button
            @click="$emit('apply', pattern)"
            class="p-2 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50"
            title="Aplicar patrón a transacciones existentes"
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
                d="M13 10V3L4 14h7v7l9-11h-7z"
              ></path>
            </svg>
          </button>

          <!-- Editar -->
          <button
            @click="$emit('edit', pattern)"
            class="p-2 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50"
            title="Editar patrón"
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
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              ></path>
            </svg>
          </button>

          <!-- Eliminar -->
          <button
            @click="$emit('delete', pattern)"
            class="p-2 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50"
            title="Eliminar patrón"
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";

defineProps({
  pattern: {
    type: Object,
    required: true,
  },
});

defineEmits(["edit", "delete", "toggle-active", "apply"]);

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

function getPatternTypeClass(type) {
  const classes = {
    contains: "bg-blue-100 text-blue-800",
    starts_with: "bg-green-100 text-green-800",
    ends_with: "bg-yellow-100 text-yellow-800",
    regex: "bg-purple-100 text-purple-800",
    exact: "bg-red-100 text-red-800",
  };
  return classes[type] || "bg-gray-100 text-gray-800";
}

function formatDate(dateString) {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("es-CL", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>
