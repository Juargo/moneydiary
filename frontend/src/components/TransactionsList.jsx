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
      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div className="text-sm text-gray-700">
          Mostrando <span className="font-medium">1</span> a <span className="font-medium">{transactions.length}</span> de <span className="font-medium">{transactions.length}</span> resultados
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50" disabled={transactions.length <= 10}>
            Anterior
          </button>
          <button className="px-4 py-2 border border-gray-300 bg-primary-50 rounded-md text-sm font-medium text-primary-700 hover:bg-primary-100">
            1
          </button>
          {transactions.length > 10 && (
            <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
              2
            </button>
          )}
          {transactions.length > 20 && (
            <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
              3
            </button>
          )}
          <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50" disabled={transactions.length <= 10}>
            Siguiente
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransactionsList;
