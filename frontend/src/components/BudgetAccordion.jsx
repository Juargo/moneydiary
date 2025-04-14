import React, { useState } from 'react';

export default function BudgetAccordion({ 
  budgetData, 
  onAddPattern, 
  onEditPattern, 
  onDeletePattern,
  onAddSubcategory,
  onEditSubcategory,
  onDeleteSubcategory
}) {
  // State to track open accordions
  const [openBudgets, setOpenBudgets] = useState(new Set([0])); // Default: first budget open
  const [openCategories, setOpenCategories] = useState(new Set());
  const [openSubcategories, setOpenSubcategories] = useState(new Set());

  // Toggle functions
  const toggleBudget = (index) => {
    const newOpenBudgets = new Set(openBudgets);
    if (newOpenBudgets.has(index)) {
      newOpenBudgets.delete(index);
    } else {
      newOpenBudgets.add(index);
    }
    setOpenBudgets(newOpenBudgets);
  };

  const toggleCategory = (budgetIndex, categoryIndex) => {
    const key = `${budgetIndex}-${categoryIndex}`;
    const newOpenCategories = new Set(openCategories);
    if (newOpenCategories.has(key)) {
      newOpenCategories.delete(key);
    } else {
      newOpenCategories.add(key);
    }
    setOpenCategories(newOpenCategories);
  };

  const toggleSubcategory = (budgetIndex, categoryIndex, subcategoryIndex) => {
    const key = `${budgetIndex}-${categoryIndex}-${subcategoryIndex}`;
    const newOpenSubcategories = new Set(openSubcategories);
    if (newOpenSubcategories.has(key)) {
      newOpenSubcategories.delete(key);
    } else {
      newOpenSubcategories.add(key);
    }
    setOpenSubcategories(newOpenSubcategories);
  };

  return (
    <div className="space-y-4 mb-6">
      {budgetData.map((budget, budgetIndex) => (
        <div key={budget.id} className="bg-white rounded-lg shadow overflow-hidden">
          {/* Budget Level */}
          <div 
            className="flex justify-between items-center p-5 cursor-pointer bg-gray-50 hover:bg-gray-100"
            onClick={() => toggleBudget(budgetIndex)}
          >
            <div className="flex items-center gap-2">
              <i className="fas fa-wallet text-primary-600"></i>
              <h3 className="text-lg font-semibold">{budget.name}</h3>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500 hidden md:inline">{budget.description}</span>
              <i className={`fas fa-chevron-down transform transition-transform ${openBudgets.has(budgetIndex) ? 'rotate-180' : ''}`}></i>
            </div>
          </div>
          
          {/* Categories Level - shown if budget is open */}
          {openBudgets.has(budgetIndex) && (
            <div className="p-5 space-y-3">
              {budget.categories && budget.categories.map((category, categoryIndex) => (
                <div key={category.id} className="border border-gray-200 rounded-lg">
                  <div 
                    className="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleCategory(budgetIndex, categoryIndex)}
                  >
                    <div className="flex flex-col">
                      <h4 className="font-medium">{category.name}</h4>
                      <p className="text-sm text-gray-500">{category.description}</p>
                    </div>
                    <i className={`fas fa-chevron-down transform transition-transform ${openCategories.has(`${budgetIndex}-${categoryIndex}`) ? 'rotate-180' : ''}`}></i>
                  </div>
                  
                  {/* Subcategories Level - shown if category is open */}
                  {openCategories.has(`${budgetIndex}-${categoryIndex}`) && (
                    <div className="p-4 pt-2 border-t border-gray-100">
                      {category.subcategories && category.subcategories.map((subcategory, subcategoryIndex) => (
                        <div key={subcategory.id} className="ml-4 border-l-2 border-gray-200 pl-4 mb-2">
                          <div 
                            className="flex justify-between items-center py-2 cursor-pointer"
                            onClick={() => toggleSubcategory(budgetIndex, categoryIndex, subcategoryIndex)}
                          >
                            <h5 className="font-medium">{subcategory.name}</h5>
                            <div className="flex items-center gap-2">
                              <button 
                                className="text-primary-600 hover:text-primary-800 text-xs"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onEditSubcategory(subcategory);
                                }}
                              >
                                <i className="fas fa-edit"></i>
                              </button>
                              <button 
                                className="text-red-600 hover:text-red-800 text-xs"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onDeleteSubcategory(subcategory);
                                }}
                              >
                                <i className="fas fa-trash"></i>
                              </button>
                              <i className={`fas fa-chevron-down transform transition-transform ${openSubcategories.has(`${budgetIndex}-${categoryIndex}-${subcategoryIndex}`) ? 'rotate-180' : ''}`}></i>
                            </div>
                          </div>
                          
                          {/* Patterns Level - shown if subcategory is open */}
                          {openSubcategories.has(`${budgetIndex}-${categoryIndex}-${subcategoryIndex}`) && (
                            <div className="pl-4 py-2">
                              <div className="flex justify-between items-center mb-2">
                                <h6 className="text-xs uppercase text-gray-500">Patrones de transacciones</h6>
                                <button 
                                  className="text-xs text-primary-600 hover:text-primary-800"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    onAddPattern(subcategory.id, subcategory.name);
                                  }}
                                >
                                  <i className="fas fa-plus mr-1"></i> Añadir Patrón
                                </button>
                              </div>
                              
                              {subcategory.patterns && subcategory.patterns.length > 0 ? (
                                <ul className="space-y-1">
                                  {subcategory.patterns.map((pattern) => (
                                    <li key={pattern.id} className="text-sm py-1 px-2 bg-gray-50 rounded flex justify-between items-center">
                                      <span>{pattern.expName}</span>
                                      <div className="flex gap-2">
                                        <button 
                                          className="text-primary-600 hover:text-primary-800 text-xs"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            onEditPattern(pattern, subcategory.id);
                                          }}
                                        >
                                          <i className="fas fa-edit"></i>
                                        </button>
                                        <button 
                                          className="text-red-600 hover:text-red-800 text-xs"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            onDeletePattern(pattern);
                                          }}
                                        >
                                          <i className="fas fa-trash"></i>
                                        </button>
                                      </div>
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-sm text-gray-500 py-2">No hay patrones definidos</p>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                      
                      <div className="flex justify-end mt-2 pt-2 border-t border-gray-100">
                        <button 
                          className="text-primary-600 hover:text-primary-800 text-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onAddSubcategory(category.id);
                          }}
                        >
                          <i className="fas fa-plus mr-1"></i> Añadir Subcategoría
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              <div className="flex justify-end mt-4">
                <button className="text-primary-600 hover:text-primary-800 text-sm">
                  <i className="fas fa-plus mr-1"></i> Añadir Categoría
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
