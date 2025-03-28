import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function CategoryChart() {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      
      const ctx = chartRef.current.getContext('2d');
      
      chartInstance.current = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Comida', 'Transporte', 'Vivienda', 'Entretenimiento', 'Otros'],
          datasets: [{
            data: [30, 20, 35, 10, 5],
            backgroundColor: [
              'rgba(14, 165, 233, 0.7)',
              'rgba(245, 158, 11, 0.7)',
              'rgba(239, 68, 68, 0.7)',
              'rgba(16, 185, 129, 0.7)',
              'rgba(139, 92, 246, 0.7)',
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'right',
            },
            title: {
              display: true,
              text: 'Gastos por Categoría'
            }
          }
        }
      });
    }
    
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, []);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Distribución de Gastos</h3>
      <canvas ref={chartRef} height="250"></canvas>
    </div>
  );
}
