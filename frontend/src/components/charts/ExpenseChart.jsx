import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function ExpenseChart() {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      
      const ctx = chartRef.current.getContext('2d');
      
      chartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
          datasets: [
            {
              label: 'Ingresos',
              data: [1500, 1700, 1800, 1750, 1900, 2000, 2100, 2200, 2300, 2150, 2250, 2400],
              backgroundColor: 'rgba(14, 165, 233, 0.2)',
              borderColor: 'rgba(14, 165, 233, 1)',
              borderWidth: 2,
              tension: 0.3,
            },
            {
              label: 'Gastos',
              data: [1200, 1300, 1100, 1400, 1350, 1300, 1450, 1500, 1600, 1550, 1700, 1600],
              backgroundColor: 'rgba(239, 68, 68, 0.2)',
              borderColor: 'rgba(239, 68, 68, 1)',
              borderWidth: 2,
              tension: 0.3,
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: 'Ingresos vs Gastos (2023)'
            }
          },
          scales: {
            y: {
              beginAtZero: true
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
      <h3 className="text-lg font-semibold mb-4">Resumen Financiero</h3>
      <canvas ref={chartRef} height="250"></canvas>
    </div>
  );
}
