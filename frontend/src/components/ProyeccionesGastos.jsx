import React, { useState, useEffect } from 'react';

const ProyeccionesGastos = ({ onVolver }) => {
  const [proyecciones, setProyecciones] = useState([]);
  const [periodoActual, setPeriodoActual] = useState(0);
  
  // Categorías de gastos para las proyecciones
  const categorias = [
    "Vivienda", 
    "Alimentación", 
    "Transporte", 
    "Servicios", 
    "Entretenimiento",
    "Salud",
    "Educación",
    "Otros"
  ];
  
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
        completo: `${nombresMeses[mesIndex]} ${año}`
      });
    }
    
    return meses;
  };
  
  // Obtener encabezados de los meses
  const meses = generarMeses();
  
  // Genera datos de proyección simulados
  useEffect(() => {
    const generarProyecciones = () => {
      return categorias.map(categoria => {
        // Valor base aleatorio entre 200 y 2000
        const valorBase = Math.floor(Math.random() * 1800) + 200;
        
        // Genera valores para cada mes con pequeñas variaciones
        const valoresMensuales = meses.map((_, index) => {
          // Añadir una tendencia alcista suave (1-3% mensual de aumento)
          const tendencia = 1 + (Math.random() * 0.02);
          // Variación aleatoria adicional -5% a +5%
          const variacion = 1 + (Math.random() * 0.1 - 0.05);
          // Calcula el valor con la tendencia acumulativa
          return Math.round(valorBase * Math.pow(tendencia, index) * variacion);
        });
        
        return {
          categoria,
          valores: valoresMensuales
        };
      });
    };
    
    setProyecciones(generarProyecciones());
  }, []);
  
  // Calcula los totales mensuales
  const totalesMensuales = proyecciones.length > 0 
    ? meses.map((_, mesIndex) => 
        proyecciones.reduce((total, { valores }) => total + valores[mesIndex], 0)
      )
    : [];
  
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
                Esta proyección estima tus gastos futuros basándose en patrones históricos y tendencias de inflación estimadas.
              </p>
            </div>
            
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
            
            <div style={{ overflowX: "auto", marginBottom: "1.5rem" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "right", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ backgroundColor: "#f9fafb", borderBottom: "1px solid #e5e7eb" }}>
                    <th style={{ padding: "0.75rem 1rem", position: "sticky", left: 0, backgroundColor: "#f9fafb", textAlign: "left", zIndex: 10 }}>Categoría</th>
                    {mesesFiltrados.map((mes, index) => (
                      <th key={index} style={{ padding: "0.75rem 1rem", minWidth: "100px" }}>
                        {mes.nombre} <span style={{ fontSize: "0.75rem", color: "#6b7280" }}>{mes.año}</span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {proyecciones.map((proyeccion, idx) => (
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
                          <td key={mesIdx} style={{ padding: "0.75rem 1rem" }}>
                            ${valor.toLocaleString()}
                          </td>
                        ))}
                    </tr>
                  ))}
                  <tr style={{ borderBottom: "1px solid #e5e7eb", backgroundColor: "#f9fafb", fontWeight: "600" }}>
                    <td style={{ 
                      padding: "0.75rem 1rem", 
                      position: "sticky", 
                      left: 0, 
                      backgroundColor: "#f9fafb",
                      textAlign: "left",
                      borderRight: "1px solid #f3f4f6",
                      zIndex: 5
                    }}>
                      TOTAL
                    </td>
                    {totalesMensuales
                      .slice(periodoActual * mesesVisibles, (periodoActual + 1) * mesesVisibles)
                      .map((total, idx) => (
                        <td key={idx} style={{ padding: "0.75rem 1rem", color: "#1d4ed8" }}>
                          ${total.toLocaleString()}
                        </td>
                      ))}
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div style={{ backgroundColor: "#f9fafb", padding: "1.25rem", borderRadius: "0.5rem", border: "1px solid #e5e7eb" }}>
              <h4 style={{ fontSize: "1rem", fontWeight: "500", color: "#111827", marginBottom: "0.75rem" }}>
                <i className="fas fa-lightbulb" style={{ color: "#d97706", marginRight: "0.5rem" }}></i>
                Observaciones
              </h4>
              <ul style={{ color: "#4b5563", paddingLeft: "1.5rem" }}>
                <li style={{ marginBottom: "0.5rem" }}>Las proyecciones son estimaciones basadas en patrones históricos.</li>
                <li style={{ marginBottom: "0.5rem" }}>Se considera una tasa de inflación promedio entre 1% y 3% mensual.</li>
                <li>Ajusta tu presupuesto con anticipación para prepararte para gastos futuros.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProyeccionesGastos;
