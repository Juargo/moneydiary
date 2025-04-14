import React from 'react';

export default function BudgetSummary({ totalBudgeted, totalSpent, totalRemaining }) {
  // Format currency values
  const formatCurrency = (amount) => {
    // Handle undefined, null or non-number values
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '0.00';
    }
    return amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4">Resumen de Presupuestos</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="text-sm text-green-700 font-medium">Total Presupuestado</h3>
          <p className="text-2xl font-bold text-green-800">${formatCurrency(totalBudgeted)}</p>
        </div>
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm text-blue-700 font-medium">Total Gastado</h3>
          <p className="text-2xl font-bold text-blue-800">${formatCurrency(totalSpent)}</p>
        </div>
        <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
          <h3 className="text-sm text-indigo-700 font-medium">Total Disponible</h3>
          <p className="text-2xl font-bold text-indigo-800">${formatCurrency(totalRemaining)}</p>
        </div>
      </div>
    </div>
  );
}
