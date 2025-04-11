import React, { useState, useEffect } from 'react';
import BudgetSummary from './BudgetSummary';

const DashboardBudgetSummary = ({ userId, budgetSummaryUrl, initialMonth }) => {
  const [currentMonth, setCurrentMonth] = useState(initialMonth || new Date().toISOString().substring(0, 7));
  const [budgetSummary, setBudgetSummary] = useState([]);
  const [userBanks, setUserBanks] = useState([]);
  const [totalBalance, setTotalBalance] = useState(0);
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

  // Fetch user banks data from GraphQL endpoint
  const fetchUserBanks = async () => {
    try {
      const graphqlEndpoint = `${budgetSummaryUrl}/graphql`;
      
      const query = `
       query GetUserBanks($userId: Int!) {
              userBanks(userId: $userId) {
                id
                userId
                bankId
                balance
                description
                createdAt
                updatedAt
              }
            }
      `;

      const response = await fetch(graphqlEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          variables: { userId },
        }),
      });
      
      const result = await response.json();
      
      if (result.data && result.data.userBanks) {
        // Format bank data with balance in currency format
        const formattedBanks = result.data.userBanks.map(bank => ({
          ...bank,
          formattedBalance: formatCurrency(bank.balance || 0)
        }));
        
        // Calculate the total balance from all banks
        const calculatedTotalBalance = formattedBanks.reduce((sum, bank) => sum + (Number(bank.balance) || 0), 0);
        
        setUserBanks(formattedBanks);
        setTotalBalance(calculatedTotalBalance);
        console.log('User banks loaded:', formattedBanks);
        console.log('Total balance:', calculatedTotalBalance);
      } else {
        console.error('Error fetching user banks:', result.errors);
        setUserBanks([]);
        setTotalBalance(0);
      }
    } catch (error) {
      console.error('Error fetching user banks:', error);
      setUserBanks([]);
      setTotalBalance(0);
    }
  };

  // Fetch budget summary data
  const fetchBudgetSummary = async (yearMonth) => {
    try {
      setIsLoading(true);
      const summaryResponse = await fetch(`${budgetSummaryUrl}/api/v1/transactions/budget-summary?user_id=${userId}&year_month=${yearMonth}`);
      if (summaryResponse.ok) {

        const data = await summaryResponse.json();
        
        console.log('Budget summary response:', data);
        // Format the budget summary data
        const formattedData = data.budgets.map(budget => ({
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

  // Load data when month changes or component mounts
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await Promise.all([
        fetchBudgetSummary(currentMonth),
        fetchUserBanks()
      ]);
      setIsLoading(false);
    };
    
    loadData();
  }, [currentMonth, userId]);

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

      {/* User Banks Summary */}
      {userBanks.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-gray-800">Tus Cuentas Bancarias</h3>
            <div className="text-right">
              <div className="text-sm text-gray-600">Balance Total</div>
              <div className={`text-lg font-bold ${totalBalance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {new Intl.NumberFormat('es-CL', {
                  style: 'currency',
                  currency: 'CLP',
                  minimumFractionDigits: 0
                }).format(totalBalance)}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {userBanks.map(bank => (
              <div key={bank.id} className="bg-gray-50 border border-gray-200 rounded-lg p-3 flex items-center">
                <div className="flex-shrink-0 mr-3">
                  {/* Use fallback icon since bank details aren't available */}
                  <div className="w-10 h-10 bg-blue-100 flex items-center justify-center rounded-full">
                    <i className="fas fa-university text-blue-500"></i>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{bank.description || `Cuenta ${bank.id}`}</div>
                  <div className="text-xs text-gray-500">ID: {bank.bankId || 'N/A'}</div>
                  <div className={`font-bold ${bank.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {bank.formattedBalance}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
        <BudgetSummary budgetSummary={budgetSummary} totalAvailableBalance={totalBalance} />
      </div>
    </div>
  );
};

export default DashboardBudgetSummary;
