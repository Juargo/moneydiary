import React from 'react';

export default function PatternIgnoreTable({ 
  patternIgnores, 
  onAddPatternIgnore, 
  onEditPatternIgnore, 
  onDeletePatternIgnore 
}) {
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Patrones a Ignorar</h2>
        <button 
          onClick={onAddPatternIgnore}
          className="bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg flex items-center"
        >
          <i className="fas fa-plus mr-2"></i> Nuevo Patrón a Ignorar
        </button>
      </div>
      
      <p className="text-sm text-gray-600 mb-4">
        Los patrones a ignorar te permiten excluir ciertas transacciones del procesamiento automático. 
        Útil para transferencias entre tus propias cuentas o cargos bancarios que no quieres categorizar.
      </p>
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patrón</th>
              <th className="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
              <th className="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha Creación</th>
              <th className="py-2 px-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200" id="patternIgnoresTable">
            {patternIgnores.length > 0 ? (
              patternIgnores.map((pattern) => (
                <tr key={pattern.id}>
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">{pattern.expName}</td>
                  <td className="py-3 px-4 text-sm text-gray-500">{pattern.description}</td>
                  <td className="py-3 px-4 text-sm text-gray-500">{formatDate(pattern.createdAt)}</td>
                  <td className="py-3 px-4 text-right text-sm font-medium">
                    <button 
                      className="text-primary-600 hover:text-primary-900 mr-3" 
                      onClick={() => onEditPatternIgnore(pattern)}
                    >
                      <i className="fas fa-edit"></i>
                    </button>
                    <button 
                      className="text-red-600 hover:text-red-900" 
                      onClick={() => onDeletePatternIgnore(pattern)}
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="py-4 px-4 text-sm text-gray-500 text-center">No hay patrones a ignorar definidos</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
