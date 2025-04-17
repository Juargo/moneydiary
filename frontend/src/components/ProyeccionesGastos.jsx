import React, { useState, useEffect } from 'react';

const ProyeccionesGastos = ({ onVolver, budgetSummaryUrl }) => {
  const [proyecciones, setProyecciones] = useState([]);
  const [periodoActual, setPeriodoActual] = useState(0);
  const [userId, setUserId] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [budgetSummary, setBudgetSummary] = useState([]);
  const [proyeccionesIngresos, setProyeccionesIngresos] = useState([]);
  const [proyeccionesGastos, setProyeccionesGastos] = useState([]);
  const [currentMonth, setCurrentMonth] = useState(new Date().toISOString().substring(0, 7));
  
  // URL del API para proyecciones
  const apiUrl = budgetSummaryUrl || 'https://api.moneydiary.com'; // Valor por defecto
  
  // Genera los nombres de los meses para los próximos 3 años
  const generarMeses = () => {
    const meses = [];
    const nombresMeses = [
      'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    ];
    
    const fechaActual = new Date();
    const mesActual = fechaActual.getMonth();
    const yearActual = fechaActual.getFullYear();
    
    // Generar encabezados para 36 meses (3 años)
    for (let i = 0; i < 36; i++) {
      const mesIndex = (mesActual + i) % 12;
      const año = yearActual + Math.floor((mesActual + i) / 12);
      meses.push({
        nombre: nombresMeses[mesIndex],
        año: año,
        completo: `${nombresMeses[mesIndex]} ${año}`,
        yearMonth: `${año}-${String(mesIndex + 1).padStart(2, '0')}` // formato YYYY-MM
      });
    }
    
    return meses;
  };
  
  // Obtener encabezados de los meses
  const meses = generarMeses();
  
  // Function to format currency values
  const formatCurrency = (amount) => {
    const isNegative = amount < 0;
    const prefix = isNegative ? '-$' : '$';
    return `${prefix}${Math.abs(amount).toLocaleString('es-ES', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    })}`;
  };

  // Fetch budget summary data from API
  const fetchBudgetSummary = async (yearMonth) => {
    try {
      setIsLoading(true);
      const summaryResponse = await fetch(`${apiUrl}/api/v1/transactions/budget-summary?user_id=${userId}&year_month=${yearMonth}`);
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
        
        // Procesar datos para proyecciones de ingresos y gastos
        generarProyeccionesDesdePresupuesto(formattedData);
      } else {
        console.error('Error fetching budget summary:', await summaryResponse.text());
        setBudgetSummary([]);
        // Generar proyecciones con datos simulados como respaldo
        generarProyeccionesSimuladas();
      }
    } catch (error) {
      console.error('Error fetching budget summary:', error);
      setBudgetSummary([]);
      // Generar proyecciones con datos simulados como respaldo
      generarProyeccionesSimuladas();
    } finally {
      setIsLoading(false);
    }
  };

  // Generar proyecciones basadas en datos reales del presupuesto
  const generarProyeccionesDesdePresupuesto = (data) => {
    // Separar presupuestos en ingresos y gastos
    let presupuestoIngresos = data.find(budget => budget.name === "Ingresos");
    let presupuestosGastos = data.filter(budget => budget.name !== "Ingresos");
    
    // Procesar ingresos
    const ingresosProyecciones = [];
    if (presupuestoIngresos) {
      presupuestoIngresos.categories.forEach(category => {
        category.subcategories.forEach(subcategory => {
          // Usar el valor base real
          const valorBase = Math.abs(subcategory.total || 0);
          if (valorBase > 0) {
            // Generar proyección para este ingreso
            const valoresMensuales = meses.map((_, index) => {
              // Tendencia de aumento anual (3%)
              const mesesTranscurridos = index;
              const factorAnual = 1 + (0.03 / 12); // 3% anual convertido a mensual
              // Aplicar tendencia creciente
              return Math.round(valorBase * Math.pow(factorAnual, mesesTranscurridos));
            });
            
            ingresosProyecciones.push({
              categoria: subcategory.name,
              valores: valoresMensuales
            });
          }
        });
      });
    }
    
    // Procesar gastos
    const gastosProyecciones = [];
    presupuestosGastos.forEach(budget => {
      budget.categories.forEach(category => {
        category.subcategories.forEach(subcategory => {
          // Usar el valor base real
          const valorBase = Math.abs(subcategory.total || 0);
          if (valorBase > 0) {
            // Generar proyección para este gasto
            const valoresMensuales = meses.map((_, index) => {
              // Tendencia de aumento anual (entre 3% y 5%)
              const mesesTranscurridos = index;
              const factorInflacion = 1 + ((0.03 + Math.random() * 0.02) / 12);
              // Aplicar tendencia creciente con variación
              const variacion = 1 + (Math.random() * 0.08 - 0.04); // -4% a +4%
              return Math.round(valorBase * Math.pow(factorInflacion, mesesTranscurridos) * variacion);
            });
            
            gastosProyecciones.push({
              categoria: subcategory.name,
              presupuesto: budget.name,
              valores: valoresMensuales
            });
          }
        });
      });
    });
    
    setProyeccionesIngresos(ingresosProyecciones);
    setProyeccionesGastos(gastosProyecciones);
  };

  // Genera datos de proyección simulados en caso de fallo al obtener datos reales
  const generarProyeccionesSimuladas = () => {
    // Categorías de ingresos simuladas
    const categoriasIngresos = ["Salario", "Inversiones", "Otros Ingresos"];
    const ingresosSimulados = categoriasIngresos.map(categoria => {
      const valorBase = Math.floor(Math.random() * 1500000) + 500000;
      const valoresMensuales = meses.map((_, index) => {
        const tendencia = 1 + (Math.random() * 0.01); // 0-1% mensual
        const variacion = 1 + (Math.random() * 0.04 - 0.02); // -2% a +2%
        return Math.round(valorBase * Math.pow(tendencia, index) * variacion);
      });
      
      return {
        categoria,
        valores: valoresMensuales
      };
    });
    
    // Categorías de gastos simuladas
    const categoriasGastos = [
      "Vivienda", "Alimentación", "Transporte", 
      "Servicios", "Entretenimiento", "Salud",
      "Educación", "Seguros", "Otros"
    ];
    
    const gastosSimulados = categoriasGastos.map(categoria => {
      const valorBase = Math.floor(Math.random() * 300000) + 50000;
      const valoresMensuales = meses.map((_, index) => {
        const tendencia = 1 + (Math.random() * 0.02); // 0-2% mensual
        const variacion = 1 + (Math.random() * 0.1 - 0.05); // -5% a +5%
        return Math.round(valorBase * Math.pow(tendencia, index) * variacion);
      });
      
      return {
        categoria,
        presupuesto: "Gastos",
        valores: valoresMensuales
      };
    });
    
    setProyeccionesIngresos(ingresosSimulados);
    setProyeccionesGastos(gastosSimulados);
  };

  // Get userId from localStorage
  useEffect(() => {
    try {
      const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
      if (currentUser && currentUser.id) {
        console.log('Using userId from localStorage:', currentUser.id);
        setUserId(currentUser.id);
      } else {
        console.warn('No user ID found in localStorage');
        setUserId(0);
      }
    } catch (error) {
      console.error('Error parsing user from localStorage:', error);
      setUserId(0);
    }
  }, []);

  // Fetch data when userId changes or component mounts
  useEffect(() => {
    if (userId) {
      fetchBudgetSummary(currentMonth);
    } else {
      // Generate simulated projections if no userId available
      generarProyeccionesSimuladas();
    }
  }, [userId, currentMonth]);
  
  // Calcula los totales mensuales para ingresos
  const totalesMensualesIngresos = proyeccionesIngresos.length > 0 
    ? meses.map((_, mesIndex) => 
        proyeccionesIngresos.reduce((total, { valores }) => total + valores[mesIndex], 0)
      )
    : [];
  
  // Calcula los totales mensuales para gastos
  const totalesMensualesGastos = proyeccionesGastos.length > 0 
    ? meses.map((_, mesIndex) => 
        proyeccionesGastos.reduce((total, { valores }) => total + valores[mesIndex], 0)
      )
    : [];
    
  // Calcula balance mensual (Ingresos - Gastos)
  const balanceMensual = totalesMensualesIngresos.map((ingreso, index) => {
    const gasto = totalesMensualesGastos[index] || 0;
    return ingreso - gasto;
  });
  
  // Control para navegar por períodos de 12 meses
  const mesesVisibles = 12;
  const maximoPeriodos = Math.ceil(meses.length / mesesVisibles) - 1;
  
  const avanzarPeriodo = () => {
    setPeriodoActual(prev => Math.min(prev + 1, maximoPeriodos));
  };
  
  const retrocederPeriodo = () => {
    setPeriodoActual(prev => Math.max(prev - 1, 0));
  };
  
  // Filtrar meses según el período seleccionado
  const mesesFiltrados = meses.slice(
    periodoActual * mesesVisibles,
    (periodoActual + 1) * mesesVisibles
  );

  return (
    <div style={{ padding: "1.5rem 0" }}>
      <div style={{ maxWidth: "90rem", margin: "0 auto", padding: "0 1rem" }}>
        <div style={{ backgroundColor: "white", borderRadius: "0.5rem", overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.12)" }}>
          <div style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
              <h2 style={{ fontSize: "1.5rem", fontWeight: "600", color: "#1f2937" }}>
                <i className="fas fa-chart-line" style={{ color: "#8b5cf6", marginRight: "0.75rem" }}></i>
                Proyección de Gastos
              </h2>
              <button 
                onClick={onVolver}
                style={{ 
                  padding: "0.5rem 1rem", 
                  backgroundColor: "#f3f4f6", 
                  border: "1px solid #e5e7eb",
                  borderRadius: "0.375rem",
                  color: "#374151",
                  fontWeight: "500",
                  display: "flex",
                  alignItems: "center"
                }}
              >
                <i className="fas fa-arrow-left" style={{ marginRight: "0.5rem" }}></i>
                Volver
              </button>
            </div>
            
            <div style={{ backgroundColor: "#eff6ff", padding: "1rem", borderRadius: "0.375rem", marginBottom: "1.5rem" }}>
              <p style={{ color: "#1d4ed8" }}>
                <i className="fas fa-info-circle" style={{ marginRight: "0.5rem" }}></i>
                Esta proyección estima tus ingresos y gastos futuros basándose en tu presupuesto actual y tendencias de inflación estimadas.
              </p>
            </div>
            
            {isLoading && (
              <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
                <div style={{ display: "flex", alignItems: "center" }}>
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <p style={{ marginLeft: "0.75rem", color: "#6b7280" }}>Cargando proyecciones...</p>
                </div>
              </div>
            )}
            
            {!isLoading && (
              <>
                <div style={{ marginBottom: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <h3 style={{ fontSize: "1.125rem", fontWeight: "500", color: "#111827" }}>
                      {periodoActual === 0 ? "Próximos 12 meses" : `${mesesFiltrados[0].completo} - ${mesesFiltrados[mesesFiltrados.length - 1].completo}`}
                    </h3>
                  </div>
                  <div>
                    <button
                      onClick={retrocederPeriodo}
                      disabled={periodoActual === 0}
                      style={{
                        padding: "0.5rem 0.75rem",
                        backgroundColor: periodoActual === 0 ? "#e5e7eb" : "#f3f4f6",
                        border: "1px solid #d1d5db",
                        borderRadius: "0.375rem 0 0 0.375rem",
                        color: periodoActual === 0 ? "#9ca3af" : "#374151"
                      }}
                    >
                      <i className="fas fa-chevron-left"></i>
                    </button>
                    <button
                      onClick={avanzarPeriodo}
                      disabled={periodoActual === maximoPeriodos}
                      style={{
                        padding: "0.5rem 0.75rem",
                        backgroundColor: periodoActual === maximoPeriodos ? "#e5e7eb" : "#f3f4f6",
                        border: "1px solid #d1d5db",
                        borderLeft: "none",
                        borderRadius: "0 0.375rem 0.375rem 0",
                        color: periodoActual === maximoPeriodos ? "#9ca3af" : "#374151"
                      }}
                    >
                      <i className="fas fa-chevron-right"></i>
                    </button>
                  </div>
                </div>
                
                {/* Tabla de Ingresos */}
                <div style={{ marginBottom: "2rem" }}>
                  <h3 style={{ 
                    fontSize: "1.125rem", 
                    fontWeight: "500", 
                    color: "#166534", 
                    padding: "0.5rem 1rem",
                    backgroundColor: "#f0fdf4",
                    borderRadius: "0.375rem",
                    marginBottom: "0.75rem",
                    display: "flex",
                    alignItems: "center"
                  }}>
                    <i className="fas fa-arrow-down" style={{ marginRight: "0.5rem" }}></i>
                    Proyección de Ingresos
                  </h3>
                  
                  <div style={{ overflowX: "auto", marginBottom: "1rem" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "right", fontSize: "0.875rem" }}>
                      <thead>
                        <tr style={{ backgroundColor: "#f9fafb", borderBottom: "1px solid #e5e7eb" }}>
                          <th style={{ padding: "0.75rem 1rem", position: "sticky", left: 0, backgroundColor: "#f9fafb", textAlign: "left", zIndex: 10 }}>Fuente de Ingreso</th>
                          {mesesFiltrados.map((mes, index) => (
                            <th key={index} style={{ padding: "0.75rem 1rem", minWidth: "100px" }}>
                              {mes.nombre} <span style={{ fontSize: "0.75rem", color: "#6b7280" }}>{mes.año}</span>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {proyeccionesIngresos.map((proyeccion, idx) => (
                          <tr key={idx} style={{ borderBottom: "1px solid #e5e7eb" }}>
                            <td style={{ 
                              padding: "0.75rem 1rem", 
                              fontWeight: "500", 
                              color: "#111827", 
                              position: "sticky", 
                              left: 0, 
                              backgroundColor: "white",
                              textAlign: "left",
                              borderRight: "1px solid #f3f4f6",
                              zIndex: 5
                            }}>
                              {proyeccion.categoria}
                            </td>
                            {proyeccion.valores
                              .slice(periodoActual * mesesVisibles, (periodoActual + 1) * mesesVisibles)
                              .map((valor, mesIdx) => (
                                <td key={mesIdx} style={{ padding: "0.75rem 1rem", color: "#15803d" }}>
                                  ${valor.toLocaleString()}
                                </td>
                              ))}
                          </tr>
                        ))}
                        <tr style={{ borderBottom: "1px solid #e5e7eb", backgroundColor: "#f0fdf4", fontWeight: "600" }}>
                          <td style={{ 
                            padding: "0.75rem 1rem", 
                            position: "sticky", 
                            left: 0, 
                            backgroundColor: "#f0fdf4",
                            textAlign: "left",
                            borderRight: "1px solid #f3f4f6",
                            zIndex: 5
                          }}>
                            TOTAL INGRESOS
                          </td>
                          {totalesMensualesIngresos
                            .slice(periodoActual * mesesVisibles, (periodoActual + 1) * mesesVisibles)
                            .map((total, idx) => (
                              <td key={idx} style={{ padding: "0.75rem 1rem", color: "#15803d" }}>
                                ${total.toLocaleString()}
                              </td>
                            ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                
                {/* Tabla de Gastos */}
                <div style={{ marginBottom: "2rem" }}>
                  <h3 style={{ 
                    fontSize: "1.125rem", 
                    fontWeight: "500", 
                    color: "#b91c1c", 
                    padding: "0.5rem 1rem",
                    backgroundColor: "#fef2f2",
                    borderRadius: "0.375rem",
                    marginBottom: "0.75rem",
                    display: "flex",
                    alignItems: "center"
                  }}>
                    <i className="fas fa-arrow-up" style={{ marginRight: "0.5rem" }}></i>
                    Proyección de Gastos
                  </h3>
                  
                  <div style={{ overflowX: "auto", marginBottom: "1rem" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "right", fontSize: "0.875rem" }}>
                      <thead>
                        <tr style={{ backgroundColor: "#f9fafb", borderBottom: "1px solid #e5e7eb" }}>
                          <th style={{ padding: "0.75rem 1rem", position: "sticky", left: 0, backgroundColor: "#f9fafb", textAlign: "left", zIndex: 10 }}>Categoría de Gasto</th>
                          {mesesFiltrados.map((mes, index) => (
                            <th key={index} style={{ padding: "0.75rem 1rem", minWidth: "100px" }}>
                              {mes.nombre} <span style={{ fontSize: "0.75rem", color: "#6b7280" }}>{mes.año}</span>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {proyeccionesGastos.map((proyeccion, idx) => (
                          <tr key={idx} style={{ borderBottom: "1px solid #e5e7eb" }}>
                            <td style={{ 
                              padding: "0.75rem 1rem", 
                              fontWeight: "500", 
                              color: "#111827", 
                              position: "sticky", 
                              left: 0, 
                              backgroundColor: "white",
                              textAlign: "left",
                              borderRight: "1px solid #f3f4f6",
                              zIndex: 5
                            }}>
                              <div>{proyeccion.categoria}</div>
                              {proyeccion.presupuesto && (
                                <div style={{ fontSize: "0.75rem", color: "#6b7280" }}>{proyeccion.presupuesto}</div>
                              )}
                            </td>
                            {proyeccion.valores
                              .slice(periodoActual * mesesVisibles, (periodoActual + 1) * mesesVisibles)
                              .map((valor, mesIdx) => (
                                <td key={mesIdx} style={{ padding: "0.75rem 1rem", color: "#b91c1c" }}>
                                  ${valor.toLocaleString()}
                                </td>
                              ))}
                          </tr>
                        ))}
                        <tr style={{ borderBottom: "1px solid #e5e7eb", backgroundColor: "#fef2f2", fontWeight: "600" }}>
                          <td style={{ 
                            padding: "0.75rem 1rem", 
                            position: "sticky", 
                            left: 0, 
                            backgroundColor: "#fef2f2",
                            textAlign: "left",
                            borderRight: "1px solid #f3f4f6",
                            zIndex: 5
                          }}>
                            TOTAL GASTOS
                          </td>
                          {totalesMensualesGastos
                            .slice(periodoActual * mesesVisibles, (periodoActual + 1) * mesesVisibles)
                            .map((total, idx) => (
                              <td key={idx} style={{ padding: "0.75rem 1rem", color: "#b91c1c" }}>
                                ${total.toLocaleString()}
                              </td>
                            ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                
                {/* Tabla de Balance Mensual */}
                <div style={{ marginBottom: "2rem" }}>
                  <h3 style={{ 
                    fontSize: "1.125rem", 
                    fontWeight: "500", 
                    color: "#1e40af", 
                    padding: "0.5rem 1rem",
                    backgroundColor: "#eff6ff",
                    borderRadius: "0.375rem",
                    marginBottom: "0.75rem",
                    display: "flex",
                    alignItems: "center"
                  }}>
                    <i className="fas fa-chart-line" style={{ marginRight: "0.5rem" }}></i>
                    Balance Proyectado Mensual
                  </h3>
                  
                  <div style={{ overflowX: "auto", marginBottom: "1rem" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "right", fontSize: "0.875rem" }}>
                      <thead>
                        <tr style={{ backgroundColor: "#f9fafb", borderBottom: "1px solid #e5e7eb" }}>
                          <th style={{ padding: "0.75rem 1rem", position: "sticky", left: 0, backgroundColor: "#f9fafb", textAlign: "left", zIndex: 10 }}>Concepto</th>
                          {mesesFiltrados.map((mes, index) => (
                            <th key={index} style={{ padding: "0.75rem 1rem", minWidth: "100px" }}>
                              {mes.nombre} <span style={{ fontSize: "0.75rem", color: "#6b7280" }}>{mes.año}</span>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr style={{ borderBottom: "1px solid #e5e7eb", backgroundColor: "#eff6ff", fontWeight: "600" }}>
                          <td style={{ 
                            padding: "0.75rem 1rem", 
                            position: "sticky", 
                            left: 0, 
                            backgroundColor: "#eff6ff",
                            textAlign: "left",
                            borderRight: "1px solid #f3f4f6",
                            zIndex: 5
                          }}>
                            BALANCE MENSUAL
                          </td>
                          {balanceMensual
                            .slice(periodoActual * mesesVisibles, (periodoActual + 1) * mesesVisibles)
                            .map((balance, idx) => (
                              <td key={idx} style={{ 
                                padding: "0.75rem 1rem", 
                                color: balance >= 0 ? "#15803d" : "#b91c1c",
                                fontWeight: "bold"
                              }}>
                                ${balance.toLocaleString()}
                              </td>
                            ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                
                <div style={{ backgroundColor: "#f9fafb", padding: "1.25rem", borderRadius: "0.5rem", border: "1px solid #e5e7eb" }}>
                  <h4 style={{ fontSize: "1rem", fontWeight: "500", color: "#111827", marginBottom: "0.75rem" }}>
                    <i className="fas fa-lightbulb" style={{ color: "#d97706", marginRight: "0.5rem" }}></i>
                    Observaciones
                  </h4>
                  <ul style={{ color: "#4b5563", paddingLeft: "1.5rem" }}>
                    <li style={{ marginBottom: "0.5rem" }}>Las proyecciones están basadas en tu presupuesto actual y patrones históricos.</li>
                    <li style={{ marginBottom: "0.5rem" }}>Se considera una tasa de inflación promedio entre 3% y 5% anual para gastos.</li>
                    <li style={{ marginBottom: "0.5rem" }}>Para ingresos, se estima un crecimiento anual del 3%.</li>
                    <li>Ajusta tu presupuesto con anticipación para prepararte para meses con balance negativo.</li>
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProyeccionesGastos;
