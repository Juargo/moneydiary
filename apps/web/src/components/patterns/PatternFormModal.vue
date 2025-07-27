<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
  >
    <div
      class="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto"
    >
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">
          {{ isEditing ? "Editar Patrón" : "Crear Nuevo Patrón" }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <!-- Nombre del patrón -->
        <div>
          <label
            for="name"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Nombre del Patrón *
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Ej: Supermercados, Netflix, Transferencias..."
          />
          <p class="mt-1 text-sm text-gray-500">
            Un nombre descriptivo para identificar el patrón
          </p>
        </div>

        <!-- Tipo de patrón -->
        <div>
          <label
            for="patternType"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Tipo de Patrón *
          </label>
          <select
            id="patternType"
            v-model="form.patternType"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
            @change="onPatternTypeChange"
          >
            <option value="contains">
              Contiene - busca el texto en cualquier parte
            </option>
            <option value="starts_with">
              Inicia con - busca al inicio de la descripción
            </option>
            <option value="ends_with">
              Termina con - busca al final de la descripción
            </option>
            <option value="exact">Exacto - coincidencia exacta</option>
            <option value="regex">Regex - expresión regular avanzada</option>
          </select>
        </div>

        <!-- Patrón de texto -->
        <div>
          <label
            for="pattern"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Patrón de Búsqueda *
          </label>
          <div class="relative">
            <input
              id="pattern"
              v-model="form.pattern"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
              :class="{ 'border-red-300': patternError }"
              :placeholder="getPatternPlaceholder()"
              @input="validatePattern"
            />
            <button
              v-if="form.pattern"
              type="button"
              @click="testPattern"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-blue-600 hover:text-blue-800"
              title="Probar patrón"
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
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </button>
          </div>
          <div v-if="patternError" class="mt-1 text-sm text-red-600">
            {{ patternError }}
          </div>
          <p class="mt-1 text-sm text-gray-500">
            {{ getPatternHelp() }}
          </p>
        </div>

        <!-- Subcategoría -->
        <div>
          <label
            for="subcategory"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Subcategoría *
          </label>
          <select
            id="subcategory"
            v-model="form.subcategoryId"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Seleccionar subcategoría...</option>
            <optgroup
              v-for="category in categories"
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
          <p class="mt-1 text-sm text-gray-500">
            La subcategoría que se asignará cuando el patrón coincida
          </p>
        </div>

        <!-- Configuraciones avanzadas -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Configuración</h3>

          <!-- Prioridad -->
          <div>
            <label
              for="priority"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
              Prioridad (0-100)
            </label>
            <input
              id="priority"
              v-model.number="form.priority"
              type="number"
              min="0"
              max="100"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="mt-1 text-sm text-gray-500">
              Mayor prioridad significa que se evaluará primero. Default: 50
            </p>
          </div>

          <!-- Opciones -->
          <div class="space-y-3">
            <label class="flex items-center">
              <input
                v-model="form.isCaseSensitive"
                type="checkbox"
                class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span class="ml-2 text-sm text-gray-700"
                >Sensible a mayúsculas y minúsculas</span
              >
            </label>

            <label class="flex items-center">
              <input
                v-model="form.isActive"
                type="checkbox"
                class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span class="ml-2 text-sm text-gray-700">Patrón activo</span>
            </label>

            <label class="flex items-center">
              <input
                v-model="form.autoApply"
                type="checkbox"
                class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span class="ml-2 text-sm text-gray-700"
                >Aplicar automáticamente a nuevas transacciones</span
              >
            </label>
          </div>
        </div>

        <!-- Notas -->
        <div>
          <label
            for="notes"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Notas (opcional)
          </label>
          <textarea
            id="notes"
            v-model="form.notes"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Notas adicionales sobre este patrón..."
          ></textarea>
        </div>

        <!-- Prueba de patrón -->
        <div v-if="testDescription" class="bg-gray-50 p-4 rounded-lg">
          <h4 class="font-medium text-gray-900 mb-2">Prueba del Patrón</h4>
          <input
            v-model="testDescription"
            type="text"
            placeholder="Ingresa una descripción para probar..."
            class="w-full border border-gray-300 rounded-md px-3 py-2 mb-2"
            @input="runPatternTest"
          />
          <div v-if="testResult" class="text-sm">
            <span
              :class="testResult.matched ? 'text-green-600' : 'text-red-600'"
              class="font-medium"
            >
              {{ testResult.matched ? "✓ Coincide" : "✗ No coincide" }}
            </span>
            <span v-if="testResult.matchedText" class="ml-2 text-gray-600">
              (texto coincidente: "{{ testResult.matchedText }}")
            </span>
          </div>
        </div>

        <!-- Botones -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            @click="testPattern"
            class="px-4 py-2 text-blue-700 bg-blue-100 border border-blue-300 rounded-md hover:bg-blue-200"
            :disabled="!form.pattern"
          >
            Probar
          </button>
          <button
            type="submit"
            :disabled="loading || !!patternError"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            {{ loading ? "Guardando..." : isEditing ? "Actualizar" : "Crear" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { usePatternStore } from "../../stores/patternStore";

const props = defineProps({
  pattern: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close", "save"]);

const patternStore = usePatternStore();
const { loading, validateRegexPattern } = patternStore;

// Estado del formulario
const form = ref({
  name: "",
  pattern: "",
  patternType: "contains",
  subcategoryId: "",
  priority: 50,
  isCaseSensitive: false,
  isActive: true,
  autoApply: true,
  notes: "",
});

const patternError = ref("");
const testDescription = ref("");
const testResult = ref(null);
const categories = ref([]); // Se cargaría desde la API

const isEditing = computed(() => !!props.pattern);

// Watchers
watch(
  () => props.pattern,
  (newPattern) => {
    if (newPattern) {
      form.value = {
        name: newPattern.name,
        pattern: newPattern.pattern,
        patternType: newPattern.patternType,
        subcategoryId: newPattern.subcategoryId,
        priority: newPattern.priority,
        isCaseSensitive: newPattern.isCaseSensitive,
        isActive: newPattern.isActive,
        autoApply: newPattern.autoApply,
        notes: newPattern.notes || "",
      };
    }
  },
  { immediate: true }
);

// Métodos
function getPatternPlaceholder() {
  const placeholders = {
    contains: "Ej: JUMBO, netflix, transferencia",
    starts_with: "Ej: COMPRA, PAG, TRF",
    ends_with: "Ej: .CL, SPA, LTDA",
    exact: "Ej: NETFLIX CHILE",
    regex: "Ej: JUMBO|LIDER|TOTTUS",
  };
  return (
    placeholders[form.value.patternType] || "Ingresa el patrón de búsqueda"
  );
}

function getPatternHelp() {
  const helps = {
    contains: "El patrón se buscará en cualquier parte de la descripción",
    starts_with: "La descripción debe comenzar con este texto",
    ends_with: "La descripción debe terminar con este texto",
    exact: "La descripción debe ser exactamente igual a este texto",
    regex: "Expresión regular. Usa | para alternativos, () para grupos, etc.",
  };
  return helps[form.value.patternType] || "";
}

function onPatternTypeChange() {
  validatePattern();
}

function validatePattern() {
  patternError.value = "";

  if (form.value.patternType === "regex" && form.value.pattern) {
    const validation = validateRegexPattern(form.value.pattern);
    if (!validation.valid) {
      patternError.value = validation.message;
    }
  }
}

function testPattern() {
  if (!form.value.pattern) return;
  testDescription.value = testDescription.value || "COMPRA JUMBO MAIPU";
  runPatternTest();
}

function runPatternTest() {
  if (!form.value.pattern || !testDescription.value) {
    testResult.value = null;
    return;
  }

  const description = testDescription.value;
  const pattern = form.value.pattern;
  const type = form.value.patternType;
  const caseSensitive = form.value.isCaseSensitive;

  const testText = caseSensitive ? description : description.toLowerCase();
  const patternText = caseSensitive ? pattern : pattern.toLowerCase();

  let matched = false;
  let matchedText = null;

  try {
    switch (type) {
      case "contains":
        matched = testText.includes(patternText);
        matchedText = matched ? pattern : null;
        break;
      case "starts_with":
        matched = testText.startsWith(patternText);
        matchedText = matched ? pattern : null;
        break;
      case "ends_with":
        matched = testText.endsWith(patternText);
        matchedText = matched ? pattern : null;
        break;
      case "exact":
        matched = testText === patternText;
        matchedText = matched ? description : null;
        break;
      case "regex":
        const flags = caseSensitive ? "" : "i";
        const regex = new RegExp(pattern, flags);
        const match = description.match(regex);
        matched = !!match;
        matchedText = match ? match[0] : null;
        break;
    }
  } catch (error) {
    matched = false;
    matchedText = null;
  }

  testResult.value = { matched, matchedText };
}

async function handleSubmit() {
  if (patternError.value) return;

  try {
    const data = {
      name: form.value.name,
      pattern: form.value.pattern,
      pattern_type: form.value.patternType,
      subcategory_id: parseInt(form.value.subcategoryId),
      priority: form.value.priority,
      is_case_sensitive: form.value.isCaseSensitive,
      is_active: form.value.isActive,
      auto_apply: form.value.autoApply,
      notes: form.value.notes || undefined,
    };

    if (isEditing.value) {
      await patternStore.updatePattern(props.pattern.id, data);
    } else {
      await patternStore.createPattern(data);
    }

    emit("save");
  } catch (error) {
    console.error("Error saving pattern:", error);
  }
}

async function loadCategories() {
  // Aquí cargarías las categorías y subcategorías desde la API
  // Por ahora mock data
  categories.value = [
    {
      id: 1,
      name: "Alimentación",
      subcategories: [
        { id: 1, name: "Supermercado" },
        { id: 2, name: "Restaurantes" },
      ],
    },
    {
      id: 2,
      name: "Entretenimiento",
      subcategories: [
        { id: 3, name: "Streaming" },
        { id: 4, name: "Cine" },
      ],
    },
  ];
}

onMounted(() => {
  loadCategories();
});
</script>
