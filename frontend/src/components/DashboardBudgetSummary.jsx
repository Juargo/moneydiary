import React, { useState, useEffect } from 'react';
import BudgetSummary from './BudgetSummary';

const DashboardBudgetSummary = ({ userId, budgetSummaryUrl, initialMonth }) => {
  const [currentMonth, setCurrentMonth] = useState(initialMonth || new Date().toISOString().substring(0, 7));
  const [budgetSummary, setBudgetSummary] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [displayPeriod, setDisplayPeriod] = useState(initialMonth || new Date().toISOString().substring(0, 7));

  // Function to format currency values
  const formatCurrency = (amount) => {
    const isNegative = amount < 0;
    const prefix = isNegative ? '-$' : '+$';
    return `${prefix}${Math.abs(amount).toLocaleString('es-ES', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    })}`;
  };

  // Fetch budget summary data
  const fetchBudgetSummary = async (yearMonth) => {
    try {
      setIsLoading(true);
      const summaryResponse = await fetch(`${budgetSummaryUrl}/api/v1/transactions/budget-summary?user_id=${userId}&year_month=${yearMonth}`);
      if (summaryResponse.ok) {
        const data = await summaryResponse.json();
        
        // Format the budget summary data
        const formattedData = data.map(budget => ({
          ...budget,
          formattedTotal: formatCurrency(budget.total),
          categories: budget.categories.map(category => ({
            ...category,
            formattedTotal: formatCurrency(category.total),
            subcategories: category.subcategories.map(subcategory => ({
              ...subcategory,
              formattedTotal: formatCurrency(subcategory.total),
              patterns: subcategory.patterns.map(pattern => ({
                ...pattern,
                formattedTotal: formatCurrency(pattern.total)
              }))
            }))
          }))
        }));
        
        setBudgetSummary(formattedData);
        
        // Update the display period if available
        if (data.length > 0 && data[0].period) {
          setDisplayPeriod(data[0].period);
        }
      } else {
        console.error('Error fetching budget summary:', await summaryResponse.text());
        setBudgetSummary([]);
      }
    } catch (error) {
      console.error('Error fetching budget summary:', error);
      setBudgetSummary([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Load data when month changes
  useEffect(() => {
    fetchBudgetSummary(currentMonth);
  }, [currentMonth]);

  // Handle month change
  const handleMonthChange = (event) => {
    const newMonth = event.target.value;
    setCurrentMonth(newMonth);
  };

  return (
    <div className="dashboard-budget-summary">
      {/* Month Filter */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="w-full md:w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">Periodo del Presupuesto</label>
            <input 
              type="month" 
              value={currentMonth} 
              onChange={handleMonthChange}
              disabled={isLoading}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
            />
          </div>
          <div className="text-sm text-gray-600">
            Mostrando datos para: <span className="font-medium">{displayPeriod}</span>
          </div>
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="relative">
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="ml-2 text-sm text-gray-600">Cargando resumen...</p>
          </div>
        </div>
      )}
      
      {/* Budget Summary */}
      <div>
        <BudgetSummary budgetSummary={budgetSummary} />
      </div>
    </div>
  );
};

export default DashboardBudgetSummary;
