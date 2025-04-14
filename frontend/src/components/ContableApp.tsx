import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000'; 
// Remove the direct localStorage access at module level

interface Transaction {
  transaction_date: string;
  description: string;
  amount: number;
  type: string;
  user_bank_id: number;
  subcategory_id: number;
}

interface TransactionProcessed {
  Fecha: string;
  Descripción: string;
  Monto: number;
  Tipo: string;
  Cargo: number;
  Abono: number;
  user_bank_id: number;
  subcategory_id: number;
  subcategory_name: string;
  category_name: string;
  category_color: string;
  pattern_id: number | null;  // Add pattern_id field
  createdAt: string;
  updatedAt: string;
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
  transactions: TransactionProcessed[];
  transactions_count: number;
  ignored_count: number;
  categorized_count: number;
  uncategorized_count: number;
  ignored_transactions?: TransactionProcessed[];
  uncategorized_transactions?: TransactionProcessed[];
}

// Add a userId prop or use a default value (1 for demo)
export default function ContableApp() {
  const [user, setUser] = useState<{ id: number; name: string } | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [data, setData] = useState<TransactionProcessed[]>([]);
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
  const [showTable, setShowTable] = useState(false);
  // Add currentUser state
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [userId, setUserId] = useState<number>(1); // Default user ID
  const [userBanksData, setUserBanksData] = useState<GraphQLUserBank[]>([]); // Store user banks data
  const [isDragging, setIsDragging] = useState(false);
  const [reportStats, setReportStats] = useState<{
    transactions_count: number;
    ignored_count: number;
    categorized_count: number;
    uncategorized_count: number;
  } | null>(null);

  useEffect(() => {
    // Safe to access localStorage inside useEffect (client-side only)
    try {
      const userFromStorage = localStorage.getItem('currentUser');
      if (userFromStorage) {
        const parsedUser = JSON.parse(userFromStorage);
        setCurrentUser(parsedUser);
        if (parsedUser.id) {
          setUserId(parseInt(parsedUser.id)); // Ensure it's parsed as number
          console.log("User ID set from localStorage:", parsedUser.id);
        }
      }
    } catch (error) {
      console.error('Error accessing localStorage:', error);
    }
    
    // Move fetchBanks to a separate useEffect that depends on userId
    setLoading(false);
  }, []);

  // Add a new useEffect to fetch banks after userId is set from localStorage
  useEffect(() => {
    if (userId) {
      console.log("Fetching banks with user ID:", userId);
      fetchBanks();
    }
  }, [userId]);

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
      console.log("Using userId for API call:", userId);
      
      // Define GraphQL types for type safety
      interface GraphQLUserBank {
        id: number;
        userId: number;
        bankId: number;
        balance: number;
        description: string | null;
        patternNameFile?: string | null;
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
                patternNameFile
                createdAt
                updatedAt
              }
            }
          `,
          variables: {
            // Use the userId from state which is updated from localStorage in useEffect
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
      
      // Store the original user banks data for pattern matching later
      setUserBanksData(userBanks);
      
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
      
      setBanks(enhancedBanks);
      
    } catch (err) {
      console.error('Error fetching user banks:', err);
    } finally {
      setLoadingBanks(false);
    }
  };

  const processFileUpload = async (selectedFile: File) => {
    if (!selectedFile) {
      setUploadStatus('Por favor selecciona un archivo');
      return;
    }
  
    setUploadStatus('Subiendo reporte...');
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', userId.toString() || '');
  
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
      console.log('>>>>>>>>Processed report:', result);
      setData(result.transactions);
      setBalance(result.balance);
      setSelectedBankId(result.bank_id);
      
      // Store report statistics
      setReportStats({
        transactions_count: result.transactions_count || 0,
        ignored_count: result.ignored_count || 0,
        categorized_count: result.categorized_count || 0,
        uncategorized_count: result.uncategorized_count || 0
      });
      
      // Mostrar tabla cuando hay datos del reporte
      setShowTable(result.transactions.length > 0);
  
      // Limpiar el input file
      setFile(null);
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err: any) {
      setUploadStatus(`Error: ${err.message}`);
    }
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      console.log('File selected:', selectedFile);
      setFile(selectedFile);
      setUploadStatus(null);
      
      // Auto-select bank based on filename pattern matching
      autoSelectBankByFileName(selectedFile.name);
      
      // Process the file after selection
      processFileUpload(selectedFile);
    }
  };

  // New dedicated function for auto-selecting bank based on file name
  const autoSelectBankByFileName = (fileName: string) => {
    if (!fileName || !userBanksData || userBanksData.length === 0) return;
    
    fileName = fileName.toLowerCase();
    console.log('Checking if filename matches any bank patterns:', fileName);
    
    // Look for banks with matching pattern_name_file
    const matchedBank = userBanksData.find(userBank => {
      if (!userBank.patternNameFile) return false;
      
      const pattern = userBank.patternNameFile.toLowerCase();
      const isMatch = fileName.includes(pattern);
      
      if (isMatch) {
        console.log(`File name "${fileName}" matches pattern "${pattern}" for bank ID ${userBank.bankId}`);
      }
      
      return isMatch;
    });
    
    if (matchedBank) {
      // Find the corresponding bank in the banks array to get its name
      const bankInfo = banks.find(bank => bank.id === matchedBank.bankId);
      const bankName = bankInfo?.name || `Banco ID: ${matchedBank.bankId}`;
      
      // Select this bank
      console.log(`Auto-selecting bank: ${bankName} (ID: ${matchedBank.bankId})`);
      setSelectedBank(matchedBank.bankId.toString());
      
      // Show notification to user with more details
      setUploadStatus(`Banco ${bankName} seleccionado automáticamente por coincidencia con el patrón "${matchedBank.patternNameFile}"`);
    } else {
      console.log('No bank pattern matches the filename');
      // Clear selected bank if no match is found
      setSelectedBank('');
      setUploadStatus('No se pudo identificar el banco automáticamente. Por favor, sube un archivo con un nombre que coincida con algún patrón configurado.');
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
      // Find the selected bank object
      const selectedBankObj = banks.find(b => b.id.toString() === selectedBank);
      
      if (!selectedBankObj) {
        setSaveStatus('Error: No se ha seleccionado un banco automáticamente. Por favor, sube un archivo cuyo nombre coincida con un patrón configurado.');
        setSavingTransactions(false);
        return;
      }
      
      // Format transactions according to the bulk-transactions endpoint requirements
      const transactionsToSave = data.map(item => {
        const {
          Fecha,
          Descripción,
          Monto,
          Tipo,
          Cargo,
          Abono,
          subcategory_id = -1, // Default to -1 if not specified
          pattern_id = null,   // Include pattern_id, default to null if not specified
        } = item;
        
        // Format the date to YYYY-MM-DD format for the API
        const formattedDate = formatDateForAPI(Fecha);
        
        // Create the transaction object with all required fields
        const transaction = {
          transaction_date: formattedDate,
          description: Descripción,
          amount: Monto || Cargo || Abono || 0,
          type: Tipo || "Gasto", // Default to "Gasto" if not specified
          user_bank_id: selectedBankObj.userBankId || selectedBankObj.id,
          subcategory_id
        };
        
        // Add pattern_id only if it exists
        if (pattern_id !== null) {
          transaction.pattern_id = pattern_id;
        }
        
        return transaction;
      });
      
      console.log('Saving transactions:', transactionsToSave);
  
      // Send the transactions to the backend
      const response = await fetch(`${API_URL}/api/v1/transactions/bulk-transactions`, {
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
      setSaveStatus(`Transacciones guardadas: ${result.inserted_count} de ${result.total_processed} (${result.duplicates_count} duplicadas)`);
      
      // Clear the table after successfully saving if any were inserted
      if (result.inserted_count > 0) {
        setData([]);
        setShowTable(false);
        setBalance(null);
        
        // Optional: refresh banks to show updated balances
        fetchBanks();
      }
    } catch (err: any) {
      setSaveStatus(`Error: ${err.message}`);
      console.error('Error saving transactions:', err);
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

  // Update countUncategorizedTransactions to be more reliable
  const countUncategorizedTransactions = data.filter(item => 
    !item.category_name || 
    item.category_name === "Sin categoría" || 
    item.subcategory_id === -1
  ).length;
  
  // Check if saving should be disabled due to uncategorized transactions
  const hasSaveDisabled = countUncategorizedTransactions > 0;

  // Handle drag events for file upload
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      console.log('File dropped:', droppedFile);
      setFile(droppedFile);
      
      // Auto-select bank based on filename pattern matching
      autoSelectBankByFileName(droppedFile.name);
      
      // Process the file after selection
      processFileUpload(droppedFile);
    }
  };

  if (loading) return <div className="loading-container">Cargando datos...</div>;
  if (error) return <div className="error-container">Error: {error}</div>;

  return (
    <div className="contable-app">
      <div className="upload-section">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Subir Reporte Bancario</h2>
        <p className="text-sm text-gray-600 mb-4">
          Sube el archivo de tu banco para procesar las transacciones. El banco será detectado automáticamente según el nombre del archivo.
        </p>
        <form id="upload-form" className="space-y-4">
          <div className="form-row flex flex-col md:flex-row gap-4">
            <div className="form-group flex-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Banco: {selectedBank && <span className="text-emerald-600 font-medium">(Auto-detectado)</span>}
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {loadingBanks ? (
                  <p className="text-gray-500">Cargando bancos...</p>
                ) : (
                  banks.map(bank => {
                    // Find the corresponding userBank to show pattern info
                    const userBank = userBanksData.find(ub => ub.bankId === bank.id);
                    const hasPattern = userBank && userBank.patternNameFile;
                    const isSelected = selectedBank === bank.id.toString();
                    
                    return (
                      <div 
                        key={bank.id} 
                        className={`bank-option p-4 border rounded-lg shadow-sm cursor-not-allowed ${
                          isSelected
                            ? 'border-emerald-500 bg-emerald-50 ring-2 ring-emerald-500 ring-opacity-50' 
                            : hasPattern 
                              ? 'border-blue-200 bg-blue-50' 
                              : 'border-gray-200 bg-gray-50 opacity-60'
                        }`}
                      >
                        <h3 className={`text-sm font-medium ${isSelected ? 'text-emerald-800' : 'text-gray-800'}`}>
                          {bank.name}
                          {isSelected && <span className="ml-2 text-xs text-emerald-600">✓ Seleccionado</span>}
                          {hasPattern && !isSelected && <span className="ml-1 text-xs text-blue-500">Auto-detectable</span>}
                        </h3>
                        {bank.balance && (
                          <p className={`text-sm ${isSelected ? 'text-emerald-700' : 'text-gray-600'}`}>
                            Saldo: {formatAmount(bank.balance)}
                          </p>
                        )}
                        {hasPattern && (
                          <p className={`text-xs mt-1 truncate ${isSelected ? 'text-emerald-600' : 'text-blue-500'}`} title={userBank.patternNameFile}>
                            Patrón: {userBank.patternNameFile}
                          </p>
                        )}
                        {!hasPattern && (
                          <p className="text-xs text-gray-400 mt-1">
                            Sin patrón de detección
                          </p>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
              {!selectedBank && !loadingBanks && (
                <p className="text-sm text-amber-600 mt-2 font-medium">
                  El banco será seleccionado automáticamente al subir un archivo que coincida con algún patrón.
                </p>
              )}
            </div>
            
            <div className="form-group flex-1">
              <label htmlFor="file-input" className="block text-sm font-medium text-gray-700 mb-1">Archivo de Reporte:</label>
              <div 
                className={`drag-drop-area relative p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-all ${
                  isDragging 
                    ? 'border-emerald-500 bg-emerald-50' 
                    : 'border-gray-300 hover:border-emerald-300 hover:bg-gray-50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
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
                  className="cursor-pointer flex flex-col items-center"
                >
                  <svg 
                    className={`w-10 h-10 mb-2 ${isDragging ? 'text-emerald-500' : 'text-gray-400'}`} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24" 
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  {file ? (
                    <div className="mt-2 text-sm font-medium text-gray-900">
                      {file.name}
                    </div>
                  ) : (
                    <>
                      <p className="text-sm font-medium text-gray-900">
                        {isDragging ? 'Suelta el archivo aquí' : 'Arrastra y suelta un archivo'}
                      </p>
                      <p className="mt-1 text-xs text-gray-500">
                        o haz clic para seleccionar
                      </p>
                    </>
                  )}
                </label>
              </div>
              <p className="text-sm text-gray-500 mt-1">Formatos soportados: .csv, .xls, .xlsx, .pdf</p>
            </div>
          </div>
        </form>
        
        {uploadStatus && (
          <div 
            className={`mt-4 p-3 rounded-lg text-sm font-medium ${
              uploadStatus.includes('Error') || uploadStatus.includes('No se pudo') 
                ? 'bg-amber-100 text-amber-700 border-l-4 border-amber-500' 
                : uploadStatus.includes('seleccionado automáticamente') 
                  ? 'bg-emerald-100 text-emerald-700 border-l-4 border-emerald-500'
                  : 'bg-blue-100 text-blue-700'
            }`}
          >
            {uploadStatus}
          </div>
        )}
      </div>
      
      {balance !== null && (
        <div className="balance-info">
          <h3 className="font-semibold text-lg mb-2">Información del Reporte</h3>
          
          {reportStats && (
            <div className="stats-container">
              <div className="stat-card">
                <div className="stat-value">{reportStats.transactions_count}</div>
                <div className="stat-label">Encontradas</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-value text-emerald-600">{reportStats.categorized_count}</div>
                <div className="stat-label">Categorizadas</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-value text-red-600">{reportStats.uncategorized_count}</div>
                <div className="stat-label">Sin categorizar</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-value text-amber-600">{reportStats.ignored_count}</div>
                <div className="stat-label">Ignoradas</div>
              </div>
              
             
            </div>
          )}
        </div>
      )}

      {showTable && data.length > 0 && (
        <>
          <div className="transactions-header">
            <h2>Transacciones</h2>
            <div className="flex items-center">
              {hasSaveDisabled && (
                <div className="save-warning mr-4">
                  <svg className="inline-block w-5 h-5 mr-1 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span className="text-sm text-amber-700">
                    {countUncategorizedTransactions} transacción{countUncategorizedTransactions !== 1 ? 'es' : ''} sin categoría
                  </span>
                </div>
              )}
              <button 
                onClick={handleSaveTransactions} 
                disabled={savingTransactions || hasSaveDisabled}
                className="save-button"
                title={hasSaveDisabled ? "Clasifica todas las transacciones antes de guardar" : ""}
              >
                {savingTransactions ? 'Guardando...' : 'Guardar en Base de Datos'}
              </button>
            </div>
          </div>
          
          {saveStatus && (
            <div className={`save-status ${saveStatus.includes('Error') ? 'error' : 'success'}`}>
              {saveStatus}
            </div>
          )}
          
          {hasSaveDisabled && (
            <div className="save-status warning">
              <p className="font-medium">No se pueden guardar transacciones sin categoría</p>
              <p className="text-sm mt-1">Por favor, clasifica todas las transacciones para continuar.</p>
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
              {data.map((item, index) => {
                // Determine if item is uncategorized
                const isUncategorized = !item.category_name || 
                  item.category_name === "Sin categoría" || 
                  item.subcategory_id === -1;
                
                return (
                  <tr 
                    key={index} 
                    className={`${item.Tipo?.toLowerCase() || ''} ${isUncategorized ? 'uncategorized-row' : ''}`}
                    style={{
                      borderLeft: item.category_color 
                        ? `4px solid ${item.category_color}` 
                        : 'none'
                    }}
                  >
                    <td>{item.Fecha}</td>
                    <td>{item.Descripción}</td>
                    <td>{formatAmount(item.Monto || item.Cargo || item.Abono)}</td>
                    <td>{item.Tipo || "-"}</td>
                    <td>
                      <span className="category-tag" style={{ 
                        backgroundColor: item.category_color || getCategoryColor(item.category_name || "Sin categoría"),
                        color: item.category_name === 'Sin categoría' ? '#FF0000' : 'black'
                      }}>
                        {item.category_name || "Sin categoría"}
                        {isUncategorized && 
                          <svg className="inline-block w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        }
                      </span>
                    </td>
                    <td>{item.subcategory_name || "Sin subcategoría"}</td>
                  </tr>
                );
              })}
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
          opacity: 0.7;
        }
        
        .save-status {
          margin: 0.5rem 0 1rem;
          padding: 0.75rem 1rem;
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
        
        .save-status.warning {
          background-color: #fff8e1;
          border-left: 4px solid #ffc107;
          color: #f57c00;
        }
        
        .save-warning {
          display: flex;
          align-items: center;
          color: #f57c00;
        }
        
        .uncategorized-row {
          background-color: rgba(255, 193, 7, 0.05);
        }
        
        .uncategorized-row:hover {
          background-color: rgba(255, 193, 7, 0.1);
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
          background-color: #f0f9ff;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1.5rem;
          border-left: 4px solid #0ea5e9;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        .stats-container {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
          gap: 0.75rem;
          margin-top: 0.5rem;
        }
        
        .stat-card {
          background: white;
          border-radius: 6px;
          padding: 0.75rem;
          text-align: center;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
          transition: transform 0.2s;
        }
        
        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .stat-value {
          font-size: 1.25rem;
          font-weight: 700;
          line-height: 1.2;
          margin-bottom: 0.25rem;
        }
        
        .stat-label {
          font-size: 0.75rem;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 0.05em;
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

        .drag-drop-area {
          min-height: 8rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          transition: all 0.2s ease;
        }
        
        .drag-drop-area:hover {
          border-color: #4a66d8;
          background-color: #f8fafc;
        }

        .bank-option {
          transition: all 0.2s ease-in-out;
          position: relative;
        }
        
        .bank-option.opacity-60:after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255,255,255,0.5);
          border-radius: 0.5rem;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 0.5rem;
        }
        
        .stat-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.25rem 0;
        }
        
        .stat-label {
          font-weight: 500;
        }
        
        .stat-value {
          font-weight: 600;
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

// Add this utility function at the top level of the file, before the ContableApp component
function formatDateForAPI(dateString: string): string {
  // Handle different date formats that might come from bank reports
  try {
    // Try to parse the date
    const dateParts = dateString.split(/[-/.]/);
    
    // Check if the date is in DD-MM-YYYY or similar format
    if (dateParts.length === 3) {
      // If first part is likely a day (1-31) and third part is likely a year (>= 1000)
      if (parseInt(dateParts[0]) <= 31 && parseInt(dateParts[2]) >= 1000) {
        // Convert DD-MM-YYYY to YYYY-MM-DD
        return `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`;
      } 
      // If already in YYYY-MM-DD format
      else if (parseInt(dateParts[0]) >= 1000 && parseInt(dateParts[2]) <= 31) {
        // Just ensure proper padding
        return `${dateParts[0]}-${dateParts[1].padStart(2, '0')}-${dateParts[2].padStart(2, '0')}`;
      }
    }
    
    // If no specific format detected or parsing failed, try creating a date object
    const date = new Date(dateString);
    if (!isNaN(date.getTime())) {
      // Format as YYYY-MM-DD
      return date.toISOString().split('T')[0];
    }

    // If all else fails, return the original string
    return dateString;
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateString;
  }
}
