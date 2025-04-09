import React, { useState, useEffect } from 'react';
import TransactionsList from './TransactionsList';
import BudgetSummary from './BudgetSummary';

const TransactionsManager = ({ userId, apiUrl, budgetSummaryUrl, initialMonth }) => {
  const [activeTab, setActiveTab] = useState('budget-summary');
  const [currentMonth, setCurrentMonth] = useState(initialMonth);
  const [transactions, setTransactions] = useState([]);
  const [budgetSummary, setBudgetSummary] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [displayPeriod, setDisplayPeriod] = useState(initialMonth);

  // Function to format currency values
  const formatCurrency = (amount) => {
    const isNegative = amount < 0;
    const prefix = isNegative ? '-$' : '+$';
    return `${prefix}${Math.abs(amount).toLocaleString('es-ES', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    })}`;
  };

  // Fetch transaction data
  const fetchTransactions = async (yearMonth) => {
    try {
      const query = `
        query GetUserTransactions($userId: Int!, $yearMonth: String) {
          userTransactions(userId: $userId, yearMonth: $yearMonth) {
            id
            transactionDate
            description
            amount
            type
            userBankId
            subcategoryId
            userBankName
            bankName
            subcategoryName
            categoryName
          }
        }
      `;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          variables: { 
            userId,
            yearMonth
          },
        }),
      });
      
      const result = await response.json();
      if (result.data && result.data.userTransactions) {
        const formattedTransactions = result.data.userTransactions.map(tx => {
          // Format the date (comes as ISO string)
          const date = new Date(tx.transactionDate);
          const formattedDate = date.toISOString().split('T')[0];
          
          // Determine if it's an expense based on the type
          const isExpense = tx.type === 'Gasto';
          
          return {
            ...tx,
            date: formattedDate,
            isExpense,
            formattedAmount: formatCurrency(tx.amount),
            category: tx.categoryName,
          };
        });
        setTransactions(formattedTransactions);
      } else {
        setTransactions([]);
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setTransactions([]);
    }
  };

  // Fetch budget summary data
  const fetchBudgetSummary = async (yearMonth) => {
    try {
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
    }
  };

  // Load data when month changes
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await Promise.all([
        fetchTransactions(currentMonth),
        fetchBudgetSummary(currentMonth)
      ]);
      setIsLoading(false);
    };
    
    loadData();
  }, [currentMonth]);

  // Handle month change
  const handleMonthChange = (event) => {
    const newMonth = event.target.value;
    setCurrentMonth(newMonth);
    
    // Update URL without page reload
    const url = new URL(window.location);
    url.searchParams.set('month', newMonth);
    window.history.pushState({}, '', url);
  };

  return (
    <div>
      {/* Month Filter - Common for both tabs */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="w-full md:w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">Periodo</label>
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-5 rounded-lg shadow-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Cargando datos...</p>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="mb-4 border-b border-gray-200">
        <ul className="flex flex-wrap -mb-px text-sm font-medium text-center">
          <li className="mr-2">
            <button 
              className={`inline-block p-4 border-b-2 rounded-t-lg ${activeTab === 'transactions' ? 'border-primary-600 text-primary-600' : 'border-transparent hover:text-gray-600 hover:border-gray-300'}`}
              onClick={() => setActiveTab('transactions')}
            >
              <i className="fas fa-list-ul mr-2"></i>Listado de Transacciones
            </button>
          </li>
          <li className="mr-2">
            <button 
              className={`inline-block p-4 border-b-2 rounded-t-lg ${activeTab === 'budget-summary' ? 'border-primary-600 text-primary-600' : 'border-transparent hover:text-gray-600 hover:border-gray-300'}`}
              onClick={() => setActiveTab('budget-summary')}
            >
              <i className="fas fa-chart-pie mr-2"></i>Resumen Presupuestario
            </button>
          </li>
        </ul>
      </div>
      
      {/* Tab Content */}
      <div>
        {activeTab === 'transactions' ? (
          <TransactionsList transactions={transactions} />
        ) : (
          <BudgetSummary budgetSummary={budgetSummary} />
        )}
      </div>
    </div>
  );
};

export default TransactionsManager;
