<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

// Estado
const authStore = useAuthStore();
const banks = ref([]);
const accountTypes = ref([]);
const saving = ref(false);
const error = ref(null);

// Formulario
const form = reactive({
  name: "",
  account_number: "",
  bank_id: "",
  account_type_id: "",
  current_balance: 0,
  active: true,
});

// GraphQL query para obtener los bancos
const GET_BANKS_QUERY = `
  query GetBanks($activeOnly: Boolean = true) {
    banks(activeOnly: $activeOnly) {
      id
      name
      code
      logoUrl
      active
      description
      createdAt
      updatedAt
    }
  }
`;

// Función para realizar una consulta GraphQL
async function graphqlRequest(query, variables = {}) {
  const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

  const response = await fetch(`${apiUrl}/graphql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authStore.accessToken}`,
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();

  // Verificar si hay errores de GraphQL
  if (data.errors) {
    throw new Error(data.errors[0]?.message || "Error en la consulta GraphQL");
  }

  return data.data;
}

// Obtener bancos usando GraphQL
async function fetchBanks() {
  try {
    // Realizar consulta GraphQL para obtener bancos activos
    const data = await graphqlRequest(GET_BANKS_QUERY, { activeOnly: true });
    banks.value = data.banks || [];
  } catch (err) {
    console.error("Error al cargar bancos:", err);

    // Manejar errores de autenticación
    if (
      err.message.includes("401") ||
      err.message.includes("Credenciales inválidas")
    ) {
      const refreshed = await authStore.refreshAuthToken();
      if (refreshed) {
        return fetchBanks(); // Reintentar con el nuevo token
      } else {
        window.location.href = "/auth/login?returnTo=/dashboard/accounts/new";
        return;
      }
    }

    error.value = "No se pudieron cargar los bancos disponibles.";
  }
}

async function fetchAccountTypes() {
  try {
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(`${apiUrl}/api/v1/account-types`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error(
        `Error al obtener tipos de cuenta: ${response.statusText}`
      );
    }

    const data = await response.json();
    accountTypes.value = data.items || data;
  } catch (err) {
    console.error("Error al cargar tipos de cuenta:", err);
    error.value = "No se pudieron cargar los tipos de cuenta disponibles.";
  }
}

// Crear nueva cuenta
async function createAccount() {
  saving.value = true;
  error.value = null;

  try {
    // Si no hay token de acceso, redirigir al login
    if (!authStore.accessToken) {
      window.location.href = "/auth/login?returnTo=/dashboard/accounts/new";
      return;
    }

    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

    const response = await fetch(`${apiUrl}/api/v1/accounts`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expirado, intentar refresh
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          // Reintentar con el nuevo token
          return await createAccount();
        } else {
          throw new Error(
            "Sesión expirada. Por favor, inicia sesión nuevamente."
          );
        }
      }

      const errorData = await response.json();
      throw new Error(
        errorData.message || `Error al crear cuenta: ${response.statusText}`
      );
    }

    const newAccount = await response.json();

    // Redirigir a la página de la cuenta recién creada
    window.location.href = `/dashboard/accounts/${newAccount.id}`;
  } catch (err) {
    console.error("Error al crear cuenta:", err);
    error.value =
      err.message ||
      "No se pudo crear la cuenta. Por favor, intenta nuevamente.";
    alert(error.value);
  } finally {
    saving.value = false;
  }
}

// Inicializar
onMounted(async () => {
  // Si no hay token de acceso, redirigir al login
  if (!authStore.accessToken) {
    window.location.href = "/auth/login?returnTo=/dashboard/accounts/new";
    return;
  }

  // Cargar datos para los selectores
  await Promise.all([fetchBanks(), fetchAccountTypes()]);
});
</script>
