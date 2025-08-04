// Servicio para gestionar categorías
import { useAuthStore } from "../stores/authStore";

// Interfaces para CategoryGroup
export interface CategoryGroup {
  id: number;
  name: string;
  isExpense: boolean;
  icon?: string;
  displayOrder: number;
  createdAt?: string;
  updatedAt?: string;
  categories?: Category[];
}

export interface CreateCategoryGroupRequest {
  name: string;
  isExpense: boolean;
  icon?: string;
  displayOrder?: number;
}

export interface UpdateCategoryGroupRequest {
  name?: string;
  isExpense?: boolean;
  icon?: string;
  displayOrder?: number;
}

// Interfaces para Category
export interface Category {
  id: number;
  categoryGroupId: number;
  name: string;
  isIncome: boolean;
  icon?: string;
  displayOrder: number;
  createdAt?: string;
  updatedAt?: string;
  subcategories?: Subcategory[];
}

export interface CreateCategoryRequest {
  categoryGroupId: number;
  name: string;
  isIncome: boolean;
  icon?: string;
  displayOrder?: number;
}

export interface UpdateCategoryRequest {
  categoryGroupId?: number;
  name?: string;
  isIncome?: boolean;
  icon?: string;
  displayOrder?: number;
}

// Interfaces para Subcategory
export interface Subcategory {
  id: number;
  categoryId: number;
  name: string;
  displayOrder: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface CreateSubcategoryRequest {
  categoryId: number;
  name: string;
  displayOrder?: number;
}

export interface UpdateSubcategoryRequest {
  categoryId?: number;
  name?: string;
  displayOrder?: number;
}

// Configuración de la API
const API_BASE_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Función helper para obtener headers de autenticación
function getAuthHeaders() {
  const authStore = useAuthStore();
  return {
    "Content-Type": "application/json",
    ...(authStore.accessToken && {
      Authorization: `Bearer ${authStore.accessToken}`,
    }),
  };
}

// Función helper para manejar respuestas de la API
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `HTTP ${response.status}: ${response.statusText}`
    );
  }
  return response.json();
}

// =============================
// SERVICIOS REST API
// =============================

// CategoryGroup Services
export const categoryGroupService = {
  // Obtener todos los grupos de categorías
  async getAll(): Promise<CategoryGroup[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/categories/groups`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<CategoryGroup[]>(response);
  },

  // Obtener un grupo específico
  async getById(groupId: number): Promise<CategoryGroup> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/groups/${groupId}`,
      {
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<CategoryGroup>(response);
  },

  // Crear un nuevo grupo
  async create(data: CreateCategoryGroupRequest): Promise<CategoryGroup> {
    const response = await fetch(`${API_BASE_URL}/api/v1/categories/groups`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<CategoryGroup>(response);
  },

  // Actualizar un grupo existente
  async update(
    groupId: number,
    data: UpdateCategoryGroupRequest
  ): Promise<CategoryGroup> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/groups/${groupId}`,
      {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    );
    return handleResponse<CategoryGroup>(response);
  },

  // Eliminar un grupo
  async delete(groupId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/groups/${groupId}`,
      {
        method: "DELETE",
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }
  },
};

// Category Services
export const categoryService = {
  // Obtener categorías por grupo
  async getByGroup(groupId: number): Promise<Category[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/groups/${groupId}/categories`,
      {
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<Category[]>(response);
  },

  // Obtener una categoría específica
  async getById(categoryId: number): Promise<Category> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/${categoryId}`,
      {
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<Category>(response);
  },

  // Crear una nueva categoría
  async create(data: CreateCategoryRequest): Promise<Category> {
    const response = await fetch(`${API_BASE_URL}/api/v1/categories/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Category>(response);
  },

  // Actualizar una categoría existente
  async update(
    categoryId: number,
    data: UpdateCategoryRequest
  ): Promise<Category> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/${categoryId}`,
      {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    );
    return handleResponse<Category>(response);
  },

  // Eliminar una categoría
  async delete(categoryId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/${categoryId}`,
      {
        method: "DELETE",
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }
  },
};

// Subcategory Services
export const subcategoryService = {
  // Obtener subcategorías por categoría
  async getByCategory(categoryId: number): Promise<Subcategory[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/${categoryId}/subcategories`,
      {
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<Subcategory[]>(response);
  },

  // Obtener una subcategoría específica
  async getById(subcategoryId: number): Promise<Subcategory> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/subcategories/${subcategoryId}`,
      {
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<Subcategory>(response);
  },

  // Crear una nueva subcategoría
  async create(data: CreateSubcategoryRequest): Promise<Subcategory> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/subcategories`,
      {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    );
    return handleResponse<Subcategory>(response);
  },

  // Actualizar una subcategoría existente
  async update(
    subcategoryId: number,
    data: UpdateSubcategoryRequest
  ): Promise<Subcategory> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/subcategories/${subcategoryId}`,
      {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    );
    return handleResponse<Subcategory>(response);
  },

  // Eliminar una subcategoría
  async delete(subcategoryId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/categories/subcategories/${subcategoryId}`,
      {
        method: "DELETE",
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }
  },
};

// =============================
// SERVICIOS GRAPHQL
// =============================

const GRAPHQL_URL = `${API_BASE_URL}/graphql`;

// Función helper para ejecutar queries GraphQL
async function executeGraphQL<T>(query: string, variables?: any): Promise<T> {
  const response = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  const result = await response.json();

  if (result.errors) {
    throw new Error(result.errors[0]?.message || "GraphQL Error");
  }

  return result.data;
}

// GraphQL Queries
export const categoryGraphQLService = {
  // Obtener todos los grupos de categorías con sus categorías y subcategorías
  async getAllCategoryGroups(): Promise<{ myCategoryGroups: CategoryGroup[] }> {
    const query = `
      query GetMyCategoryGroups {
        myCategoryGroups {
          id
          name
          isExpense
          icon
          displayOrder
          createdAt
          updatedAt
          categories {
            id
            categoryGroupId
            name
            isIncome
            icon
            displayOrder
            createdAt
            updatedAt
            subcategories {
              id
              categoryId
              name
              displayOrder
              createdAt
              updatedAt
            }
          }
        }
      }
    `;
    return executeGraphQL<{ myCategoryGroups: CategoryGroup[] }>(query);
  },

  // Obtener un grupo específico
  async getCategoryGroup(
    groupId: number
  ): Promise<{ myCategoryGroup: CategoryGroup | null }> {
    const query = `
      query GetMyCategoryGroup($groupId: Int!) {
        myCategoryGroup(groupId: $groupId) {
          id
          name
          isExpense
          icon
          displayOrder
          createdAt
          updatedAt
          categories {
            id
            categoryGroupId
            name
            isIncome
            icon
            displayOrder
            createdAt
            updatedAt
            subcategories {
              id
              categoryId
              name
              displayOrder
              createdAt
              updatedAt
            }
          }
        }
      }
    `;
    return executeGraphQL<{ myCategoryGroup: CategoryGroup | null }>(query, {
      groupId,
    });
  },

  // Obtener categorías por grupo
  async getCategoriesByGroup(
    groupId: number
  ): Promise<{ myCategoriesByGroup: Category[] }> {
    const query = `
      query GetMyCategoriesByGroup($groupId: Int!) {
        myCategoriesByGroup(groupId: $groupId) {
          id
          categoryGroupId
          name
          isIncome
          icon
          displayOrder
          createdAt
          updatedAt
          subcategories {
            id
            categoryId
            name
            displayOrder
            createdAt
            updatedAt
          }
        }
      }
    `;
    return executeGraphQL<{ myCategoriesByGroup: Category[] }>(query, {
      groupId,
    });
  },

  // Obtener una categoría específica
  async getCategory(
    categoryId: number
  ): Promise<{ myCategory: Category | null }> {
    const query = `
      query GetMyCategory($categoryId: Int!) {
        myCategory(categoryId: $categoryId) {
          id
          categoryGroupId
          name
          isIncome
          icon
          displayOrder
          createdAt
          updatedAt
          subcategories {
            id
            categoryId
            name
            displayOrder
            createdAt
            updatedAt
          }
        }
      }
    `;
    return executeGraphQL<{ myCategory: Category | null }>(query, {
      categoryId,
    });
  },

  // Obtener subcategorías por categoría
  async getSubcategoriesByCategory(
    categoryId: number
  ): Promise<{ mySubcategoriesByCategory: Subcategory[] }> {
    const query = `
      query GetMySubcategoriesByCategory($categoryId: Int!) {
        mySubcategoriesByCategory(categoryId: $categoryId) {
          id
          categoryId
          name
          displayOrder
          createdAt
          updatedAt
        }
      }
    `;
    return executeGraphQL<{ mySubcategoriesByCategory: Subcategory[] }>(query, {
      categoryId,
    });
  },

  // Obtener una subcategoría específica
  async getSubcategory(
    subcategoryId: number
  ): Promise<{ mySubcategory: Subcategory | null }> {
    const query = `
      query GetMySubcategory($subcategoryId: Int!) {
        mySubcategory(subcategoryId: $subcategoryId) {
          id
          categoryId
          name
          displayOrder
          createdAt
          updatedAt
        }
      }
    `;
    return executeGraphQL<{ mySubcategory: Subcategory | null }>(query, {
      subcategoryId,
    });
  },
};
