import { defineStore } from "pinia";
import { ref, computed } from "vue";
import {
  patternService,
  type DescriptionPattern,
  type PatternTestResponse,
  type PatternSuggestionResponse,
  type PatternStatistics,
  type SubcategoryInfo,
} from "../services/patternService";

export interface PatternTestResult {
  patternId: number;
  patternName: string;
  pattern: string;
  patternType: string;
  matched: boolean;
  matchedText?: string;
  subcategory: SubcategoryInfo;
}

export interface PatternSuggestion {
  suggestedPattern: string;
  patternType: string;
  descriptionSample: string;
  occurrenceCount: number;
  suggestedSubcategoryId?: number;
  confidenceScore: number;
}

export interface Category {
  id: number;
  name: string;
  subcategories: Subcategory[];
}

export interface Subcategory {
  id: number;
  name: string;
  categoryId: number;
  categoryName: string;
}

export const usePatternStore = defineStore("patterns", () => {
  // State
  const patterns = ref<DescriptionPattern[]>([]);
  const categories = ref<Category[]>([]);
  const subcategories = ref<Subcategory[]>([]);
  const testResults = ref<PatternTestResponse | null>(null);
  const statistics = ref<PatternStatistics>({
    totalPatterns: 0,
    activePatterns: 0,
    autoApplyPatterns: 0,
    totalMatches: 0,
  });
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const activePatterns = computed(() =>
    patterns.value.filter((p) => p.isActive)
  );

  const inactivePatterns = computed(() =>
    patterns.value.filter((p) => !p.isActive)
  );

  const patternsByPriority = computed(() =>
    [...patterns.value].sort((a, b) => b.priority - a.priority)
  );

  // Actions
  async function loadPatterns(activeOnly = false, skip = 0, limit = 50) {
    try {
      loading.value = true;
      error.value = null;

      const response = await patternService.getPatterns(
        activeOnly,
        skip,
        limit
      );
      patterns.value = response;

      return response;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Error loading patterns";
      console.error("Error loading patterns:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function loadCategories() {
    try {
      loading.value = true;
      error.value = null;

      // Por ahora retornamos un array vacío ya que no tenemos el servicio de categorías
      // Esto se debe implementar cuando esté disponible
      const response: Category[] = [];
      categories.value = response;

      // Extract all subcategories for easier access
      subcategories.value = response.flatMap((category: Category) =>
        category.subcategories.map((sub: Subcategory) => ({
          ...sub,
          categoryName: category.name,
        }))
      );

      return response;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Error loading categories";
      console.error("Error loading categories:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createPattern(input: any): Promise<DescriptionPattern> {
    try {
      loading.value = true;
      error.value = null;

      const newPattern = await patternService.createPattern(input);
      patterns.value.push(newPattern);

      // Update statistics
      await loadStatistics();

      return newPattern;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Error creating pattern";
      console.error("Error creating pattern:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updatePattern(
    id: number,
    input: any
  ): Promise<DescriptionPattern> {
    try {
      loading.value = true;
      error.value = null;

      const updatedPattern = await patternService.updatePattern(id, input);

      const index = patterns.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        patterns.value[index] = updatedPattern;
      }

      // Update statistics
      await loadStatistics();

      return updatedPattern;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Error updating pattern";
      console.error("Error updating pattern:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deletePattern(id: number): Promise<boolean> {
    try {
      loading.value = true;
      error.value = null;

      const response = await patternService.deletePattern(id);

      if (response.message) {
        patterns.value = patterns.value.filter((p) => p.id !== id);

        // Update statistics
        await loadStatistics();

        return true;
      }

      return false;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Error deleting pattern";
      console.error("Error deleting pattern:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function testPatterns(input: any): Promise<PatternTestResponse> {
    try {
      loading.value = true;
      error.value = null;

      const response = await patternService.testPatterns(input);
      testResults.value = response;
      return response;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Error testing patterns";
      console.error("Error testing patterns:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function getPatternSuggestions(
    input: any
  ): Promise<PatternSuggestionResponse> {
    try {
      loading.value = true;
      error.value = null;

      const response = await patternService.getSuggestions(
        input.limit,
        input.minOccurrences
      );
      return response;
    } catch (err) {
      error.value =
        err instanceof Error
          ? err.message
          : "Error getting pattern suggestions";
      console.error("Error getting pattern suggestions:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function loadStatistics(): Promise<PatternStatistics> {
    try {
      const stats = await patternService.getStatistics();
      statistics.value = stats;
      return stats;
    } catch (err) {
      console.error("Error loading statistics:", err);
      throw err;
    }
  }

  async function applyPatternToTransactions(
    patternId: number,
    transactionIds?: number[]
  ): Promise<number> {
    try {
      loading.value = true;
      error.value = null;

      const response = await patternService.applyPattern(
        patternId,
        transactionIds
      );

      // Update statistics after applying patterns
      await loadStatistics();

      return response.applied_count;
    } catch (err) {
      error.value =
        err instanceof Error
          ? err.message
          : "Error applying pattern to transactions";
      console.error("Error applying pattern to transactions:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function getPatternById(id: number): DescriptionPattern | undefined {
    return patterns.value.find((p) => p.id === id);
  }

  function getSubcategoryById(id: number): Subcategory | undefined {
    return subcategories.value.find((s) => s.id === id);
  }

  function getCategoryById(id: number): Category | undefined {
    return categories.value.find((c) => c.id === id);
  }

  function clearTestResults() {
    testResults.value = null;
  }

  // Reset store
  function $reset() {
    patterns.value = [];
    categories.value = [];
    subcategories.value = [];
    statistics.value = {
      totalPatterns: 0,
      activePatterns: 0,
      autoApplyPatterns: 0,
      totalMatches: 0,
    };
    testResults.value = null;
    loading.value = false;
    error.value = null;
  }

  return {
    // State
    patterns,
    categories,
    subcategories,
    statistics,
    testResults,
    loading,
    error,

    // Computed
    activePatterns,
    inactivePatterns,
    patternsByPriority,

    // Actions
    loadPatterns,
    loadCategories,
    createPattern,
    updatePattern,
    deletePattern,
    testPatterns,
    getPatternSuggestions,
    loadStatistics,
    applyPatternToTransactions,
    getPatternById,
    getSubcategoryById,
    getCategoryById,
    clearTestResults,
    $reset,
  };
});
