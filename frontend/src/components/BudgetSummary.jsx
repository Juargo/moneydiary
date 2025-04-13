import React, { useState, useMemo } from 'react';

const BudgetSummary = ({ budgetSummary, budgetConfig = [], totalAvailableBalance = 0 }) => {
  const [expandedItems, setExpandedItems] = useState({});

  // Format currency values
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(value);
  };

  // Create a lookup map from budgetConfig for quick access
  const configLookup = useMemo(() => {
    const lookup = {
      subcategories: {},
      categories: {},
      budgets: {}
    };
    
    if (budgetConfig && budgetConfig.length > 0) {
      // For each config item, populate all lookup maps
      budgetConfig.forEach(item => {
        // Budget lookup
        if (item.budgetId && !lookup.budgets[item.budgetId]) {
          lookup.budgets[item.budgetId] = {
            name: item.budgetName
          };
        }
        
        // Category lookup
        if (item.categoryId && !lookup.categories[item.categoryId]) {
          lookup.categories[item.categoryId] = {
            name: item.categoryName,
            budgetId: item.budgetId,
            budgetName: item.budgetName
          };
        }
        
        // Subcategory lookup
        if (item.subcategoryId) {
          if (!lookup.subcategories[item.subcategoryId]) {
            lookup.subcategories[item.subcategoryId] = {
              budgetAmount: item.subcategoryBudgetAmount || 0,
              budgetId: item.budgetId,
              budgetName: item.budgetName,
              categoryId: item.categoryId,
              categoryName: item.categoryName,
              subcategoryName: item.subcategoryName
            };
          }
        }
      });
    }
    
    return lookup;
  }, [budgetConfig]);

  // Transform budgetConfig into hierarchical structure and identify missing items
  const { organizedConfig, completeData } = useMemo(() => {
    // Create hierarchical organization of config data
    const configMap = {
      budgets: {}
    };
    
    // Copy budgetSummary to avoid modifying original
    const mergedData = JSON.parse(JSON.stringify(budgetSummary || []));
    
    // Create lookup maps for easy access
    const budgetLookup = {};
    mergedData.forEach(budget => {
      budgetLookup[budget.id] = budget;
      
      // Create category lookup within each budget
      const categoryLookup = {};
      budget.categories.forEach(category => {
        categoryLookup[category.id] = category;
        
        // Create subcategory lookup within each category
        const subcategoryLookup = {};
        category.subcategories.forEach(subcategory => {
          subcategoryLookup[subcategory.id] = subcategory;
        });
        
        category.subcategoryLookup = subcategoryLookup;
      });
      
      budget.categoryLookup = categoryLookup;
    });
    
    // Process budgetConfig to add missing items
    if (budgetConfig && budgetConfig.length > 0) {
      budgetConfig.forEach(item => {
        // Ensure budget exists
        if (!configMap.budgets[item.budgetId]) {
          configMap.budgets[item.budgetId] = {
            id: item.budgetId,
            name: item.budgetName,
            categories: {}
          };
        }
        
        // Ensure category exists
        const budget = configMap.budgets[item.budgetId];
        if (!budget.categories[item.categoryId]) {
          budget.categories[item.categoryId] = {
            id: item.categoryId,
            name: item.categoryName,
            subcategories: {}
          };
        }
        
        // Ensure subcategory exists with budget amount
        const category = budget.categories[item.categoryId];
        if (!category.subcategories[item.subcategoryId]) {
          category.subcategories[item.subcategoryId] = {
            id: item.subcategoryId,
            name: item.subcategoryName,
            budgetAmount: item.subcategoryBudgetAmount || 0,
            patterns: []
          };
        }
        
        // Add pattern if it exists
        if (item.patternId && item.patternText) {
          const subcategory = category.subcategories[item.subcategoryId];
          const patternExists = subcategory.patterns.some(p => p.id === item.patternId);
          
          if (!patternExists) {
            subcategory.patterns.push({
              id: item.patternId,
              text: item.patternText
            });
          }
        }
        
        // Now add missing items to the merged data
        
        // Check if budget exists in data, if not add it
        let budgetInData = budgetLookup[item.budgetId];
        if (!budgetInData) {
          budgetInData = {
            id: item.budgetId,
            name: item.budgetName,
            total: 0,
            formattedTotal: formatCurrency(0),
            categories: [],
            categoryLookup: {}
          };
          mergedData.push(budgetInData);
          budgetLookup[item.budgetId] = budgetInData;
        }
        
        // Check if category exists in budget, if not add it
        let categoryInData = budgetInData.categoryLookup[item.categoryId];
        if (!categoryInData) {
          categoryInData = {
            id: item.categoryId,
            name: item.categoryName,
            total: 0,
            formattedTotal: formatCurrency(0),
            subcategories: [],
            subcategoryLookup: {}
          };
          budgetInData.categories.push(categoryInData);
          budgetInData.categoryLookup[item.categoryId] = categoryInData;
        }
        
        // Check if subcategory exists in category, if not add it
        let subcategoryInData = categoryInData.subcategoryLookup[item.subcategoryId];
        if (!subcategoryInData) {
          subcategoryInData = {
            id: item.subcategoryId,
            name: item.subcategoryName,
            subcategory_budget_amount: item.subcategoryBudgetAmount || 0,
            total: 0,
            formattedTotal: formatCurrency(0),
            patterns: []
          };
          categoryInData.subcategories.push(subcategoryInData);
          categoryInData.subcategoryLookup[item.subcategoryId] = subcategoryInData;
          
          // Update category budget amount
          if (!categoryInData.category_budget_amount) {
            categoryInData.category_budget_amount = 0;
          }
          categoryInData.category_budget_amount += (item.subcategoryBudgetAmount || 0);
          
          // Update budget amount
          if (!budgetInData.budget_amount) {
            budgetInData.budget_amount = 0;
          }
          budgetInData.budget_amount += (item.subcategoryBudgetAmount || 0);
        }
        
        // Add pattern if needed
        if (item.patternId && item.patternText) {
          const patternExists = subcategoryInData.patterns.some(p => p.id === item.patternId);
          
          if (!patternExists) {
            subcategoryInData.patterns.push({
              id: item.patternId,
              text: item.patternText,
              total: 0,
              transaction_count: 0,
              formattedTotal: formatCurrency(0)
            });
          }
        }
      });
    }
    
    return {
      organizedConfig: configMap,
      completeData: mergedData
    };
  }, [budgetSummary, budgetConfig]);

  // Sort all data by amount (total) in descending order
  const sortedBudgetData = useMemo(() => {
    // Sort budgets by total (highest to lowest)
    const sortedData = [...completeData].sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
    
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
  }, [completeData]);

  // Calculate aggregate data for the overall budget visualization
  const aggregateData = useMemo(() => {
    if (!budgetSummary || budgetSummary.length === 0) return { totalSpent: 0, budgets: [], totalLimit: 0, totalBudgetAmount: 0 };
    
    // Find the "Ingresos" budget to use as the monthly limit
    const ingresosBudget = budgetSummary.find(budget => budget.name.toLowerCase() === 'ingresos');
    // Use the income total as the limit, or default to 0 if not found
    const totalLimit = ingresosBudget ? Math.abs(ingresosBudget.total || 0) : 0;
    
    let totalSpent = 0;
    
    // Filter out the "Ingresos" budget and prepare budget data
    const budgets = budgetSummary
      .filter(budget => budget.name.toLowerCase() !== 'ingresos')
      .map(budget => {
        // Use the budget_amount directly from the API response
        const budgetTotal = budget.budget_amount || 0;
        let totalBudgetSpent = Math.abs(budget.total || 0);
        
        totalSpent += totalBudgetSpent;
        
        return {
          id: budget.id,
          name: budget.name,
          total: totalBudgetSpent,
          budget_amount: budgetTotal, // Use the budget_amount field directly
          color: getBudgetColor(budget.id)
        };
      });
    
    // Calculate total budget amount by summing all budget amounts
    const totalBudgetAmount = budgets.reduce((sum, budget) => sum + budget.budget_amount, 0);
    
    // Calculate the difference between total limit and budget amount
    const difference = totalLimit - totalBudgetAmount;
    const hasSavings = difference >= 0;
    
    return { 
      totalSpent, 
      budgets, 
      totalLimit, 
      totalBudgetAmount,
      difference,
      hasSavings
    };
  }, [sortedBudgetData]);

  // Helper function to get a color for each budget
  function getBudgetColor(budgetId) {
    // Array of distinct pastel colors for budgets
    const colors = [
      'bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-red-400', 
      'bg-purple-400', 'bg-pink-400', 'bg-indigo-400', 'bg-orange-400',
      'bg-teal-400', 'bg-lime-400', 'bg-cyan-400', 'bg-rose-400'
    ];
    
    // Use the budgetId to deterministically select a color
    return colors[budgetId % colors.length];
  }

  const toggleAccordion = (type, id) => {
    setExpandedItems(prev => ({
      ...prev,
      [`${type}-${id}`]: !prev[`${type}-${id}`]
    }));
  };

  const isExpanded = (type, id) => {
    return !!expandedItems[`${type}-${id}`];
  };

  // Function to check if a subcategory should show a progress bar
  const getSubcategoryProgressBar = (subcategory, budget) => {
    if (!subcategory) return { show: false, amount: 0 };
    
    // If subcategory has a budget amount in the data, use it
    if (subcategory.subcategory_budget_amount > 0 && budget.name.toLowerCase() !== 'ingresos') {
      return {
        show: true,
        amount: subcategory.subcategory_budget_amount
      };
    }
    
    // Check if it has a budget amount in the config
    const configInfo = configLookup.subcategories[subcategory.id];
    if (configInfo && configInfo.budgetAmount > 0 && budget.name.toLowerCase() !== 'ingresos') {
      return {
        show: true,
        amount: configInfo.budgetAmount
      };
    }
    
    return { show: false, amount: 0 };
  };

  // Function to check if a category should show a progress bar
  const getCategoryProgressBar = (category, budget) => {
    if (!category) return { show: false, amount: 0 };
    
    // If category has a budget amount in the data, use it
    if (category.category_budget_amount > 0 && budget.name.toLowerCase() !== 'ingresos') {
      return {
        show: true,
        amount: category.category_budget_amount
      };
    }
    
    // Sum up the budget amounts from all subcategories in configLookup
    let totalBudgetAmount = 0;
    let foundBudgetAmount = false;
    
    // Look through all subcategories in the configuration
    Object.values(configLookup.subcategories).forEach(subConfig => {
      if (subConfig.categoryId === category.id && subConfig.budgetAmount > 0) {
        totalBudgetAmount += subConfig.budgetAmount;
        foundBudgetAmount = true;
      }
    });
    
    if (foundBudgetAmount && budget.name.toLowerCase() !== 'ingresos') {
      return {
        show: true,
        amount: totalBudgetAmount
      };
    }
    
    return { show: false, amount: 0 };
  };

  return (
    <div className="bg-white rounded-lg shadow" id="budget-summary-container">
      <div className="p-6">
        {/* Display total available balance if provided */}
        {/* {totalAvailableBalance !== undefined && (
          <div className={`mb-4 p-3 rounded-lg border border-gray-300 
                          ${totalAvailableBalance >= 0 ? 'bg-blue-50' : 'bg-yellow-50'}`}>
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-700">Dinero Disponible Actualmente:</span>
                <p className="text-sm text-gray-600 mt-1">
                  Este es el balance total de todas tus cuentas bancarias registradas.
                </p>
              </div>
              <div className={`text-xl font-bold ${totalAvailableBalance >= 0 ? 'text-blue-600' : 'text-yellow-600'}`}>
                {formatCurrency(totalAvailableBalance)}
              </div>
            </div>
          </div>
        )} */}
        
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
          
          {/* Enhanced and Fixed Savings/Deficit indicator */}
          <div 
            className={`mb-4 p-4 rounded-lg border-2 ${aggregateData.hasSavings ? 'bg-green-100 border-green-300' : 'bg-red-100 border-red-400'}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <i className={`fas ${aggregateData.hasSavings ? 'fa-piggy-bank text-green-600' : 'fa-exclamation-triangle text-red-600'} text-xl mr-3`}></i>
                <span className="font-bold text-lg">
                  {aggregateData.hasSavings ? 'Ahorro Potencial:' : 'Déficit Presupuestario:'}
                </span>
              </div>
              <span className={`font-bold text-xl ${aggregateData.hasSavings ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(Math.abs(aggregateData.difference))}
              </span>
            </div>
            
            <div className="mt-3 text-sm">
              <p className={`${aggregateData.hasSavings ? 'text-green-700' : 'text-red-700'} font-medium`}>
                {aggregateData.hasSavings 
                  ? `Tienes un excedente de ${formatCurrency(aggregateData.difference)} que podrías destinar al ahorro.`
                  : `Te estás excediendo del límite mensual de ${formatCurrency(aggregateData.totalLimit)} por ${formatCurrency(Math.abs(aggregateData.difference))}.`
                }
              </p>
            </div>
            
            {/* Always show the breakdown for clarity */}
            <div className="mt-3 flex flex-col bg-white rounded p-2 border border-gray-200">
              <div className="flex justify-between text-sm font-medium">
                <span>Límite total:</span>
                <span className="font-bold">{formatCurrency(aggregateData.totalLimit)}</span>
              </div>
              <div className="flex justify-between text-sm font-medium mt-1 pt-1 border-t border-gray-100">
                <span>Total presupuestado:</span>
                <span className="font-bold">{formatCurrency(aggregateData.totalBudgetAmount)}</span>
              </div>
              <div className={`flex justify-between text-sm font-bold mt-1 pt-1 border-t ${aggregateData.hasSavings ? 'border-green-200' : 'border-red-200'}`}>
                <span>{aggregateData.hasSavings ? 'Ahorro:' : 'Exceso:'}</span>
                <span className={aggregateData.hasSavings ? 'text-green-600' : 'text-red-600'}>
                  {aggregateData.hasSavings ? '+' : '-'}{formatCurrency(Math.abs(aggregateData.difference))}
                </span>
              </div>
            </div>
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
                  // const darkerColorClass = `bg-${colorBase}-500`; // Use shade 500 instead of 600
                  const darkerColorClass = `bg-[#00000054]`; // Use shade 500 instead of 600
                  
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
          <div className="space-y-2 font-mono" id="container-resumen">
            {sortedBudgetData.map((budget) => (
              <div key={budget.id} className="border-l-2 border-gray-200 pl-2">
              {/* <pre className='text-xs'>
                {JSON.stringify(budget, null, 2)}
              </pre>
     */}
                {/* Budget (Root folder) */}
                <div className="py-1 hover:bg-gray-50">
                  <div 
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleAccordion('budget', budget.id)}
                  >
                    <div className="flex items-center gap-2">
                      <i className={`${isExpanded('budget', budget.id) ? 'fas fa-folder-open text-yellow-500' : 'fas fa-folder text-yellow-400'} mr-2`}></i>
                      <span className="font-semibold text-gray-700 text-sm w-36 truncate">{budget.name}</span>
                      
                      {/* Progress bar for budget - hide for "Ingresos" budget */}
                      {budget.budget_amount > 0 && budget.name.toLowerCase() !== 'ingresos' ? (
                        <div className="w-48 relative">
                          <div className="relative h-4 flex overflow-hidden rounded bg-gray-200 w-full">
                            {/* Progress bar showing percentage of usage */}
                            <div 
                              style={{ 
                                width: `${Math.min(100, (Math.abs(budget.total) / budget.budget_amount) * 100)}%` 
                              }} 
                              className={`
                                flex flex-col text-center whitespace-nowrap 
                                text-white justify-center
                                ${Math.abs(budget.total) > budget.budget_amount ? 'bg-red-500' : 'bg-yellow-500'}
                              `}
                            >
                              <span className="text-xs px-1 truncate">
                                {Math.round((Math.abs(budget.total) / budget.budget_amount) * 100)}%
                              </span>
                            </div>
                          </div>
                          
                          {/* Amount information below the progress bar */}
                          <div className="flex justify-between text-xs mt-0.5 text-gray-600">
                            <span>{formatCurrency(Math.abs(budget.total))}</span>
                            <span>{formatCurrency(budget.budget_amount)}</span>
                          </div>
                        </div>
                      ) : (
                        // Empty placeholder to maintain alignment when no progress bar
                        <div className="w-48"></div>
                      )}
                    </div>
                    <div className={`font-semibold text-sm ${budget.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {formatCurrency(budget.total)}
                    </div>
                  </div>
                </div>
                
                {/* Budget Content (Categories) */}
                <div className={`pl-6 ${isExpanded('budget', budget.id) ? 'block' : 'hidden'}`}>
                  {budget.categories.map((category) => {
                    // Check if this category should show a progress bar
                    const categoryProgressBar = getCategoryProgressBar(category, budget);
                    
                    return (
                      <div key={category.id} className="border-l-2 border-gray-200 pl-2 mt-1">
                        {/* Category (Subfolder) */}
                        <div className="py-1 hover:bg-gray-50">
                          <div 
                            className="flex items-center justify-between cursor-pointer"
                            onClick={() => toggleAccordion('category', category.id)}
                          >
                            <div className="flex items-center gap-2">
                              <i className={`${isExpanded('category', category.id) ? 'fas fa-folder-open text-blue-400' : 'fas fa-folder text-blue-300'} mr-2`}></i>
                              <span className="w-36 truncate text-xs font-semibold text-gray-700">{category.name}</span>
                              
                              {/* Progress bar for category - now showing for those with budgetConfig entries too */}
                              {categoryProgressBar.show ? (
                                <div className="w-48 relative">
                                  <div className="relative h-4 flex overflow-hidden rounded bg-gray-200 w-full">
                                    {/* Progress bar showing percentage of usage */}
                                    <div 
                                      style={{ 
                                        width: `${Math.min(100, (Math.abs(category.total || 0) / categoryProgressBar.amount) * 100)}%` 
                                      }} 
                                      className={`
                                        flex flex-col text-center whitespace-nowrap 
                                        text-white justify-center
                                        ${Math.abs(category.total || 0) > categoryProgressBar.amount ? 'bg-red-500' : 'bg-blue-500'}
                                      `}
                                    >
                                      <span className="text-xs px-1 truncate">
                                        {Math.round((Math.abs(category.total || 0) / categoryProgressBar.amount) * 100)}%
                                      </span>
                                    </div>
                                  </div>
                                  
                                  {/* Amount information below the progress bar */}
                                  <div className="flex justify-between text-xs mt-0.5 text-gray-600">
                                    <span>{formatCurrency(Math.abs(category.total || 0))}</span>
                                    <span>{formatCurrency(categoryProgressBar.amount)}</span>
                                  </div>
                                </div>
                              ) : (
                                // Empty placeholder to maintain alignment when no progress bar
                                <div className="w-48"></div>
                              )}
                            </div>
                            <div className={`font-semibold ${category.total < 0 ? 'text-red-600' : 'text-green-600'} text-sm`}>
                              {formatCurrency(category.total || 0)}
                            </div>
                          </div>
                        </div>

                        {/* Category Content (Subcategories) */}
                        <div className={`pl-6 ${isExpanded('category', category.id) ? 'block' : 'hidden'}`}>
                          {category.subcategories.map((subcategory) => {
                            // Check if this subcategory should show a progress bar
                            const subcategoryProgressBar = getSubcategoryProgressBar(subcategory, budget);
                            
                            return (
                              <div key={subcategory.id} className="border-l-2 border-gray-200 pl-2 mt-1">
                                {/* Subcategory (Nested subfolder) */}
                                <div className="py-1 hover:bg-gray-50">
                                  <div 
                                    className="flex items-center justify-between cursor-pointer"
                                    onClick={() => toggleAccordion('subcategory', subcategory.id)}
                                  >
                                    <div className="flex items-center gap-2">
                                      <i className={`${isExpanded('subcategory', subcategory.id) ? 'fas fa-folder-open text-green-400' : 'fas fa-folder text-green-300'} mr-2`}></i>
                                      <span className="w-36 truncate text-xs font-semibold text-gray-700">{subcategory.name}</span>
                                      
                                      {/* Progress bar for subcategory */}
                                      {subcategoryProgressBar.show ? (
                                        <div className="w-48 relative">
                                          <div className="relative h-4 flex overflow-hidden rounded bg-gray-200 w-full">
                                            {/* Progress bar showing percentage of usage */}
                                            <div 
                                              style={{ 
                                                width: `${Math.min(100, (Math.abs(subcategory.total || 0) / subcategoryProgressBar.amount) * 100)}%` 
                                              }} 
                                              className={`
                                                flex flex-col text-center whitespace-nowrap 
                                                text-white justify-center
                                                ${Math.abs(subcategory.total || 0) > subcategoryProgressBar.amount ? 'bg-red-500' : 'bg-green-500'}
                                              `}
                                            >
                                              <span className="text-xs px-1 truncate">
                                                {Math.round((Math.abs(subcategory.total || 0) / subcategoryProgressBar.amount) * 100)}%
                                              </span>
                                            </div>
                                          </div>
                                          
                                          {/* Amount information below the progress bar */}
                                          <div className="flex justify-between text-xs mt-0.5 text-gray-600">
                                            <span>{formatCurrency(Math.abs(subcategory.total || 0))}</span>
                                            <span>{formatCurrency(subcategoryProgressBar.amount)}</span>
                                          </div>
                                        </div>
                                      ) : (
                                        // Empty placeholder to maintain alignment when no progress bar
                                        <div className="w-48"></div>
                                      )}
                                    </div>
                                    <div className={`font-semibold ${subcategory.total < 0 ? 'text-red-600' : 'text-green-600'} text-sm`}>
                                      {formatCurrency(subcategory.total || 0)}
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Subcategory Content (Patterns as files) */}
                                <div className={`pl-6 ${isExpanded('subcategory', subcategory.id) ? 'block' : 'hidden'}`}>
                                  {subcategory.patterns.map((pattern) => (
                                    <div key={pattern.id} className="flex items-center justify-between py-1 hover:bg-gray-50">
                                      <div className="flex items-center">
                                        <i className="fas fa-file-alt text-gray-400 mr-2"></i>
                                        <span className="text-xs">{pattern.text}</span>
                                      </div>
                                      <div className="flex items-center">
                                        <span className="text-xs text-gray-500 mr-3">{pattern.transaction_count} transacciones</span>
                                        <span className={`text-sm font-medium ${pattern.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                          {pattern.formattedTotal}
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                  
                                  {/* Show message when no patterns exist */}
                                  {subcategory.patterns.length === 0 && (
                                    <div className="py-1 text-xs text-gray-500 italic">
                                      No hay patrones definidos para esta subcategoría
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
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
