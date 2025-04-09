import React, { useState, useMemo } from 'react';

const BudgetSummary = ({ budgetSummary }) => {
  const [expandedItems, setExpandedItems] = useState({});

  // Sort all data by amount (total) in descending order
  const sortedBudgetData = useMemo(() => {
    // Create a deep copy to avoid modifying the original data
    const sortedData = [...(budgetSummary || [])];
    
    // Sort budgets by total (highest to lowest)
    sortedData.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
    
    // Sort categories within each budget
    sortedData.forEach(budget => {
      budget.categories.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
      
      // Sort subcategories within each category
      budget.categories.forEach(category => {
        category.subcategories.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
        
        // Sort patterns within each subcategory
        category.subcategories.forEach(subcategory => {
          subcategory.patterns.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
        });
      });
    });
    
    return sortedData;
  }, [budgetSummary]);

  const toggleAccordion = (type, id) => {
    setExpandedItems(prev => ({
      ...prev,
      [`${type}-${id}`]: !prev[`${type}-${id}`]
    }));
  };

  const isExpanded = (type, id) => {
    return !!expandedItems[`${type}-${id}`];
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Resumen de Presupuestos</h2>
        
        {sortedBudgetData.length > 0 ? (
          <div className="space-y-2 font-mono">
            {sortedBudgetData.map((budget) => (
              <div key={budget.id} className="border-l-2 border-gray-200 pl-2">
                {/* Budget (Root folder) */}
                <div className="py-1 hover:bg-gray-50">
                  <div 
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleAccordion('budget', budget.id)}
                  >
                    <div className="flex items-center">
                      <i className={`${isExpanded('budget', budget.id) ? 'fas fa-folder-open text-yellow-500' : 'fas fa-folder text-yellow-400'} mr-2`}></i>
                      <span className="font-medium">{budget.name}</span>
                    </div>
                    <div className={`font-semibold ${budget.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {budget.formattedTotal}
                    </div>
                  </div>
                  
                  {/* Progress bar for budget */}
                  {budget.budget_amount > 0 && (
                    <div className="mt-1 relative pt-1">
                      <div className="flex mb-2 items-center justify-between">
                        <div>
                          <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-yellow-600 bg-yellow-200">
                            Presupuesto Total
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-semibold inline-block text-yellow-600">
                            {Math.round(Math.abs(budget.total) / budget.budget_amount * 100)}%
                          </span>
                        </div>
                      </div>
                      <div className="relative h-4 flex overflow-hidden rounded bg-gray-200">
                        {/* Budget limit line */}
                        <div 
                          className="absolute h-full w-1 bg-black z-10"
                          style={{
                            left: `${Math.min(100, (budget.budget_amount / Math.max(Math.abs(budget.total), budget.budget_amount)) * 100)}%`
                          }}
                        ></div>
                        
                        {/* Progress bar */}
                        <div 
                          style={{ 
                            width: `${Math.min(100, (Math.abs(budget.total) / Math.max(Math.abs(budget.total), budget.budget_amount)) * 100)}%` 
                          }} 
                          className={`
                            flex flex-col text-center whitespace-nowrap 
                            text-white justify-center
                            ${Math.abs(budget.total) > budget.budget_amount ? 'bg-red-500' : 'bg-yellow-500'}
                          `}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Budget Content (Categories) */}
                <div className={`pl-6 ${isExpanded('budget', budget.id) ? 'block' : 'hidden'}`}>
                  {budget.categories.map((category) => (
                    <div key={category.id} className="border-l-2 border-gray-200 pl-2 mt-1">
                      {/* Category (Subfolder) */}
                      <div className="py-1 hover:bg-gray-50">
                        <div 
                          className="flex items-center justify-between cursor-pointer"
                          onClick={() => toggleAccordion('category', category.id)}
                        >
                          <div className="flex items-center">
                            <i className={`${isExpanded('category', category.id) ? 'fas fa-folder-open text-blue-400' : 'fas fa-folder text-blue-300'} mr-2`}></i>
                            <span>{category.name}</span>
                          </div>
                          <div className={`font-semibold ${category.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {category.formattedTotal}
                          </div>
                        </div>
                        
                        {/* Progress bar for category */}
                        {category.category_budget_amount > 0 && (
                          <div className="mt-1 relative pt-1">
                            <div className="flex mb-2 items-center justify-between">
                              <div>
                                <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                                  Categoría
                                </span>
                              </div>
                              <div className="text-right">
                                <span className="text-xs font-semibold inline-block text-blue-600">
                                  {Math.round(Math.abs(category.total) / category.category_budget_amount * 100)}%
                                </span>
                              </div>
                            </div>
                            <div className="relative h-4 flex overflow-hidden rounded bg-gray-200">
                              {/* Category budget limit line */}
                              <div 
                                className="absolute h-full w-1 bg-black z-10"
                                style={{
                                  left: `${Math.min(100, (category.category_budget_amount / Math.max(Math.abs(category.total), category.category_budget_amount)) * 100)}%`
                                }}
                              ></div>
                              
                              {/* Progress bar */}
                              <div 
                                style={{ 
                                  width: `${Math.min(100, (Math.abs(category.total) / Math.max(Math.abs(category.total), category.category_budget_amount)) * 100)}%` 
                                }} 
                                className={`
                                  flex flex-col text-center whitespace-nowrap 
                                  text-white justify-center
                                  ${Math.abs(category.total) > category.category_budget_amount ? 'bg-red-500' : 'bg-blue-500'}
                                `}
                              ></div>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Category Content (Subcategories) */}
                      <div className={`pl-6 ${isExpanded('category', category.id) ? 'block' : 'hidden'}`}>
                        {category.subcategories.map((subcategory) => (
                          <div key={subcategory.id} className="border-l-2 border-gray-200 pl-2 mt-1">
                            {/* Subcategory (Nested subfolder) */}
                            <div className="py-1 hover:bg-gray-50">
                              <div 
                                className="flex items-center justify-between cursor-pointer"
                                onClick={() => toggleAccordion('subcategory', subcategory.id)}
                              >
                                <div className="flex items-center">
                                  <i className={`${isExpanded('subcategory', subcategory.id) ? 'fas fa-folder-open text-green-400' : 'fas fa-folder text-green-300'} mr-2`}></i>
                                  <span>{subcategory.name}</span>
                                </div>
                                <div className={`font-semibold ${subcategory.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                  {subcategory.formattedTotal}
                                </div>
                              </div>
                              
                              {/* Progress bar for subcategory */}
                              {subcategory.subcategory_budget_amount > 0 && (
                                <div className="mt-1 relative pt-1">
                                  <div className="flex mb-2 items-center justify-between">
                                    <div>
                                      <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                                        Progreso
                                      </span>
                                    </div>
                                    <div className="text-right">
                                      <span className="text-xs font-semibold inline-block text-blue-600">
                                        {Math.round(Math.abs(subcategory.total) / subcategory.subcategory_budget_amount * 100)}%
                                      </span>
                                    </div>
                                  </div>
                                  <div className="relative h-4 flex overflow-hidden rounded bg-gray-200">
                                    {/* Budget limit line (black vertical line) */}
                                    <div 
                                      className="absolute h-full w-1 bg-black z-10"
                                      style={{
                                        left: `${Math.min(100, (subcategory.subcategory_budget_amount / Math.max(Math.abs(subcategory.total), subcategory.subcategory_budget_amount)) * 100)}%`
                                      }}
                                    ></div>
                                    
                                    {/* Progress bar */}
                                    <div 
                                      style={{ 
                                        width: `${Math.min(100, (Math.abs(subcategory.total) / Math.max(Math.abs(subcategory.total), subcategory.subcategory_budget_amount)) * 100)}%` 
                                      }} 
                                      className={`
                                        flex flex-col text-center whitespace-nowrap 
                                        text-white justify-center
                                        ${Math.abs(subcategory.total) > subcategory.subcategory_budget_amount ? 'bg-red-500' : 'bg-blue-500'}
                                      `}
                                    ></div>
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {/* Subcategory Content (Patterns as files) */}
                            <div className={`pl-6 ${isExpanded('subcategory', subcategory.id) ? 'block' : 'hidden'}`}>
                              {subcategory.patterns.map((pattern) => (
                                <div key={pattern.id} className="flex items-center justify-between py-1 hover:bg-gray-50">
                                  <div className="flex items-center">
                                    <i className="fas fa-file-alt text-gray-400 mr-2"></i>
                                    <span className="text-sm">{pattern.text}</span>
                                  </div>
                                  <div className="flex items-center">
                                    <span className="text-xs text-gray-500 mr-3">{pattern.transaction_count} transacciones</span>
                                    <span className={`text-sm font-medium ${pattern.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                      {pattern.formattedTotal}
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center p-6 text-gray-500">
            No hay datos de presupuesto disponibles. Por favor, verifica la conexión con el API.
          </div>
        )}
      </div>
    </div>
  );
};

export default BudgetSummary;
