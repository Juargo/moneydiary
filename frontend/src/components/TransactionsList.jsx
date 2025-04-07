import React from 'react';

const TransactionsList = ({ transactions }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subcategoría</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cuenta</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Monto</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {transactions.length > 0 ? (
              transactions.map(tx => (
                <tr key={tx.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{tx.description}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.categoryName}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.subcategoryName}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.userBankName} ({tx.bankName})</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.date}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${tx.isExpense ? 'text-red-600' : 'text-green-600'}`}>
                    {tx.formattedAmount}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-primary-600 hover:text-primary-900 mr-3">
                      <i className="fas fa-edit"></i>
                    </button>
                    <button className="text-red-600 hover:text-red-900">
                      <i className="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                  No se encontraron transacciones para el período seleccionado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-4 border-t border-gray-200 text-center text-sm text-gray-700">
        Total: <span className="font-medium">{transactions.length}</span> transacciones
      </div>
    </div>
  );
};

export default TransactionsList;
