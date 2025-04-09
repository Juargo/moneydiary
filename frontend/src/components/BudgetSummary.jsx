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

  // Calculate aggregate data for the overall budget visualization
  const aggregateData = useMemo(() => {
    if (!budgetSummary || budgetSummary.length === 0) return { totalSpent: 0, budgets: [], totalLimit: 2000000, totalBudgetAmount: 0 };
    
    const totalLimit = 2000000; // Fixed limit of 2,000,000 CLP
    let totalSpent = 0;
    let totalBudgetAmount = 0;
    
    // Filter out the "Ingresos" budget and prepare budget data
    const budgets = budgetSummary
      .filter(budget => budget.name.toLowerCase() !== 'ingresos')
      .map(budget => {
        // Calculate the total budget amount from subcategories
        let budgetTotal = 0;
        let totalBudgetSpent = 0;
        
        // Sum up all subcategory budget amounts and actual spending
        budget.categories.forEach(category => {
          category.subcategories.forEach(subcategory => {
            budgetTotal += (subcategory.subcategory_budget_amount || 0);
            totalBudgetSpent += Math.abs(subcategory.total || 0);
          });
        });
        
        totalSpent += totalBudgetSpent;
        totalBudgetAmount += budgetTotal; // Add to the overall budget amount
        
        return {
          id: budget.id,
          name: budget.name,
          total: totalBudgetSpent, // Use the sum of all subcategory totals
          budget_amount: budgetTotal, // Use the sum of all subcategory budget amounts
          color: getBudgetColor(budget.id)
        };
      });
    
    return { totalSpent, budgets, totalLimit, totalBudgetAmount };
  }, [budgetSummary]);

  // Helper function to get a color for each budget
  function getBudgetColor(budgetId) {
    // Array of distinct colors for budgets - using more vibrant colors
    const colors = [
      'bg-blue-500', 'bg-green-500', 'bg-yellow-400', 'bg-red-500', 
      'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500',
      'bg-teal-500', 'bg-lime-500', 'bg-cyan-500', 'bg-rose-500'
    ];
    
    // Use the budgetId to deterministically select a color
    return colors[budgetId % colors.length];
  }

  // Format currency values
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(value);
  };

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
        {/* Overall Budget Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-md font-bold">Distribución General de Presupuestos</h3>
            <span className="text-sm font-semibold">
              {formatCurrency(aggregateData.totalBudgetAmount)} / {formatCurrency(aggregateData.totalLimit)}
              {' '}({Math.round((aggregateData.totalBudgetAmount / aggregateData.totalLimit) * 100)}% del límite)
              <span className="text-xs text-gray-500 ml-2">(Excluye Ingresos)</span>
            </span>
          </div>
          
          <div className="relative">
            {/* Main progress bar background */}
            <div className="h-8 bg-gray-200 rounded-lg overflow-hidden">
              {/* Stacked budget segments */}
              <div className="h-full flex">
                {aggregateData.budgets.map((budget, index) => {
                  // Calculate the width as percentage of the total limit based on budget_amount
                  const widthPercent = (budget.budget_amount / aggregateData.totalLimit) * 100;
                  const color = budget.color;
                  
                  // Calculate spending percentage relative to this budget's allocation
                  const spendingPercent = budget.budget_amount > 0 
                    ? Math.min(100, (budget.total / budget.budget_amount) * 100) 
                    : 0;
                  
                  // Get the corresponding darker color class by extracting the color base
                  const colorBase = color.replace('bg-', '').split('-')[0]; // Extract base color name
                  const darkerColorClass = `bg-${colorBase}-600`; // Use darker shade
                  
                  return (
                    <div
                      key={budget.id}
                      className={`h-full ${color} relative group flex items-center justify-center`}
                      style={{ 
                        width: `${Math.min(widthPercent, 100)}%`,
                        minWidth: widthPercent > 0 ? '1%' : '0' // Ensure small segments are still visible
                      }}
                    >
                      {/* Amount text inside the bar - show the budget_amount */}
                      {widthPercent > 5 && (
                        <span className="text-xs text-white font-medium z-10 truncate px-1 drop-shadow-md">
                          {formatCurrency(budget.budget_amount)}
                        </span>
                      )}
                      
                      {/* Spending indicator inside the bar - using same color family but darker */}
                      <div 
                        className={`absolute left-0 top-0 h-2 ${darkerColorClass} bg-opacity-70 z-5`}
                        style={{ width: `${spendingPercent}%` }}
                      ></div>
                      
                      {/* Tooltip on hover - show both the budget amount and actual spending */}
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-800 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-20">
                        <div>{budget.name}:</div>
                        <div>Presupuesto: {formatCurrency(budget.budget_amount)}</div>
                        <div>Gastado: {formatCurrency(budget.total)} ({Math.round(spendingPercent)}%)</div>
                        <div>({Math.round((budget.budget_amount / aggregateData.totalLimit) * 100)}% del límite)</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Limit marker */}
            <div className="absolute top-0 right-0 bottom-0 flex items-center">
              <div className="h-full w-0.5 bg-black"></div>
              <span className="text-xs font-semibold ml-1 bg-white px-1 rounded">Límite</span>
            </div>
          </div>
          
          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-2">
            {aggregateData.budgets.map((budget) => (
              <div key={budget.id} className="flex items-center">
                <div className={`w-4 h-4 rounded ${budget.color} mr-1 border border-gray-300`}></div>
                <span className="text-xs">
                  {budget.name} ({Math.round((budget.budget_amount / aggregateData.totalLimit) * 100)}% - {Math.round(budget.total / budget.budget_amount * 100)}% usado)
                </span>
              </div>
            ))}
          </div>
        </div>
        
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
                  
                  {/* Progress bar for budget - hide for "Ingresos" budget */}
                  {budget.budget_amount > 0 && budget.name.toLowerCase() !== 'ingresos' && (
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
                        
                        {/* Progress bar for category - hide for "Ingresos" budget */}
                        {category.category_budget_amount > 0 && budget.name.toLowerCase() !== 'ingresos' && (
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
                              
                              {/* Progress bar for subcategory - hide for "Ingresos" budget */}
                              {subcategory.subcategory_budget_amount > 0 && budget.name.toLowerCase() !== 'ingresos' && (
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
