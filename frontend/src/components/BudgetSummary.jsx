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
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Resumen de Presupuestos</h2>
        
        {sortedBudgetData.length > 0 ? (
          <div className="space-y-4">
            {sortedBudgetData.map((budget) => (
              <div key={budget.id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Budget Accordion Header */}
                <div 
                  className="flex items-center justify-between p-4 bg-gray-50 cursor-pointer" 
                  onClick={() => toggleAccordion('budget', budget.id)}
                >
                  <div className="flex items-center">
                    <i className={`fas fa-chevron-right text-gray-500 mr-2 transform transition-transform duration-200 ${isExpanded('budget', budget.id) ? 'rotate-90' : ''}`}></i>
                    <span className="font-medium">{budget.name}</span>
                  </div>
                  <div className={`font-semibold ${budget.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {budget.formattedTotal}
                  </div>
                </div>
                
                {/* Budget Accordion Content */}
                <div className={`p-4 pl-8 ${isExpanded('budget', budget.id) ? 'block' : 'hidden'}`}>
                  {budget.categories.map((category) => (
                    <div key={category.id} className="border border-gray-200 rounded-lg overflow-hidden mb-3">
                      {/* Category Accordion Header */}
                      <div 
                        className="flex items-center justify-between p-3 bg-gray-50 cursor-pointer" 
                        onClick={() => toggleAccordion('category', category.id)}
                      >
                        <div className="flex items-center">
                          <i className={`fas fa-chevron-right text-gray-500 mr-2 transform transition-transform duration-200 ${isExpanded('category', category.id) ? 'rotate-90' : ''}`}></i>
                          <span className="font-medium">{category.name}</span>
                        </div>
                        <div className={`font-semibold ${category.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {category.formattedTotal}
                        </div>
                      </div>
                      
                      {/* Category Accordion Content */}
                      <div className={`p-3 pl-8 ${isExpanded('category', category.id) ? 'block' : 'hidden'}`}>
                        {category.subcategories.map((subcategory) => (
                          <div key={subcategory.id} className="border border-gray-200 rounded-lg overflow-hidden mb-2">
                            {/* Subcategory Accordion Header */}
                            <div 
                              className="flex items-center justify-between p-2 bg-gray-50 cursor-pointer" 
                              onClick={() => toggleAccordion('subcategory', subcategory.id)}
                            >
                              <div className="flex items-center">
                                <i className={`fas fa-chevron-right text-gray-500 mr-2 transform transition-transform duration-200 ${isExpanded('subcategory', subcategory.id) ? 'rotate-90' : ''}`}></i>
                                <span className="font-medium">{subcategory.name}</span>
                              </div>
                              <div className={`font-semibold ${subcategory.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                {subcategory.formattedTotal}
                              </div>
                            </div>
                            
                            {/* Subcategory Accordion Content (Patterns) */}
                            <div className={`p-2 pl-8 ${isExpanded('subcategory', subcategory.id) ? 'block' : 'hidden'}`}>
                              <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                  <tr>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patrón</th>
                                    <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Transacciones</th>
                                    <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                                  </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                  {subcategory.patterns.map((pattern) => (
                                    <tr key={pattern.id}>
                                      <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">{pattern.text}</td>
                                      <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500 text-right">{pattern.transaction_count}</td>
                                      <td className={`px-3 py-2 whitespace-nowrap text-sm font-medium text-right ${pattern.total < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                        {pattern.formattedTotal}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
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
