import React from 'react';

const Planificador = () => {
  return (
    <div style={{ padding: "1.5rem 0" }}>
      <div style={{ maxWidth: "80rem", margin: "0 auto", padding: "0 1rem" }}>
        <div style={{ backgroundColor: "white", borderRadius: "0.5rem", overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.12)" }}>
          <div style={{ padding: "1.5rem" }}>
            <h2 style={{ fontSize: "1.5rem", fontWeight: "600", color: "#1f2937", marginBottom: "1rem" }}>Planificador Financiero</h2>
            
            <div style={{ backgroundColor: "#eff6ff", padding: "1rem", borderRadius: "0.375rem", marginBottom: "1.5rem" }}>
              <p style={{ color: "#1d4ed8" }}>
                Usa esta herramienta para planificar tus finanzas a futuro y establecer metas financieras.
              </p>
            </div>
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1.5rem" }}>
              {/* Sección de Planificación de Metas */}
              <div className="planificador-card">
                <h3 style={{ fontSize: "1.125rem", fontWeight: "500", color: "#111827", marginBottom: "0.75rem" }}>
                  <i className="fas fa-bullseye" style={{ color: "#3b82f6", marginRight: "0.5rem" }}></i>
                  Metas Financieras
                </h3>
                <p style={{ color: "#4b5563", marginBottom: "1rem" }}>Define y haz seguimiento a tus objetivos económicos.</p>
                <button className="blue-button">
                  Crear Nueva Meta
                </button>
              </div>
              
              {/* Sección de Ahorro Programado */}
              <div className="planificador-card">
                <h3 style={{ fontSize: "1.125rem", fontWeight: "500", color: "#111827", marginBottom: "0.75rem" }}>
                  <i className="fas fa-piggy-bank" style={{ color: "#10b981", marginRight: "0.5rem" }}></i>
                  Ahorro Programado
                </h3>
                <p style={{ color: "#4b5563", marginBottom: "1rem" }}>Planifica tus ahorros mensuales y visualiza tu progreso.</p>
                <button className="green-button">
                  Configurar Plan de Ahorro
                </button>
              </div>
              
              {/* Sección de Proyección de Gastos */}
              <div className="planificador-card">
                <h3 style={{ fontSize: "1.125rem", fontWeight: "500", color: "#111827", marginBottom: "0.75rem" }}>
                  <i className="fas fa-chart-line" style={{ color: "#8b5cf6", marginRight: "0.5rem" }}></i>
                  Proyección de Gastos
                </h3>
                <p style={{ color: "#4b5563", marginBottom: "1rem" }}>Anticipa tus gastos futuros basado en el histórico.</p>
                <button className="purple-button">
                  Ver Proyecciones
                </button>
              </div>
              
              {/* Sección de Simulador de Escenarios */}
              <div className="planificador-card">
                <h3 style={{ fontSize: "1.125rem", fontWeight: "500", color: "#111827", marginBottom: "0.75rem" }}>
                  <i className="fas fa-calculator" style={{ color: "#d97706", marginRight: "0.5rem" }}></i>
                  Simulador Financiero
                </h3>
                <p style={{ color: "#4b5563", marginBottom: "1rem" }}>Simula diferentes escenarios para tomar mejores decisiones.</p>
                <button className="amber-button">
                  Iniciar Simulación
                </button>
              </div>
            </div>
            
            <div style={{ marginTop: "2rem", backgroundColor: "white", padding: "1.25rem", borderRadius: "0.5rem", border: "1px solid #e5e7eb", boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
              <h3 style={{ fontSize: "1.125rem", fontWeight: "500", color: "#111827", marginBottom: "1rem" }}>Calendario Financiero</h3>
              <div style={{ backgroundColor: "#f3f4f6", padding: "2.5rem", borderRadius: "0.375rem", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <p style={{ color: "#6b7280", textAlign: "center" }}>
                  <i className="fas fa-calendar-alt" style={{ color: "#9ca3af", fontSize: "2.25rem", display: "block", marginBottom: "0.75rem" }}></i>
                  Calendario de eventos financieros próximo a implementarse
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Planificador;
