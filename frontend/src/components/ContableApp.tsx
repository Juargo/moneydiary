import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000'; 

interface Transaction {
  date: string;
  description: string;
  category?: string;
  amount?: number;
  Fecha?: string;
  Descripción?: string;
  Cargo?: number;
  Abono?: number;
  Monto?: number;
  Tipo?: string;
  "N° Operación"?: string;
  // Add new categorization fields
  category_id?: number | null;
  category_name?: string;
  subcategory_id?: number | null;
  subcategory_name?: string;
  category_color?: string;
}

interface Bank {
  id: number;
  name: string;
  description: string;
  code?: string;
}

interface BankReport {
  bank_id: number;
  balance: number;
  transactions: Transaction[];
}

// Add a userId prop or use a default value (1 for demo)
export default function ContableApp({ userId = 1 }) {
  const [data, setData] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [selectedBank, setSelectedBank] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loadingBanks, setLoadingBanks] = useState(true);
  const [balance, setBalance] = useState<number | null>(null);
  const [selectedBankId, setSelectedBankId] = useState<number | null>(null);
  const [savingTransactions, setSavingTransactions] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false); // Nuevo estado para controlar la visibilidad de la tabla

  useEffect(() => {
    // No cargar transacciones al iniciar, solo bancos
    // fetchTransactions();
    fetchBanks();
    setLoading(false); // Indicar que la carga inicial ha terminado
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/transactions`);
      if (!response.ok) {
        throw new Error('Error al cargar los datos');
      }
      const data = await response.json();
      setData(data);
      
      // Solo mostrar la tabla si hay datos
      setShowTable(data.length > 0);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchBanks = async () => {
    try {
      setLoadingBanks(true);
      
      // Define GraphQL types for type safety
      interface GraphQLUserBank {
        id: number;
        userId: number;
        bankId: number;
        balance: number;
        description: string | null;
        createdAt: string;
        updatedAt: string;
      }

      interface GraphQLBank {
        id: number;
        name: string;
        createdAt: string;
        updatedAt: string;
      }

      // First, fetch all available banks to have their names/info
      const banksResponse = await fetch(`${API_URL}/graphql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `
            query {
              banks {
                id
                name
                createdAt
                updatedAt
              }
            }
          `
        }),
      });
      
      if (!banksResponse.ok) {
        throw new Error('Error al cargar los bancos');
      }
      
      const banksResult = await banksResponse.json();
      const allBanks: GraphQLBank[] = banksResult.data.banks;
      
      // Then fetch user banks to get the balances and relationships
      const userBanksResponse = await fetch(`${API_URL}/graphql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `
            query GetUserBanks($userId: Int!) {
              userBanks(userId: $userId) {
                id
                userId
                bankId
                balance
                description
                createdAt
                updatedAt
              }
            }
          `,
          variables: {
            userId: userId
          }
        }),
      });

      if (!userBanksResponse.ok) {
        throw new Error('Error al cargar los bancos del usuario');
      }

      const userBanksResult = await userBanksResponse.json();
      
      if (userBanksResult.errors) {
        throw new Error(userBanksResult.errors[0].message);
      }
      
      const userBanks: GraphQLUserBank[] = userBanksResult.data.userBanks;
      
      // Map user banks to the format needed by the component
      const enhancedBanks = userBanks.map(userBank => {
        // Find the bank details from the all banks list
        const bankInfo = allBanks.find(b => b.id === userBank.bankId);
        
        if (!bankInfo) {
          console.warn(`No se encontró información para el banco con ID ${userBank.bankId}`);
        }
        
        return {
          id: userBank.bankId,
          name: bankInfo ? bankInfo.name : `Banco ID: ${userBank.bankId}`,
          description: userBank.description || (bankInfo ? bankInfo.name : `Banco ID: ${userBank.bankId}`),
          balance: userBank.balance,
          userBankId: userBank.id,
          createdAt: userBank.createdAt,
          updatedAt: userBank.updatedAt
        };
      });
      
      console.log('Bancos cargados:', enhancedBanks);
      setBanks(enhancedBanks);
      
    } catch (err) {
      console.error('Error fetching user banks:', err);
    } finally {
      setLoadingBanks(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleBankChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedBank(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!file || !selectedBank) {
      setUploadStatus('Por favor selecciona un archivo y un banco');
      return;
    }

    setUploadStatus('Subiendo reporte...');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank_id', selectedBank);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/transactions/upload-bank-report`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar el archivo');
      }

      const result: BankReport = await response.json();
      setUploadStatus('Reporte procesado correctamente');
      
      // Actualiza el estado con los datos del reporte
      setData(result.transactions);
      setBalance(result.balance);
      setSelectedBankId(result.bank_id);
      setFile(null);
      
      // Mostrar tabla cuando hay datos del reporte
      setShowTable(result.transactions.length > 0);

      // Resetear el formulario
      const form = document.getElementById('upload-form') as HTMLFormElement;
      if (form) form.reset();
    } catch (err: any) {
      setUploadStatus(`Error: ${err.message}`);
    }
  };

  const handleSaveTransactions = async () => {
    if (!data.length) {
      setSaveStatus('No hay transacciones para guardar');
      return;
    }

    setSavingTransactions(true);
    setSaveStatus('Guardando transacciones...');

    try {
      // Convertir el formato de las transacciones para el endpoint bulk-transactions
      const transactionsToSave = data.map(item => {
        // Determinar el tipo (Ingreso/Gasto) de la transacción
        const tipo = item.Tipo || 'Gasto'; // Por defecto es gasto si no se especifica
        
        // Obtener el monto de la transacción
        let monto;
        if (item.Monto !== undefined) {
          monto = item.Monto;
        } else if (item.amount !== undefined) {
          monto = item.amount;
        } else if (tipo === 'Ingreso') {
          monto = item.Abono || 0;
        } else {
          monto = item.Cargo || 0;
        }
        
        // Ajustar el signo del monto según el tipo
        // Para gastos: valores negativos, para ingresos: valores positivos
        const montoAjustado = tipo === 'Gasto' 
          ? -Math.abs(Number(monto)) 
          : Math.abs(Number(monto));
        
        console.log(`Procesando transacción: ${item.Descripción || item.description}, Tipo: ${tipo}, Monto: ${montoAjustado}`);
        
        return {
          fecha: item.Fecha || item.date,
          descripcion: item.Descripción || item.description,
          monto: montoAjustado,
          categoria: "Sin clasificar",
          banco_id: banks.find(b => b.name === selectedBank)?.id,
          tipo: tipo
        };
      });

      // Verificar que hay transacciones para guardar
      if (transactionsToSave.length === 0) {
        setSaveStatus('No hay transacciones válidas para guardar');
        return;
      }

      const response = await fetch(`${API_URL}/bulk-transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionsToSave),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar las transacciones');
      }

      const result = await response.json();
      setSaveStatus(`Transacciones guardadas: ${result.insertadas} de ${result.total_recibidas} (${result.duplicadas} duplicadas)`);
      
      // Opcional: Limpiar la tabla después de guardar exitosamente
      if (result.insertadas > 0) {
        setData([]);
        setShowTable(false);
        setBalance(null);
      }
    } catch (err: any) {
      setSaveStatus(`Error: ${err.message}`);
    } finally {
      setSavingTransactions(false);
    }
  };

  // Formatear los montos en CLP
  const formatAmount = (amount: number | undefined) => {
    if (amount === undefined) return "-";
    return amount.toLocaleString('es-CL', { 
      style: 'currency', 
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  const countUncategorizedTransactions = data.filter(item => !item.category_name || item.category_name === "Sin categoría").length;

  if (loading) return <div className="loading-container">Cargando datos...</div>;
  if (error) return <div className="error-container">Error: {error}</div>;

  return (
    <div className="contable-app">
      <div className="upload-section">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Subir Reporte Bancario</h2>
        <p className="text-sm text-gray-600 mb-4">
          Sube un archivo de tu banco para procesar las transacciones. Asegúrate de seleccionar el banco correcto y un archivo válido.
        </p>
        <form id="upload-form" onSubmit={handleSubmit} className="space-y-4">
          <div className="form-row flex flex-col md:flex-row gap-4">
            <div className="form-group flex-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Seleccionar Banco:</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {loadingBanks ? (
                  <p className="text-gray-500">Cargando bancos...</p>
                ) : (
                  banks.map(bank => (
                    <div 
                      key={bank.id} 
                      className={`bank-option p-4 border rounded-lg cursor-pointer shadow-sm ${
                        selectedBank === bank.id.toString() ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
                      }`}
                      onClick={() => setSelectedBank(bank.id.toString())}
                    >
                      <h3 className="text-sm font-medium text-gray-800">{bank.name}</h3>
                      {bank.balance && (
                        <p className="text-sm text-gray-600">Saldo: {formatAmount(bank.balance)}</p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
            
            <div className="form-group flex-1">
              <label htmlFor="file-input" className="block text-sm font-medium text-gray-700 mb-1">Archivo de Reporte:</label>
              <div className="relative">
                <input 
                  id="file-input"
                  type="file" 
                  onChange={handleFileChange}
                  accept=".csv,.xls,.xlsx,.pdf"
                  required
                  className="hidden"
                />
                <label 
                  htmlFor="file-input" 
                  className="block w-full cursor-pointer rounded-md border border-gray-300 bg-white py-2 px-4 text-sm text-gray-700 shadow-sm hover:bg-gray-50 focus-within:ring focus-within:ring-primary-200 focus-within:ring-opacity-50"
                >
                  {file ? file.name : "Seleccionar archivo"}
                </label>
              </div>
              <p className="text-sm text-gray-500 mt-1">Formatos soportados: .csv, .xls, .xlsx, .pdf</p>
            </div>
          </div>
          
          <button 
            type="submit" 
            className="w-full bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg font-medium transition"
          >
            Procesar Reporte
          </button>
        </form>
        
        {uploadStatus && (
          <div 
            className={`mt-4 p-3 rounded-lg text-sm font-medium ${
              uploadStatus.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
            }`}
          >
            {uploadStatus}
          </div>
        )}
      </div>
      
      {balance !== null && (
        <div className="balance-info">
          <h3>Información del Reporte</h3>
          <p>Banco: {banks.find(b => b.id === selectedBankId)?.name || `ID: ${selectedBankId}`}</p>
          <p>Saldo: {formatAmount(balance)}</p>
          <p>Transacciones sin categoría: {countUncategorizedTransactions}</p>
        </div>
      )}
      
      {showTable && data.length > 0 && (
        <>
          <div className="transactions-header">
            <h2>Transacciones</h2>
            <button 
              onClick={handleSaveTransactions} 
              disabled={savingTransactions}
              className="save-button"
            >
              {savingTransactions ? 'Guardando...' : 'Guardar en Base de Datos'}
            </button>
          </div>
          
          {saveStatus && (
            <div className={`save-status ${saveStatus.includes('Error') ? 'error' : 'success'}`}>
              {saveStatus}
            </div>
          )}
          
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Monto</th>
                <th>Tipo</th>
                <th>Categoría</th>
                <th>Subcategoría</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr 
                  key={index} 
                  className={item.Tipo?.toLowerCase() || ''}
                  style={{
                    borderLeft: item.category_color 
                      ? `4px solid ${item.category_color}` 
                      : 'none'
                  }}
                >
                  <td>{item.Fecha || item.date}</td>
                  <td>{item.Descripción || item.description}</td>
                  <td>{formatAmount(item.Monto || item.amount || item.Cargo || item.Abono)}</td>
                  <td>{item.Tipo || "-"}</td>
                  <td>
                    <span className="category-tag" style={{ 
                      backgroundColor: item.category_color || getCategoryColor(item.category_name || "Sin categoría"),
                      color: item.category_name ==='Sin categoría'? '#FF0000' :'black'// Red color for "Sin categoría"
                    }}>
                      {item.category_name || "Sin categoría"}
                    </span>
                  </td>
                  <td>{item.subcategory_name || "Sin subcategoría"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      
      {!showTable && !uploadStatus && (
        <div className="info-message">
          <p>Selecciona un banco y sube un archivo para procesar transacciones.</p>
        </div>
      )}
      
      <style>{`
        .upload-section {
          background-color: #f9fafb;
          padding: 1.5rem;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
          margin-bottom: 2rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          font-weight: 600;
        }

        .form-group input, .form-group select {
          padding: 0.5rem;
          border-radius: 4px;
          border: 1px solid #d1d5db;
          transition: border-color 0.2s;
        }

        .form-group input:focus, .form-group select:focus {
          border-color: #4a66d8;
          outline: none;
        }

        .form-group p {
          font-size: 0.875rem;
          color: #6b7280;
        }

        button {
          font-weight: 600;
        }

        .transactions-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .save-button {
          background-color: #4caf50;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          font-weight: bold;
          transition: background-color 0.2s;
        }
        
        .save-button:hover {
          background-color: #388e3c;
        }
        
        .save-button:disabled {
          background-color: #a5d6a7;
          cursor: not-allowed;
        }
        
        .save-status {
          margin: 0.5rem 0 1rem;
          padding: 0.5rem;
          border-radius: 4px;
        }
        
        .save-status.success {
          background-color: #e8f5e9;
          border-left: 4px solid #4caf50;
        }
        
        .save-status.error {
          background-color: #ffebee;
          border-left: 4px solid #f44336;
          color: #c62828;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 1rem;
          font-size: 0.9rem;
        }
        
        th, td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }
        
        th {
          background-color: #f5f5f5;
          font-weight: bold;
        }
        
        tr:hover {
          background-color: #f5f5f5;
        }

        .balance-info {
          background-color: #e3f2fd;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1.5rem;
          border-left: 4px solid #2196f3;
        }
        
        tr.ingreso {
          background-color: rgba(76, 175, 80, 0.1);
        }
        
        tr.ingreso:hover {
          background-color: rgba(76, 175, 80, 0.2);
        }
        
        tr.gasto {
          background-color: rgba(244, 67, 54, 0.05);
        }
        
        tr.gasto:hover {
          background-color: rgba(244, 67, 54, 0.1);
        }

        .loading-container, 
        .error-container,
        .info-message {
          padding: 2rem;
          text-align: center;
          background-color: #f5f5f5;
          border-radius: 8px;
          margin-top: 1rem;
        }

        .error-container {
          background-color: #ffebee;
          color: #c62828;
        }

        .info-message {
          background-color: #e3f2fd;
          color: #1565c0;
          padding: 2rem;
          font-weight: 500;
          border-left: 4px solid #1976d2;
        }

        .category-tag {
          display: inline-block;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.85rem;
          font-weight: 500;
          white-space: nowrap;
        }
        
        td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #ddd;
          vertical-align: middle;
        }
        
        tr {
          transition: background-color 0.2s;
          border-left: 4px solid transparent;
        }

        .form-row {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .form-group label {
          font-weight: 600;
        }

        .form-group input[type="file"] + label {
          display: inline-block;
          text-align: center;
        }

        .form-group input[type="file"]:focus + label {
          outline: 2px solid #4a66d8;
          outline-offset: 2px;
        }

        .form-group.flex-2 {
          flex: 2;
        }

        .form-group.flex-1 {
          flex: 1;
        }

        .bank-option {
          transition: all 0.2s ease-in-out;
        }

        .bank-option:hover {
          border-color: #4a66d8;
          background-color: #f0f4ff;
        }
      `}</style>
    </div>
  );
}

// Add this utility function for determining text color based on background
function getContrastColor(hexColor: string) {
  // Remove the leading # if it exists
  const hex = hexColor.replace('#', '');
  
  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  
  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  // Return black for bright colors, white for dark colors
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

// Add this utility function to determine a color based on the category name
function getCategoryColor(categoryName: string): string {
  const colors: Record<string, string> = {
    "Alimentos": "#FF5733",
    "Transporte": "#33FF57",
    "Entretenimiento": "#3357FF",
    "Sin categoría": "#CCCCCC",
    // Add more categories and their corresponding colors as needed
  };
  return colors[categoryName] || "#CCCCCC"; // Default to gray if no match
}
