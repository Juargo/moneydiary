// Servicio para gestionar patrones de descripción
export interface SubcategoryInfo {
  id: number;
  name: string;
  categoryId: number;
  categoryName: string;
}

export interface DescriptionPattern {
  id: number;
  userId: number;
  name: string;
  pattern: string;
  patternType: "contains" | "starts_with" | "ends_with" | "regex" | "exact";
  subcategoryId: number;
  subcategory: SubcategoryInfo;
  priority: number;
  isCaseSensitive: boolean;
  isActive: boolean;
  autoApply: boolean;
  notes?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface CreatePatternRequest {
  name: string;
  pattern: string;
  patternType: "contains" | "starts_with" | "ends_with" | "regex" | "exact";
  subcategoryId: number;
  priority: number;
  isCaseSensitive: boolean;
  isActive: boolean;
  autoApply: boolean;
  notes?: string;
}

export interface UpdatePatternRequest {
  name?: string;
  pattern?: string;
  patternType?: "contains" | "starts_with" | "ends_with" | "regex" | "exact";
  subcategoryId?: number;
  priority?: number;
  isCaseSensitive?: boolean;
  isActive?: boolean;
  autoApply?: boolean;
  notes?: string;
}

export interface PatternTestRequest {
  description: string;
  patternIds?: number[];
}

export interface PatternTestResult {
  patternId: number;
  patternName: string;
  pattern: string;
  patternType: string;
  matched: boolean;
  matchedText?: string;
  subcategory: SubcategoryInfo;
}

export interface PatternTestResponse {
  description: string;
  results: PatternTestResult[];
  bestMatch?: PatternTestResult;
}

export interface PatternSuggestion {
  suggestedPattern: string;
  patternType: string;
  descriptionSample: string;
  occurrenceCount: number;
  suggestedSubcategoryId?: number;
  confidenceScore: number;
}

export interface PatternSuggestionResponse {
  suggestions: PatternSuggestion[];
}

export interface PatternStatistics {
  totalPatterns: number;
  activePatterns: number;
  autoApplyPatterns: number;
  totalMatches: number;
}

class PatternService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem("accessToken");

    const response = await fetch(
      `${this.baseUrl}/api/description-patterns${endpoint}`,
      {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
      }
    );

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Error desconocido" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Obtener patrones del usuario
  async getPatterns(
    activeOnly: boolean = true,
    skip: number = 0,
    limit: number = 100
  ): Promise<DescriptionPattern[]> {
    return this.request(
      `/?active_only=${activeOnly}&skip=${skip}&limit=${limit}`
    );
  }

  // Obtener un patrón específico
  async getPattern(patternId: number): Promise<DescriptionPattern> {
    return this.request(`/${patternId}`);
  }

  // Crear un nuevo patrón
  async createPattern(data: CreatePatternRequest): Promise<DescriptionPattern> {
    return this.request("/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Actualizar un patrón
  async updatePattern(
    patternId: number,
    data: UpdatePatternRequest
  ): Promise<DescriptionPattern> {
    return this.request(`/${patternId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // Eliminar un patrón
  async deletePattern(patternId: number): Promise<{ message: string }> {
    return this.request(`/${patternId}`, {
      method: "DELETE",
    });
  }

  // Probar patrones contra una descripción
  async testPatterns(data: PatternTestRequest): Promise<PatternTestResponse> {
    return this.request("/test", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Generar sugerencias de patrones
  async getSuggestions(
    limit: number = 10,
    minOccurrences: number = 3
  ): Promise<PatternSuggestionResponse> {
    return this.request("/suggestions", {
      method: "POST",
      body: JSON.stringify({
        limit,
        min_occurrences: minOccurrences,
      }),
    });
  }

  // Obtener estadísticas
  async getStatistics(): Promise<PatternStatistics> {
    return this.request("/statistics/summary");
  }

  // Aplicar patrón a transacciones
  async applyPattern(
    patternId: number,
    transactionIds?: number[]
  ): Promise<{ message: string; applied_count: number }> {
    return this.request(`/${patternId}/apply`, {
      method: "POST",
      body: JSON.stringify({ transaction_ids: transactionIds }),
    });
  }
}

export const patternService = new PatternService();
