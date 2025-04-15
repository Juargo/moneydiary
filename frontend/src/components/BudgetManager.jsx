import React, { useState, useEffect } from 'react';
import PatternIgnoreTable from './PatternIgnoreTable';
import BudgetAccordion from './BudgetAccordion';
import BudgetSummary from './BudgetSummary';
import './BudgetManager.css'; // Import a CSS file instead

const BUDGET_CONFIG_QUERY = `
  query GetBudgetConfig($userId: Int!) {
    budgetConfig(userId: $userId) {
      userId
      userName
      budgetId
      budgetName
      categoryId
      categoryName
      subcategoryId
      subcategoryName
      subcategoryBudgetAmount
      patternId
      patternText
    }
  }
`;

const PATTERN_IGNORES_QUERY = `
  query GetPatternIgnores($userId: Int!) {
    patternIgnores(userId: $userId) {
      id
      expName
      description
      createdAt
      updatedAt
    }
  }
`;

export default function BudgetManager() {
  // State for data - initialize with empty arrays/objects instead of using props
  const [budgetData, setBudgetData] = useState([]);
  const [patternIgnores, setPatternIgnores] = useState([]);
  const [totals, setTotals] = useState({ totalBudgeted: 0, totalSpent: 0, totalRemaining: 0 });
  const [userId, setUserId] = useState(0); 
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // State for modals
  const [showPatternModal, setShowPatternModal] = useState(false);
  const [showEditPatternModal, setShowEditPatternModal] = useState(false);
  const [showDeletePatternModal, setShowDeletePatternModal] = useState(false);
  const [showSubcategoryModal, setShowSubcategoryModal] = useState(false);
  const [showEditSubcategoryModal, setShowEditSubcategoryModal] = useState(false);
  const [showDeleteSubcategoryModal, setShowDeleteSubcategoryModal] = useState(false);
  const [showPatternIgnoreModal, setShowPatternIgnoreModal] = useState(false);
  const [showDeletePatternIgnoreModal, setShowDeletePatternIgnoreModal] = useState(false);
  
  // Form state
  const [currentPattern, setCurrentPattern] = useState({ id: null, expName: '', subcategoryId: null });
  const [currentSubcategory, setCurrentSubcategory] = useState({ id: null, name: '', categoryId: null });
  const [currentPatternIgnore, setCurrentPatternIgnore] = useState({ id: null, expName: '', description: '' });

  // Improved function to get current user from localStorage
  const getCurrentUserFromLocalStorage = () => {
    try {
      const userFromStorage = localStorage.getItem('currentUser');
      if (userFromStorage) {
        const parsedUser = JSON.parse(userFromStorage);
        if (parsedUser && parsedUser.id) {
          const parsedUserId = parseInt(parsedUser.id);
          setUserId(parsedUserId);
          setCurrentUser(parsedUser);
          console.log("User ID set from localStorage:", parsedUserId);
          return true;
        }
      }
      console.warn("No user found in localStorage or invalid user data");
      return false;
    } catch (error) {
      console.error('Error accessing localStorage:', error);
      return false;
    }
  };

  // Load user data from localStorage on component mount and reload on changes
  useEffect(() => {
    const userFound = getCurrentUserFromLocalStorage();
    if (userFound) {
      // Only reload data if we have a valid userId
      if (userId > 0) {
        reloadDataWithUserId(userId);
      }
    } else {
      // If no user found, still mark loading as complete
      setIsLoading(false);
    }
  }, [userId]); // Add userId to dependency array to reload when it changes

  // GraphQL fetch function
  const fetchGraphQL = async (query, variables = {}) => {
    try {
      const response = await fetch('http://localhost:8000/graphql', {
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
      return result.data;
    } catch (error) {
      console.error('GraphQL fetch error:', error);
      return null;
    }
  };

  // Function to reload data with the correct user ID
  const reloadDataWithUserId = async (userId) => {
    if (!userId) return;
    
    setIsLoading(true);
    
    try {
      // Fetch budget config for the actual user
      const budgetConfigResponse = await fetchGraphQL(BUDGET_CONFIG_QUERY, { userId });
      
      if (!budgetConfigResponse || !budgetConfigResponse.budgetConfig || 
          budgetConfigResponse.budgetConfig.length === 0) {
        console.warn('No budget configuration found for user ID:', userId);
        return;
      }

      // Process budget config data
      const configItems = budgetConfigResponse.budgetConfig;
      const budgetsMap = new Map();
      
      configItems.forEach(item => {
        // Add budget level if not exists
        if (!budgetsMap.has(item.budgetId)) {
          budgetsMap.set(item.budgetId, {
            id: item.budgetId,
            name: item.budgetName,
            description: `Budget for ${item.userName}`,
            categories: new Map()
          });
        }
        
        const budget = budgetsMap.get(item.budgetId);
        
        // Add category level if not exists
        if (!budget.categories.has(item.categoryId)) {
          budget.categories.set(item.categoryId, {
            id: item.categoryId,
            name: item.categoryName,
            description: `Category in ${item.budgetName}`,
            subcategories: new Map(),
            limit: 1000,
            spent: 800,
            remaining: 200,
            progress: 80
          });
        }
        
        const category = budget.categories.get(item.categoryId);
        
        // Add subcategory level if not exists
        if (!category.subcategories.has(item.subcategoryId)) {
          category.subcategories.set(item.subcategoryId, {
            id: item.subcategoryId,
            name: item.subcategoryName,
            patterns: []
          });
        }
        
        // Add pattern if it exists
        if (item.patternId && item.patternText) {
          const subcategory = category.subcategories.get(item.subcategoryId);
          // Avoid duplicate patterns
          if (!subcategory.patterns.some(p => p.id === item.patternId)) {
            subcategory.patterns.push({
              id: item.patternId,
              expName: item.patternText
            });
          }
        }
      });
      
      // Convert maps to arrays for rendering
      const newBudgetData = Array.from(budgetsMap.values()).map(budget => ({
        ...budget,
        categories: Array.from(budget.categories.values()).map(category => ({
          ...category,
          subcategories: Array.from(category.subcategories.values())
        }))
      }));
      
      setBudgetData(newBudgetData);
      
      // Calculate new totals
      const allCategories = newBudgetData.flatMap(budget => budget.categories || []);
      const totalBudgeted = allCategories.reduce((sum, cat) => sum + cat.limit, 0);
      const totalSpent = allCategories.reduce((sum, cat) => sum + cat.spent, 0);
      const totalRemaining = totalBudgeted - totalSpent;
      
      setTotals({
        totalBudgeted,
        totalSpent,
        totalRemaining
      });
      
      // Get pattern ignores for the actual user
      const patternIgnoresResponse = await fetchGraphQL(PATTERN_IGNORES_QUERY, { userId });
      
      if (patternIgnoresResponse && patternIgnoresResponse.patternIgnores) {
        setPatternIgnores(patternIgnoresResponse.patternIgnores);
      }
    } catch (error) {
      console.error('Error reloading data with user ID:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle pattern creation
  const handleCreatePattern = async (pattern) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/patterns/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          match_text: pattern.expName,
          subcategory_id: pattern.subcategoryId
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error creating pattern');
      }
      
      const newPattern = await response.json();
      
      // Update state with the new pattern
      setBudgetData(prevData => {
        return prevData.map(budget => ({
          ...budget,
          categories: budget.categories.map(category => ({
            ...category,
            subcategories: category.subcategories.map(subcategory => {
              if (subcategory.id === pattern.subcategoryId) {
                return {
                  ...subcategory,
                  patterns: [...subcategory.patterns, { 
                    id: newPattern.id,
                    expName: newPattern.match_text
                  }]
                };
              }
              return subcategory;
            })
          }))
        }));
      });
      
      showNotification('Pattern created successfully', 'success');
    } catch (error) {
      console.error('Error creating pattern:', error);
      showNotification(error.message || 'Error creating pattern', 'error');
    }
  };

  // Function to handle pattern update
  const handleUpdatePattern = async (pattern) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/patterns/${pattern.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          match_text: pattern.expName
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error updating pattern');
      }
      
      const updatedPattern = await response.json();
      
      // Update state with the updated pattern
      setBudgetData(prevData => {
        return prevData.map(budget => ({
          ...budget,
          categories: budget.categories.map(category => ({
            ...category,
            subcategories: category.subcategories.map(subcategory => ({
              ...subcategory,
              patterns: subcategory.patterns.map(p => 
                p.id === pattern.id ? { ...p, expName: updatedPattern.match_text } : p
              )
            }))
          }))
        }));
      });
      
      showNotification('Pattern updated successfully', 'success');
    } catch (error) {
      console.error('Error updating pattern:', error);
      showNotification(error.message || 'Error updating pattern', 'error');
    }
  };

  // Function to handle pattern deletion
  const handleDeletePattern = async (patternId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/patterns/${patternId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error deleting pattern');
      }
      
      // Update state to remove the deleted pattern
      setBudgetData(prevData => {
        return prevData.map(budget => ({
          ...budget,
          categories: budget.categories.map(category => ({
            ...category,
            subcategories: category.subcategories.map(subcategory => ({
              ...subcategory,
              patterns: subcategory.patterns.filter(p => p.id !== patternId)
            }))
          }))
        }));
      });
      
      showNotification('Pattern deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting pattern:', error);
      showNotification(error.message || 'Error deleting pattern', 'error');
    }
  };

  // Function to handle subcategory creation
  const handleCreateSubcategory = async (subcategory) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/subcategories/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: subcategory.name,
          category_id: subcategory.categoryId
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error creating subcategory');
      }
      
      const newSubcategory = await response.json();
      
      // Update state with the new subcategory
      setBudgetData(prevData => {
        return prevData.map(budget => ({
          ...budget,
          categories: budget.categories.map(category => {
            if (category.id === subcategory.categoryId) {
              return {
                ...category,
                subcategories: [
                  ...category.subcategories, 
                  { id: newSubcategory.id, name: newSubcategory.name, patterns: [] }
                ]
              };
            }
            return category;
          })
        }));
      });
      
      showNotification('Subcategory created successfully', 'success');
    } catch (error) {
      console.error('Error creating subcategory:', error);
      showNotification(error.message || 'Error creating subcategory', 'error');
    }
  };

  // Function to handle subcategory update
  const handleUpdateSubcategory = async (subcategory) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/subcategories/${subcategory.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: subcategory.name
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error updating subcategory');
      }
      
      const updatedSubcategory = await response.json();
      
      // Update state with the updated subcategory
      setBudgetData(prevData => {
        return prevData.map(budget => ({
          ...budget,
          categories: budget.categories.map(category => ({
            ...category,
            subcategories: category.subcategories.map(sub => 
              sub.id === subcategory.id ? { ...sub, name: updatedSubcategory.name } : sub
            )
          }))
        }));
      });
      
      showNotification('Subcategory updated successfully', 'success');
    } catch (error) {
      console.error('Error updating subcategory:', error);
      showNotification(error.message || 'Error updating subcategory', 'error');
    }
  };

  // Function to handle subcategory deletion
  const handleDeleteSubcategory = async (subcategoryId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/subcategories/${subcategoryId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error deleting subcategory');
      }
      
      // Update state to remove the deleted subcategory
      setBudgetData(prevData => {
        return prevData.map(budget => ({
          ...budget,
          categories: budget.categories.map(category => ({
            ...category,
            subcategories: category.subcategories.filter(sub => sub.id !== subcategoryId)
          }))
        }));
      });
      
      showNotification('Subcategory deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting subcategory:', error);
      showNotification(error.message || 'Error deleting subcategory', 'error');
    }
  };

  // Function to handle pattern ignore creation/update
  const handleSavePatternIgnore = async (patternIgnore) => {
    try {
      let response;
      if (patternIgnore.id) {
        // Update existing pattern ignore
        response = await fetch(`http://localhost:8000/api/v1/pattern-ignores/${patternIgnore.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            match_text: patternIgnore.expName,
            description: patternIgnore.description,
            user_id: userId
          }),
        });
      } else {
        // Create new pattern ignore
        response = await fetch('http://localhost:8000/api/v1/pattern-ignores/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            match_text: patternIgnore.expName,
            description: patternIgnore.description,
            user_id: userId
          }),
        });
      }
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error saving pattern ignore');
      }
      
      // Reload pattern ignores after creating/updating
      const patternIgnoresResponse = await fetchGraphQL(PATTERN_IGNORES_QUERY, { userId });
      if (patternIgnoresResponse && patternIgnoresResponse.patternIgnores) {
        setPatternIgnores(patternIgnoresResponse.patternIgnores);
      }
      
      showNotification(`Pattern ignore ${patternIgnore.id ? 'updated' : 'created'} successfully`, 'success');
    } catch (error) {
      console.error('Error saving pattern ignore:', error);
      showNotification(error.message || 'Error saving pattern ignore', 'error');
    }
  };

  // Function to handle pattern ignore deletion
  const handleDeletePatternIgnore = async (patternIgnoreId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/pattern-ignores/${patternIgnoreId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error deleting pattern ignore');
      }
      
      // Update state to remove the deleted pattern ignore
      setPatternIgnores(prevIgnores => prevIgnores.filter(p => p.id !== patternIgnoreId));
      
      showNotification('Pattern ignore deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting pattern ignore:', error);
      showNotification(error.message || 'Error deleting pattern ignore', 'error');
    }
  };

  // Simple notification function
  const showNotification = (message, type = 'info') => {
    alert(message); // In a real app, use a toast component
  };

  return (
    <div>
      {isLoading ? (
        <div className="flex items-center justify-center p-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="ml-3">Cargando datos del presupuesto...</p>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-800">Administra tus Presupuestos</h1>
              <button className="bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg flex items-center">
                <i className="fas fa-plus mr-2"></i> Nuevo Presupuesto
              </button>
            </div>
          </div>

          {/* Pattern Ignores Section */}
          <PatternIgnoreTable 
            patternIgnores={patternIgnores}
            onAddPatternIgnore={() => {
              setCurrentPatternIgnore({ id: null, expName: '', description: '' });
              setShowPatternIgnoreModal(true);
            }}
            onEditPatternIgnore={(pattern) => {
              setCurrentPatternIgnore(pattern);
              setShowPatternIgnoreModal(true);
            }}
            onDeletePatternIgnore={(pattern) => {
              setCurrentPatternIgnore(pattern);
              setShowDeletePatternIgnoreModal(true);
            }}
          />
          
          {/* Budget Accordion */}
          <BudgetAccordion 
            budgetData={budgetData}
            onAddPattern={(subcategoryId, subcategoryName) => {
              setCurrentPattern({ id: null, expName: '', subcategoryId });
              setShowPatternModal(true);
            }}
            onEditPattern={(pattern, subcategoryId) => {
              setCurrentPattern({ ...pattern, subcategoryId });
              setShowEditPatternModal(true);
            }}
            onDeletePattern={(pattern) => {
              setCurrentPattern(pattern);
              setShowDeletePatternModal(true);
            }}
            onAddSubcategory={(categoryId) => {
              setCurrentSubcategory({ id: null, name: '', categoryId });
              setShowSubcategoryModal(true);
            }}
            onEditSubcategory={(subcategory) => {
              setCurrentSubcategory(subcategory);
              setShowEditSubcategoryModal(true);
            }}
            onDeleteSubcategory={(subcategory) => {
              setCurrentSubcategory(subcategory);
              setShowDeleteSubcategoryModal(true);
            }}
          />

          {/* All modals - rendered conditionally */}
          {showPatternModal && (
            <div className="modal">
              <div className="modal-content">
                <h2>Add Pattern</h2>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  handleCreatePattern(currentPattern);
                  setShowPatternModal(false);
                }}>
                  <input
                    type="text"
                    value={currentPattern.expName}
                    onChange={(e) => setCurrentPattern({...currentPattern, expName: e.target.value})}
                    placeholder="Pattern expression"
                    required
                  />
                  <div className="button-group">
                    <button type="button" onClick={() => setShowPatternModal(false)}>Cancel</button>
                    <button type="submit">Save</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Similar modals for edit pattern, delete pattern, etc. */}
        </>
      )}
    </div>
  );
}

