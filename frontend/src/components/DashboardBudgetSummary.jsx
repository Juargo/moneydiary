import React, { useState, useEffect } from 'react';
import BudgetSummary from './BudgetSummary';

const DashboardBudgetSummary = ({ userId, budgetSummaryUrl, initialMonth }) => {
  const [currentMonth, setCurrentMonth] = useState(initialMonth || new Date().toISOString().substring(0, 7));
  const [budgetSummary, setBudgetSummary] = useState([]);
  const [budgetConfig, setBudgetConfig] = useState([]);
  const [userBanks, setUserBanks] = useState([]);
  const [totalBalance, setTotalBalance] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [displayPeriod, setDisplayPeriod] = useState(initialMonth || new Date().toISOString().substring(0, 7));
  const [incomeTotal, setIncomeTotal] = useState(0);
  const [expensesTotal, setExpensesTotal] = useState(0);
  const [theoreticalBalance, setTheoreticalBalance] = useState(0);
  const [balanceDifference, setBalanceDifference] = useState(0);

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

  // Fetch budget configuration from GraphQL
  const fetchBudgetConfig = async () => {
    try {
      const graphqlEndpoint = `${budgetSummaryUrl}/graphql`;
      
      const query = `
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
      
      if (result.data && result.data.budgetConfig) {
        console.log('Budget config loaded:', result.data.budgetConfig);
        setBudgetConfig(result.data.budgetConfig);
      } else {
        console.error('Error fetching budget config:', result.errors);
        setBudgetConfig([]);
      }
    } catch (error) {
      console.error('Error fetching budget config:', error);
      setBudgetConfig([]);
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
        
        // Calculate income and expense totals
        let income = 0;
        let expenses = 0;
        
        data.budgets.forEach(budget => {
          if (budget.name === "Ingresos") {
            income = budget.total || 0;
          } else {
            // Sum up all other budgets as expenses
            expenses += budget.total || 0;
          }
        });
        
        const calculatedTheoreticalBalance = income - -expenses;
        
        setIncomeTotal(income);
        setExpensesTotal(expenses);
        setTheoreticalBalance(calculatedTheoreticalBalance);
        
        // Calculate difference with actual bank balances
        const difference = totalBalance - calculatedTheoreticalBalance;
        setBalanceDifference(difference);
        
        console.log('Income:', income, 'Expenses:', expenses, 'Theoretical Balance:', calculatedTheoreticalBalance, 'Actual Balance:', totalBalance, 'Difference:', difference);
        
        // Update the display period if available
        if (data.length > 0 && data[0].period) {
          setDisplayPeriod(data[0].period);
        }
      } else {
        console.error('Error fetching budget summary:', await summaryResponse.text());
        setBudgetSummary([]);
        setIncomeTotal(0);
        setExpensesTotal(0);
        setTheoreticalBalance(0);
        setBalanceDifference(0);
      }
    } catch (error) {
      console.error('Error fetching budget summary:', error);
      setBudgetSummary([]);
      setIncomeTotal(0);
      setExpensesTotal(0);
      setTheoreticalBalance(0);
      setBalanceDifference(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Load data when month changes or component mounts
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await fetchUserBanks();
      await fetchBudgetConfig(); // Fetch budget configuration
      await fetchBudgetSummary(currentMonth);
      setIsLoading(false);
    };
    
    loadData();
  }, [currentMonth, userId]);

  // Recalculate balance difference when bank total or theoretical balance changes
  useEffect(() => {
    const difference = totalBalance - theoreticalBalance;
    setBalanceDifference(difference);
  }, [totalBalance, theoreticalBalance]);

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
          
          {/* Balance Comparison Section */}
          <div className="mb-4 border-t border-gray-200 pt-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-blue-50 p-2 rounded">
                <div className="text-gray-600">Ingresos del Mes</div>
                <div className="font-bold text-green-600">
                  {new Intl.NumberFormat('es-CL', {
                    style: 'currency',
                    currency: 'CLP',
                    minimumFractionDigits: 0
                  }).format(incomeTotal)}
                </div>
              </div>
              <div className="bg-blue-50 p-2 rounded">
                <div className="text-gray-600">Gastos Presupuestados</div>
                <div className="font-bold text-red-600">
                  {new Intl.NumberFormat('es-CL', {
                    style: 'currency',
                    currency: 'CLP',
                    minimumFractionDigits: 0
                  }).format(expensesTotal)}
                </div>
              </div>
              <div className="bg-blue-50 p-2 rounded">
                <div className="text-gray-600">Balance Teórico</div>
                <div className={`font-bold ${theoreticalBalance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {new Intl.NumberFormat('es-CL', {
                    style: 'currency',
                    currency: 'CLP',
                    minimumFractionDigits: 0
                  }).format(theoreticalBalance)}
                </div>
              </div>
            </div>
            
            {/* Display difference if it exists */}
            {Math.abs(balanceDifference) > 0 && (
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center">
                  <div className="mr-2 text-yellow-500">
                    <i className="fas fa-exclamation-triangle"></i>
                  </div>
                  <div>
                    <div className="font-medium">Diferencia Detectada</div>
                    <div className="text-sm">
                      El balance de tus cuentas 
                      <span className={`font-bold ${balanceDifference > 0 ? ' text-green-600' : ' text-red-600'}`}>
                        {' '}{balanceDifference > 0 ? 'excede' : 'es menor que'}{' '}
                      </span>
                      el balance teórico por:
                      <span className={`ml-1 font-bold ${balanceDifference > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {new Intl.NumberFormat('es-CL', {
                          style: 'currency',
                          currency: 'CLP',
                          minimumFractionDigits: 0
                        }).format(Math.abs(balanceDifference))}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
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
        <BudgetSummary 
          budgetSummary={budgetSummary} 
          budgetConfig={budgetConfig} 
          totalAvailableBalance={totalBalance}
        />
      </div>
    </div>
  );
};

export default DashboardBudgetSummary;
