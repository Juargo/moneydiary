<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
  >
    <div
      class="relative top-20 mx-auto p-5 border max-w-4xl shadow-lg rounded-md bg-white"
    >
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEditing ? "Editar Perfil" : "Nuevo Perfil" }} de Importación
        </h3>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSave">
        <!-- Información básica del perfil -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Nombre del perfil *
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Ej: Estado de Cuenta Banco Chile"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Cuenta *
            </label>
            <select
              v-model="formData.account_id"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Selecciona una cuenta</option>
              <option
                v-for="account in accounts"
                :key="account.id"
                :value="account.id"
              >
                {{ account.name }} ({{ account.bank?.name }})
              </option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Descripción
            </label>
            <textarea
              v-model="formData.description"
              rows="2"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Descripción opcional del perfil"
            ></textarea>
          </div>
        </div>

        <!-- Configuración del archivo -->
        <div class="border-t pt-6 mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-4">
            Configuración del Archivo
          </h4>

          <!-- Selector de tipo de archivo -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tipo de archivo *
            </label>
            <select
              v-model="formData.file_type"
              class="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            >
              <option value="">Selecciona el tipo de archivo</option>
              <option value="csv">CSV (Valores separados por comas)</option>
              <option value="excel">Excel (.xlsx)</option>
              <option value="xls">Excel Legacy (.xls)</option>
            </select>
          </div>

          <!-- Configuración para archivos CSV -->
          <div
            v-if="formData.file_type === 'csv'"
            class="grid grid-cols-1 md:grid-cols-4 gap-4"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Delimitador
              </label>
              <select
                v-model="formData.delimiter"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value=",">Coma (,)</option>
                <option value=";">Punto y coma (;)</option>
                <option value="\t">Tabulación</option>
                <option value="|">Pipe (|)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Codificación
              </label>
              <select
                v-model="formData.encoding"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="utf-8">UTF-8</option>
                <option value="latin-1">Latin-1</option>
                <option value="cp1252">Windows-1252</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Formato de fecha
              </label>
              <select
                v-model="formData.date_format"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                <option value="DD-MM-YYYY">DD-MM-YYYY</option>
                <option value="DD.MM.YYYY">DD.MM.YYYY</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Separador decimal
              </label>
              <select
                v-model="formData.decimal_separator"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value=".">Punto (.)</option>
                <option value=",">Coma (,)</option>
              </select>
            </div>
          </div>

          <!-- Configuración para archivos Excel -->
          <div
            v-if="
              formData.file_type === 'excel' || formData.file_type === 'xls'
            "
            class="space-y-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Formato de fecha
                </label>
                <select
                  v-model="formData.date_format"
                  class="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  <option value="DD-MM-YYYY">DD-MM-YYYY</option>
                  <option value="DD.MM.YYYY">DD.MM.YYYY</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Separador decimal
                </label>
                <select
                  v-model="formData.decimal_separator"
                  class="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value=".">Punto (.)</option>
                  <option value=",">Coma (,)</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de hoja
                </label>
                <input
                  v-model="formData.sheet_name"
                  type="text"
                  placeholder="Deja vacío para usar la primera hoja"
                  class="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Fila de encabezados
                </label>
                <input
                  v-model="formData.header_row"
                  type="number"
                  min="1"
                  class="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Fila de inicio de datos
                </label>
                <input
                  v-model="formData.start_row"
                  type="number"
                  min="1"
                  class="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
          </div>

          <div class="mt-4 flex flex-wrap gap-4">
            <label class="flex items-center">
              <input
                v-model="formData.has_header"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">Tiene encabezados</span>
            </label>

            <label class="flex items-center">
              <input
                v-model="formData.skip_empty_rows"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700"
                >Omitir filas vacías</span
              >
            </label>

            <label class="flex items-center">
              <input
                v-model="formData.auto_detect_format"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700"
                >Auto-detectar formato</span
              >
            </label>
          </div>

          <div class="mt-4">
            <label class="flex items-center">
              <input
                v-model="formData.is_default"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700"
                >Usar como perfil por defecto para esta cuenta</span
              >
            </label>
          </div>
        </div>

        <!-- Configuración de esquema de montos -->
        <div class="border-t pt-6 mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-4">
            Configuración de Montos
          </h4>

          <div class="bg-blue-50 p-4 rounded-md">
            <h5 class="text-sm font-medium text-blue-900 mb-2">
              💡 Cómo mapear los montos
            </h5>
            <div class="text-sm text-blue-800 space-y-2">
              <p>
                <strong>Monto (único):</strong> Para archivos con una sola
                columna de monto con valores positivos/negativos. El tipo se
                determina por el signo.
              </p>
              <p>
                <strong>Ingreso:</strong> Para columnas que contienen solo
                ingresos.
                <span class="font-semibold text-green-700"
                  >Automáticamente marcado como ingreso.</span
                >
              </p>
              <p>
                <strong>Egreso/Gasto:</strong> Para columnas que contienen solo
                gastos.
                <span class="font-semibold text-red-700"
                  >Automáticamente marcado como gasto.</span
                >
              </p>
              <p>
                <strong>Débito/Crédito:</strong> Para archivos que usan
                terminología contable. El tipo se determina según convención
                contable.
              </p>
              <p>
                <strong>Tipo de Transacción:</strong> Solo si el archivo tiene
                una columna que indica explícitamente el tipo (ej: "INGRESO",
                "GASTO", "D", "C").
                <span class="font-semibold text-blue-700"
                  >Opcional - solo mapea si existe en tu archivo.</span
                >
              </p>
            </div>
          </div>

          <!-- Configuración para monto único -->
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Si usas "Monto (único)", ¿cómo interpretar los signos?
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="formData.positive_is_income"
                  :value="true"
                  type="radio"
                  name="sign_interpretation"
                  class="text-primary-600"
                />
                <span class="ml-2 text-sm">
                  Positivo = Ingreso, Negativo = Gasto (más común)
                </span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="formData.positive_is_income"
                  :value="false"
                  type="radio"
                  name="sign_interpretation"
                  class="text-primary-600"
                />
                <span class="ml-2 text-sm">
                  Positivo = Gasto, Negativo = Ingreso
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Mapeo de columnas -->
        <div class="border-t pt-6 mb-6">
          <div class="flex justify-between items-center mb-4">
            <h4 class="text-md font-medium text-gray-900">Mapeo de Columnas</h4>
            <button
              type="button"
              @click="addColumnMapping"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 mr-1"
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
              Agregar Mapeo
            </button>
          </div>

          <div class="space-y-3">
            <div
              v-for="(mapping, index) in formData.column_mappings"
              :key="index"
              class="flex items-center space-x-3 p-3 bg-gray-50 rounded-md"
            >
              <div class="flex-1">
                <input
                  v-model="mapping.source_column_name"
                  type="text"
                  :placeholder="
                    formData.file_type === 'csv'
                      ? 'Nombre de columna en CSV'
                      : 'Nombre de columna en Excel'
                  "
                  required
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
              </div>

              <div class="flex-1">
                <select
                  v-model="mapping.target_field_name"
                  required
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Mapear a...</option>
                  <option value="date">Fecha</option>

                  <!-- Opciones de monto -->
                  <option value="amount">Monto (único)</option>
                  <option value="income_amount">Ingreso</option>
                  <option value="expense_amount">Egreso/Gasto</option>
                  <option value="debit_amount">Débito</option>
                  <option value="credit_amount">Crédito</option>

                  <!-- Otras opciones -->
                  <option value="description">Descripción</option>
                  <option value="notes">Notas</option>
                  <option value="reference">Referencia</option>
                  <option value="category">Categoría</option>
                  <option value="account_number">Número de Cuenta</option>
                  <option value="transaction_type">Tipo de Transacción</option>
                </select>
              </div>

              <div class="flex-shrink-0">
                <input
                  v-model="mapping.position"
                  type="number"
                  placeholder="Pos."
                  min="1"
                  class="w-16 border border-gray-300 rounded-md px-2 py-2 text-sm"
                />
              </div>

              <div class="flex-shrink-0">
                <label class="flex items-center">
                  <input
                    v-model="mapping.is_required"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600"
                  />
                  <span class="ml-1 text-xs text-gray-600">Req.</span>
                </label>
              </div>

              <div class="flex-shrink-0">
                <button
                  type="button"
                  @click="removeColumnMapping(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <div
              v-if="!formData.column_mappings.length"
              class="text-center py-8 text-gray-500"
            >
              <p>No hay mapeos configurados</p>
              <p class="text-sm">Agrega al menos un mapeo para fecha y monto</p>
            </div>
          </div>

          <!-- Guía de ayuda -->
          <div class="mt-6 bg-blue-50 p-4 rounded-md">
            <h5 class="text-sm font-medium text-blue-900 mb-2">
              💡 Guía rápida de mapeo
            </h5>
            <div class="text-sm text-blue-800 space-y-1">
              <p>
                <strong>Campos requeridos:</strong> Necesitas mapear al menos
                "Fecha" y un campo de monto.
              </p>

              <p><strong>Ejemplos de mapeo (SIN columna de tipo):</strong></p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li>
                  <strong>Archivo con una columna:</strong> "Fecha" → Fecha,
                  "Monto" → Monto (único)
                  <span class="text-green-600">✓ Tipo por signo</span>
                </li>
                <li>
                  <strong>Archivo con columnas separadas:</strong> "Fecha" →
                  Fecha, "Ingresos" → Ingreso, "Gastos" → Egreso/Gasto
                  <span class="text-green-600">✓ Tipo automático</span>
                </li>
                <li>
                  <strong>Archivo contable:</strong> "Fecha" → Fecha, "Debe" →
                  Débito, "Haber" → Crédito
                  <span class="text-green-600">✓ Tipo por convención</span>
                </li>
              </ul>

              <p><strong>Con columna de tipo (opcional):</strong></p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li>
                  <strong>Con tipo explícito:</strong> Además mapea "Tipo" →
                  Tipo de Transacción
                  <span class="text-blue-600">ℹ Solo si existe</span>
                </li>
              </ul>

              <div
                class="mt-3 p-2 bg-green-100 rounded border-l-4 border-green-400"
              >
                <p class="text-green-800 text-xs">
                  <strong>📌 Nota importante:</strong> No necesitas una columna
                  de tipo de transacción. El sistema determina automáticamente
                  si es ingreso o gasto según el mapeo que elijas.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Botones -->
        <div class="flex justify-end space-x-3 pt-6 border-t">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {{ saving ? "Guardando..." : isEditing ? "Actualizar" : "Crear" }}
            Perfil
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

const props = defineProps({
  profile: {
    type: Object,
    default: null,
  },
  accounts: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["close", "saved"]);

const authStore = useAuthStore();
const saving = ref(false);

const isEditing = computed(() => !!props.profile);

// Datos del formulario
const formData = reactive({
  name: "",
  description: "",
  account_id: "",
  is_default: false,
  file_type: "",
  delimiter: ",",
  has_header: true,
  encoding: "utf-8",
  date_format: "DD/MM/YYYY",
  decimal_separator: ".",

  // Configuración simplificada para monto único
  positive_is_income: true, // Solo se usa cuando hay mapeo a "amount"

  sheet_name: "",
  header_row: 1,
  start_row: 2,
  skip_empty_rows: true,
  auto_detect_format: true,
  column_mappings: [],
});

// Funciones
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

function addColumnMapping() {
  formData.column_mappings.push({
    source_column_name: "",
    source_column_index: null,
    target_field_name: "",
    is_required: true,
    position: formData.column_mappings.length + 1,
    transformation_rule: null,
    default_value: null,
    amount_multiplier: "1",
    treat_empty_as_zero: true,
    min_value: null,
    max_value: null,
    regex_pattern: null,
  });
}

function removeColumnMapping(index) {
  formData.column_mappings.splice(index, 1);

  // Reajustar posiciones
  formData.column_mappings.forEach((mapping, idx) => {
    if (!mapping.position || mapping.position > index + 1) {
      mapping.position = idx + 1;
    }
  });
}

function validateForm() {
  if (!formData.name.trim()) {
    throw new Error("El nombre del perfil es requerido");
  }

  if (!formData.account_id) {
    throw new Error("Debe seleccionar una cuenta");
  }

  if (!formData.file_type) {
    throw new Error("Debe seleccionar un tipo de archivo");
  }

  if (!formData.column_mappings.length) {
    throw new Error("Debe agregar al menos un mapeo de columna");
  }

  // Validar que exista mapeo para fecha
  const hasDate = formData.column_mappings.some(
    (m) => m.target_field_name === "date"
  );

  if (!hasDate) {
    throw new Error('Debe mapear al menos una columna a "Fecha"');
  }

  // Validar que exista al menos un mapeo de monto
  const targetFields = formData.column_mappings
    .map((m) => m.target_field_name)
    .filter(Boolean);

  const amountFields = targetFields.filter((field) =>
    [
      "amount",
      "income_amount",
      "expense_amount",
      "debit_amount",
      "credit_amount",
    ].includes(field)
  );

  if (amountFields.length === 0) {
    throw new Error(
      "Debe mapear al menos una columna de monto (Monto, Ingreso, Egreso, Débito o Crédito)"
    );
  }

  // Validar mapeos duplicados
  const uniqueTargets = [...new Set(targetFields)];

  if (targetFields.length !== uniqueTargets.length) {
    throw new Error("No puede mapear múltiples columnas al mismo campo");
  }
}

async function handleSave() {
  try {
    validateForm();

    saving.value = true;

    const url = isEditing.value
      ? `/api/v1/import-profiles/${props.profile.id}`
      : "/api/v1/import-profiles";

    const method = isEditing.value ? "PUT" : "POST";

    await apiRequest(url, {
      method,
      body: JSON.stringify(formData),
    });

    emit("saved");
  } catch (err) {
    console.error("Error guardando perfil:", err);
    alert(`Error: ${err.message}`);
  } finally {
    saving.value = false;
  }
}

// Inicializar datos si se está editando
onMounted(() => {
  if (props.profile) {
    Object.assign(formData, {
      name: props.profile.name,
      description: props.profile.description || "",
      account_id: props.profile.account_id,
      is_default: props.profile.is_default,
      file_type: props.profile.file_type || "csv", // Default to CSV if not specified
      delimiter: props.profile.delimiter,
      has_header: props.profile.has_header,
      encoding: props.profile.encoding || "utf-8",
      date_format: props.profile.date_format,
      decimal_separator: props.profile.decimal_separator,

      // Campo simplificado
      positive_is_income: props.profile.positive_is_income !== false, // default true

      sheet_name: props.profile.sheet_name || "",
      header_row: props.profile.header_row || 1,
      start_row: props.profile.start_row || 2,
      skip_empty_rows: props.profile.skip_empty_rows !== false, // default true
      auto_detect_format: props.profile.auto_detect_format !== false, // default true
      column_mappings: props.profile.column_mappings.map((mapping) => ({
        source_column_name: mapping.source_column_name,
        source_column_index: mapping.source_column_index,
        target_field_name: mapping.target_field_name,
        is_required: mapping.is_required,
        position: mapping.position,
        transformation_rule: mapping.transformation_rule,
        default_value: mapping.default_value,
        amount_multiplier: mapping.amount_multiplier || "1",
        treat_empty_as_zero: mapping.treat_empty_as_zero !== false,
        min_value: mapping.min_value,
        max_value: mapping.max_value,
        regex_pattern: mapping.regex_pattern,
      })),
    });
  } else {
    // Agregar mapeos por defecto para nuevo perfil
    addColumnMapping();
    addColumnMapping();
  }
});
</script>
