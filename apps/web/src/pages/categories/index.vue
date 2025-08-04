<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">
                Gestión de Categorías
              </h1>
              <p class="mt-1 text-sm text-gray-600">
                Organiza tus transacciones con grupos de categorías, categorías
                y subcategorías
              </p>
            </div>

            <div class="flex space-x-3">
              <button
                @click="showCreateGroupModal = true"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
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
                Nuevo Grupo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center py-12">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
        ></div>
        <span class="ml-2 text-gray-600">Cargando categorías...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-md bg-red-50 p-4 mb-6">
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
              Error al cargar categorías
            </h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            <button
              @click="loadCategoryGroups"
              class="mt-2 text-sm font-medium text-red-800 hover:text-red-600"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      </div>

      <!-- Category Groups List -->
      <div v-else-if="categoryGroups.length > 0" class="space-y-6">
        <div
          v-for="group in sortedCategoryGroups"
          :key="group.id"
          class="bg-white shadow rounded-lg overflow-hidden"
        >
          <!-- Group Header -->
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <span v-if="group.icon" class="text-2xl">{{
                    group.icon
                  }}</span>
                  <span
                    v-else
                    class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-gray-100"
                  >
                    <svg
                      class="h-4 w-4 text-gray-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                      ></path>
                    </svg>
                  </span>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">
                    {{ group.name }}
                  </h3>
                  <div
                    class="flex items-center space-x-2 text-sm text-gray-500"
                  >
                    <span
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="
                        group.isExpense
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800'
                      "
                    >
                      {{ group.isExpense ? "Gastos" : "Ingresos" }}
                    </span>
                    <span>{{ group.categories?.length || 0 }} categorías</span>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="showCreateCategoryModal(group.id)"
                  class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
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
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    ></path>
                  </svg>
                  Categoría
                </button>
                <button
                  @click="editGroup(group)"
                  class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
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
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    ></path>
                  </svg>
                  Editar
                </button>
                <button
                  @click="deleteGroup(group)"
                  class="inline-flex items-center px-3 py-1 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
                >
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
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    ></path>
                  </svg>
                  Eliminar
                </button>
              </div>
            </div>
          </div>

          <!-- Categories -->
          <div
            v-if="group.categories && group.categories.length > 0"
            class="px-6 py-4"
          >
            <div class="space-y-4">
              <div
                v-for="category in sortedCategories(group.categories)"
                :key="category.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <!-- Category Header -->
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center">
                    <span v-if="category.icon" class="text-xl mr-3">{{
                      category.icon
                    }}</span>
                    <span
                      v-else
                      class="inline-flex items-center justify-center h-6 w-6 rounded-full bg-gray-200 mr-3"
                    >
                      <svg
                        class="h-3 w-3 text-gray-600"
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
                    </span>
                    <div>
                      <h4 class="font-medium text-gray-900">
                        {{ category.name }}
                      </h4>
                      <div
                        class="flex items-center space-x-2 text-sm text-gray-500"
                      >
                        <span
                          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                          :class="
                            category.isIncome
                              ? 'bg-green-100 text-green-800'
                              : 'bg-blue-100 text-blue-800'
                          "
                        >
                          {{ category.isIncome ? "Ingresos" : "Gastos" }}
                        </span>
                        <span
                          >{{
                            category.subcategories?.length || 0
                          }}
                          subcategorías</span
                        >
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <button
                      @click="showCreateSubcategoryModal(category.id)"
                      class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs leading-4 font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <svg
                        class="w-3 h-3 mr-1"
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
                      Subcategoría
                    </button>
                    <button
                      @click="editCategory(category)"
                      class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs leading-4 font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <svg
                        class="w-3 h-3 mr-1"
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
                      Editar
                    </button>
                    <button
                      @click="deleteCategory(category)"
                      class="inline-flex items-center px-2 py-1 border border-red-300 shadow-sm text-xs leading-4 font-medium rounded text-red-700 bg-white hover:bg-red-50"
                    >
                      <svg
                        class="w-3 h-3 mr-1"
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
                      Eliminar
                    </button>
                  </div>
                </div>

                <!-- Subcategories -->
                <div
                  v-if="
                    category.subcategories && category.subcategories.length > 0
                  "
                  class="ml-8"
                >
                  <div class="flex flex-wrap gap-2">
                    <div
                      v-for="subcategory in sortedSubcategories(
                        category.subcategories
                      )"
                      :key="subcategory.id"
                      class="inline-flex items-center bg-gray-50 rounded-full px-3 py-1 text-sm"
                    >
                      <span class="text-gray-700">{{ subcategory.name }}</span>
                      <div class="ml-2 flex space-x-1">
                        <button
                          @click="editSubcategory(subcategory)"
                          class="text-gray-400 hover:text-gray-600"
                        >
                          <svg
                            class="w-3 h-3"
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
                        <button
                          @click="deleteSubcategory(subcategory)"
                          class="text-red-400 hover:text-red-600"
                        >
                          <svg
                            class="w-3 h-3"
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

                <!-- No subcategories message -->
                <div v-else class="ml-8 text-sm text-gray-500 italic">
                  No hay subcategorías.
                  <button
                    @click="showCreateSubcategoryModal(category.id)"
                    class="text-blue-600 hover:text-blue-500"
                  >
                    Crear la primera
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- No categories message -->
          <div v-else class="px-6 py-8 text-center text-gray-500">
            <svg
              class="mx-auto h-12 w-12 text-gray-300"
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
            <p class="mt-2 text-sm">No hay categorías en este grupo.</p>
            <button
              @click="showCreateCategoryModal(group.id)"
              class="mt-2 text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              Crear la primera categoría
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg
          class="mx-auto h-12 w-12 text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          ></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">
          No hay grupos de categorías
        </h3>
        <p class="mt-1 text-sm text-gray-500">
          Comienza creando tu primer grupo de categorías.
        </p>
        <div class="mt-6">
          <button
            @click="showCreateGroupModal = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
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
            Nuevo Grupo de Categorías
          </button>
        </div>
      </div>
    </div>

    <!-- Modales -->
    <CreateGroupModal
      v-if="showCreateGroupModal"
      @close="showCreateGroupModal = false"
      @created="onGroupCreated"
    />

    <EditGroupModal
      v-if="showEditGroupModal"
      :group="editingGroup"
      @close="closeEditGroupModal"
      @updated="onGroupUpdated"
    />

    <CreateCategoryModal
      v-if="showCreateCategoryModalFlag"
      :groupId="selectedGroupId"
      @close="closeCreateCategoryModal"
      @created="onCategoryCreated"
    />

    <EditCategoryModal
      v-if="showEditCategoryModal"
      :category="editingCategory"
      @close="closeEditCategoryModal"
      @updated="onCategoryUpdated"
    />

    <CreateSubcategoryModal
      v-if="showCreateSubcategoryModalFlag"
      :categoryId="selectedCategoryId"
      @close="closeCreateSubcategoryModal"
      @created="onSubcategoryCreated"
    />

    <EditSubcategoryModal
      v-if="showEditSubcategoryModal"
      :subcategory="editingSubcategory"
      @close="closeEditSubcategoryModal"
      @updated="onSubcategoryUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import {
  categoryGroupService,
  categoryService,
  subcategoryService,
  type CategoryGroup,
  type Category,
  type Subcategory,
} from "../../services/categoryService";

// Importar componentes de modales
import CreateGroupModal from "../../components/categories/CreateGroupModal.vue";
import EditGroupModal from "../../components/categories/EditGroupModal.vue";
import CreateCategoryModal from "../../components/categories/CreateCategoryModal.vue";
import EditCategoryModal from "../../components/categories/EditCategoryModal.vue";
import CreateSubcategoryModal from "../../components/categories/CreateSubcategoryModal.vue";
import EditSubcategoryModal from "../../components/categories/EditSubcategoryModal.vue";

// Estado principal
const isLoading = ref(false);
const error = ref<string | null>(null);
const categoryGroups = ref<CategoryGroup[]>([]);

// Estados de modales
const showCreateGroupModal = ref(false);
const showEditGroupModal = ref(false);
const showCreateCategoryModalFlag = ref(false);
const showEditCategoryModal = ref(false);
const showCreateSubcategoryModalFlag = ref(false);
const showEditSubcategoryModal = ref(false);

// Estados de edición
const editingGroup = ref<CategoryGroup | null>(null);
const editingCategory = ref<Category | null>(null);
const editingSubcategory = ref<Subcategory | null>(null);
const selectedGroupId = ref<number | null>(null);
const selectedCategoryId = ref<number | null>(null);

// Computed properties
const sortedCategoryGroups = computed(() => {
  return [...categoryGroups.value].sort((a, b) => {
    if (a.displayOrder !== b.displayOrder) {
      return a.displayOrder - b.displayOrder;
    }
    return a.name.localeCompare(b.name);
  });
});

const sortedCategories = (categories: Category[]) => {
  return [...categories].sort((a, b) => {
    if (a.displayOrder !== b.displayOrder) {
      return a.displayOrder - b.displayOrder;
    }
    return a.name.localeCompare(b.name);
  });
};

const sortedSubcategories = (subcategories: Subcategory[]) => {
  return [...subcategories].sort((a, b) => {
    if (a.displayOrder !== b.displayOrder) {
      return a.displayOrder - b.displayOrder;
    }
    return a.name.localeCompare(b.name);
  });
};

// Métodos principales
async function loadCategoryGroups() {
  isLoading.value = true;
  error.value = null;

  try {
    categoryGroups.value = await categoryGroupService.getAll();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Error desconocido";
    console.error("Error loading category groups:", err);
  } finally {
    isLoading.value = false;
  }
}

// Métodos de Group
function editGroup(group: CategoryGroup) {
  editingGroup.value = group;
  showEditGroupModal.value = true;
}

function closeEditGroupModal() {
  showEditGroupModal.value = false;
  editingGroup.value = null;
}

async function deleteGroup(group: CategoryGroup) {
  if (
    !confirm(
      `¿Estás seguro de que quieres eliminar el grupo "${group.name}"? Esto también eliminará todas sus categorías y subcategorías.`
    )
  ) {
    return;
  }

  try {
    await categoryGroupService.delete(group.id);
    await loadCategoryGroups();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Error eliminando grupo";
    console.error("Error deleting group:", err);
  }
}

function onGroupCreated() {
  showCreateGroupModal.value = false;
  loadCategoryGroups();
}

function onGroupUpdated() {
  closeEditGroupModal();
  loadCategoryGroups();
}

// Métodos de Category
function showCreateCategoryModal(groupId: number) {
  selectedGroupId.value = groupId;
  showCreateCategoryModalFlag.value = true;
}

function closeCreateCategoryModal() {
  showCreateCategoryModalFlag.value = false;
  selectedGroupId.value = null;
}

function editCategory(category: Category) {
  editingCategory.value = category;
  showEditCategoryModal.value = true;
}

function closeEditCategoryModal() {
  showEditCategoryModal.value = false;
  editingCategory.value = null;
}

async function deleteCategory(category: Category) {
  if (
    !confirm(
      `¿Estás seguro de que quieres eliminar la categoría "${category.name}"? Esto también eliminará todas sus subcategorías.`
    )
  ) {
    return;
  }

  try {
    await categoryService.delete(category.id);
    await loadCategoryGroups();
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Error eliminando categoría";
    console.error("Error deleting category:", err);
  }
}

function onCategoryCreated() {
  closeCreateCategoryModal();
  loadCategoryGroups();
}

function onCategoryUpdated() {
  closeEditCategoryModal();
  loadCategoryGroups();
}

// Métodos de Subcategory
function showCreateSubcategoryModal(categoryId: number) {
  selectedCategoryId.value = categoryId;
  showCreateSubcategoryModalFlag.value = true;
}

function closeCreateSubcategoryModal() {
  showCreateSubcategoryModalFlag.value = false;
  selectedCategoryId.value = null;
}

function editSubcategory(subcategory: Subcategory) {
  editingSubcategory.value = subcategory;
  showEditSubcategoryModal.value = true;
}

function closeEditSubcategoryModal() {
  showEditSubcategoryModal.value = false;
  editingSubcategory.value = null;
}

async function deleteSubcategory(subcategory: Subcategory) {
  if (
    !confirm(
      `¿Estás seguro de que quieres eliminar la subcategoría "${subcategory.name}"?`
    )
  ) {
    return;
  }

  try {
    await subcategoryService.delete(subcategory.id);
    await loadCategoryGroups();
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Error eliminando subcategoría";
    console.error("Error deleting subcategory:", err);
  }
}

function onSubcategoryCreated() {
  closeCreateSubcategoryModal();
  loadCategoryGroups();
}

function onSubcategoryUpdated() {
  closeEditSubcategoryModal();
  loadCategoryGroups();
}

// Lifecycle
onMounted(() => {
  loadCategoryGroups();
});
</script>
