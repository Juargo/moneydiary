<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../../stores/authStore";

// Props - ID de la cuenta a mostrar/editar
const props = defineProps({
  accountId: {
    type: String,
    required: true,
  },
});

// Estado
const authStore = useAuthStore();
const loading = ref(true);
const error = ref(null);
const account = ref(null);
const banks = ref([]);
const accountTypes = ref([]);
const recentTransactions = ref([]);
const isEditing = ref(false);
const saving = ref(false);

// Formulario de edición
const editForm = reactive({
  name: "",
  account_number: "",
  bank_id: null,
  account_type_id: null,
  current_balance: 0,
  active: true,
});

// Obtener datos de la cuenta específica usando el ID
async function fetchAccount() {
  loading.value = true;
  error.value = null;

  try {
    if (!authStore.accessToken) {
      window.location.href = `/auth/login?returnTo=/dashboard/accounts/${props.accountId}`;
      return;
    }

    // URL correcta con ID específico de la cuenta
    const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(
      `${apiUrl}/api/v1/accounts/${props.accountId}`,
      {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      // Manejar errores específicos
      if (response.status === 404) {
        error.value =
          "La cuenta solicitada no existe o no tienes permiso para verla";
        loading.value = false;
        return;
      }

      if (response.status === 401) {
        const refreshed = await authStore.refreshAuthToken();
        if (refreshed) {
          return fetchAccount();
        } else {
          window.location.href = `/auth/login?returnTo=/dashboard/accounts/${props.accountId}`;
          return;
        }
      }

      throw new Error(
        `Error al obtener datos de la cuenta: ${response.statusText}`
      );
    }

    const accountData = await response.json();
    account.value = accountData;

    // Inicializar formulario con los datos de la cuenta
    Object.assign(editForm, {
      name: account.value.name,
      account_number: account.value.account_number || "",
      bank_id: account.value.bank_id,
      account_type_id: account.value.account_type_id,
      current_balance: account.value.current_balance,
      active: account.value.active,
    });

    // Cargar datos complementarios
    await Promise.all([
      fetchBanks(),
      fetchAccountTypes(),
      fetchRecentTransactions(),
    ]);
  } catch (err) {
    console.error("Error al cargar la cuenta:", err);
    error.value =
      "No se pudo cargar la información de la cuenta. Por favor, intenta nuevamente.";
  } finally {
    loading.value = false;
  }
}

// Resto de tus funciones (fetchBanks, fetchAccountTypes, etc.)

// Importante: verificar el ID al montar el componente
onMounted(() => {
  if (!props.accountId) {
    error.value = "No se especificó un ID de cuenta válido";
    loading.value = false;
  } else {
    fetchAccount();
  }
});
</script>
