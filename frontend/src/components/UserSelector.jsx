import { useState, useEffect } from 'react';

export default function UserSelector() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        // Usamos la variable de entorno para la URL del backend
        const backendUrl = import.meta.env.PUBLIC_BACKEND_URL || 'http://localhost:8000';
        const graphqlEndpoint = `${backendUrl}/graphql`;
        
        console.log('Conectando a:', graphqlEndpoint); // Para depuración
        
        const response = await fetch(graphqlEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: `
              query {
                users {
                  id
                  username
                  createdAt
                  updatedAt
                }
              }
            `
          }),
        });

        const result = await response.json();
        
        if (result.errors) {
          throw new Error(result.errors[0].message);
        }
        
        setUsers(result.data.users);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleUserSelect = (user) => {
    localStorage.setItem('currentUser', JSON.stringify(user));
    window.location.href = '/';
  };
  

  if (loading) return (
    <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  );

  if (error) return (
    <div className="flex justify-center items-center h-screen">
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>Error al cargar usuarios: {error}</p>
      </div>
    </div>
  );

  return (
    <div className="bg-white p-8 rounded-lg shadow-lg max-w-md mx-auto mt-20">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Selecciona un usuario</h2>
      <p className="text-gray-600 mb-6 text-center">Escoge un usuario para continuar a MoneyDiary</p>
      
      <div className="space-y-3">
        {users.map(user => (
          <button
            key={user.id}
            onClick={() => handleUserSelect(user)}
            className="w-full py-3 px-4 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-between transition-colors"
          >
            <div className="flex items-center">
              <div className="bg-blue-100 text-blue-800 h-10 w-10 rounded-full flex items-center justify-center font-bold">
                {user.username.substring(0, 2).toUpperCase()}
              </div>
              <span className="ml-3 font-medium text-gray-800">{user.username}</span>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </button>
        ))}
      </div>
    </div>
  );
}
