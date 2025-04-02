/**
 * GraphQL client utility for MoneyDiary
 */

/**
 * Send a GraphQL request to the API
 * 
 * @param {string} query - GraphQL query string
 * @param {Object} variables - Variables for the query
 * @returns {Promise<Object>} - The data returned from the API
 */
export async function fetchGraphQL(query, variables = {}) {
  const response = await fetch('/api/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  if (!response.ok) {
    throw new Error(`GraphQL request failed: ${response.statusText}`);
  }

  const result = await response.json();
  
  if (result.errors) {
    throw new Error(result.errors.map(e => e.message).join('\n'));
  }
  
  return result.data;
}

// Common queries
export const BUDGETS_QUERY = `
  query GetBudgets($userId: Int!) {
    budgets(userId: $userId) {
      id
      name
      description
    }
  }
`;

export const CATEGORIES_QUERY = `
  query GetCategories($budgetId: Int!) {
    categories(budgetId: $budgetId) {
      id
      name
      description
    }
  }
`;

export const SUBCATEGORIES_QUERY = `
  query GetSubcategories($categoryId: Int!) {
    subcategories(categoryId: $categoryId) {
      id
      name
    }
  }
`;

export const PATTERNS_QUERY = `
  query GetPatterns($subcategoryId: Int!) {
    patterns(subcategoryId: $subcategoryId) {
      id
      expName
    }
  }
`;
