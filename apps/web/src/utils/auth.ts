import { useAuthStore } from "../stores/authStore";
import { loadUserInfo } from "../services/authService";

// Debug flag
const DEBUG_AUTH = false;

const debugLog = (message: string, data?: any) => {
  if (DEBUG_AUTH) {
    if (data) {
      console.log(`[Auth Utils Debug] ${message}`, data);
    } else {
      console.log(`[Auth Utils Debug] ${message}`);
    }
  }
};

/**
 * Verifica si el usuario actual tiene el rol especificado
 * @param roleName Nombre del rol a verificar
 * @param loadIfMissing Si es true, intentará cargar la información del usuario si no está disponible
 * @returns true si el usuario tiene el rol, false en caso contrario
 */
export function hasRole(roleName: string, loadIfMissing = true): boolean {
  debugLog(`Checking if user has role: ${roleName}`);

  const authStore = useAuthStore();

  // Verificar si el usuario está autenticado
  if (!authStore.isAuthenticated || !authStore.user) {
    debugLog("User not authenticated or user data not loaded");
    return false;
  }

  // Si no hay información de rol y loadIfMissing es true, programar una carga de datos
  if (!authStore.user.role && loadIfMissing) {
    debugLog("Role information not loaded, scheduling user info load");
    // Programar la carga pero no esperar (esto se hará de forma asíncrona)
    setTimeout(async () => {
      console.log(
        "Scheduling user info load for role check from loadUserInfo() from authStore"
      );
      await loadUserInfo();
    }, 0);
  }

  const hasRole = authStore.user.role?.name === roleName;
  debugLog(`User ${hasRole ? "has" : "does not have"} role: ${roleName}`);
  return hasRole;
}

/**
 * Verifica si el usuario actual es un administrador
 * @param loadIfMissing Si es true, intentará cargar la información del usuario si no está disponible
 * @returns true si el usuario es administrador, false en caso contrario
 */
export function isAdmin(loadIfMissing = true): boolean {
  debugLog("Checking if user is admin");
  return hasRole("admin", loadIfMissing);
}

/**
 * Verifica si el usuario tiene un permiso específico
 * @param permissionName Nombre del permiso a verificar
 * @param loadIfMissing Si es true, intentará cargar la información del usuario si no está disponible
 * @returns true si el usuario tiene el permiso, false en caso contrario
 */
export function hasPermission(
  permissionName: string,
  loadIfMissing = true
): boolean {
  debugLog(`Checking if user has permission: ${permissionName}`);

  const authStore = useAuthStore();

  // Verificar si el usuario está autenticado
  if (!authStore.isAuthenticated || !authStore.user) {
    debugLog("User not authenticated or user data not loaded");
    return false;
  }

  // Si no hay información de permisos y loadIfMissing es true, programar una carga de datos
  if (
    (!authStore.user.permissions || authStore.user.permissions.length === 0) &&
    loadIfMissing
  ) {
    debugLog("Permission information not loaded, scheduling user info load");
    // Programar la carga pero no esperar (esto se hará de forma asíncrona)
    setTimeout(async () => {
      console.log(
        "Scheduling user info load for permission check from loadUserInfo() from hasPermission"
      );
      await loadUserInfo();
    }, 0);
  }

  // Verificar en permisos directos
  const directPermission =
    authStore.user.permissions?.some((p) => p.name === permissionName) || false;

  // Verificar en permisos del rol
  const rolePermission =
    authStore.user.role?.permissions?.some((p) => p.name === permissionName) ||
    false;

  const hasPermission = directPermission || rolePermission;

  debugLog(
    `User ${
      hasPermission ? "has" : "does not have"
    } permission: ${permissionName}`
  );
  return hasPermission;
}

/**
 * Verifica si el usuario puede acceder a un recurso (basado en permisos RBAC)
 * @param resource Nombre del recurso (ej: 'users', 'accounts')
 * @param action Acción a realizar ('read', 'create', 'update', 'delete', 'all')
 * @returns true si el usuario tiene permiso para la acción en el recurso
 */
export function canAccess(resource: string, action: string): boolean {
  debugLog(`Checking if user can ${action} on resource ${resource}`);

  const authStore = useAuthStore();

  // Verificar si el usuario está autenticado
  if (!authStore.isAuthenticated || !authStore.user) {
    debugLog("User not authenticated or user data not loaded");
    return false;
  }

  // Los administradores tienen acceso completo
  if (isAdmin()) {
    debugLog("User is admin, granting access");
    return true;
  }

  // Combinar permisos directos y de rol
  const allPermissions = [
    ...(authStore.user.permissions || []),
    ...(authStore.user.role?.permissions || []),
  ];

  // Verificar permiso específico (resource:action)
  const hasSpecificPermission = allPermissions.some(
    (p) =>
      p.resource === resource && (p.action === action || p.action === "all")
  );

  // Verificar permiso de acción general para todos los recursos
  const hasGeneralActionPermission = allPermissions.some(
    (p) => p.resource === "*" && (p.action === action || p.action === "all")
  );

  // Verificar permiso de recurso general para todas las acciones
  const hasGeneralResourcePermission = allPermissions.some(
    (p) => p.resource === resource && p.action === "*"
  );

  // Verificar permiso general (admin-like)
  const hasFullPermission = allPermissions.some(
    (p) => p.resource === "*" && p.action === "*"
  );

  const hasAccess =
    hasSpecificPermission ||
    hasGeneralActionPermission ||
    hasGeneralResourcePermission ||
    hasFullPermission;

  debugLog(
    `User ${
      hasAccess ? "has" : "does not have"
    } access to ${action} on ${resource}`
  );
  return hasAccess;
}

/**
 * Componente de autenticación para Vue
 * Proporciona directivas para verificar roles y permisos
 */
export const authDirectives = {
  install(app: any) {
    // Directiva v-admin: solo muestra el elemento si el usuario es administrador
    app.directive("admin", {
      beforeMount(el: HTMLElement, binding: any) {
        const value = binding.value !== undefined ? binding.value : true;
        if (value && !isAdmin()) {
          el.style.display = "none";
        }
      },
      updated(el: HTMLElement, binding: any) {
        const value = binding.value !== undefined ? binding.value : true;
        el.style.display = value && !isAdmin() ? "none" : "";
      },
    });

    // Directiva v-role: solo muestra el elemento si el usuario tiene el rol especificado
    app.directive("role", {
      beforeMount(el: HTMLElement, binding: any) {
        if (!hasRole(binding.value)) {
          el.style.display = "none";
        }
      },
      updated(el: HTMLElement, binding: any) {
        el.style.display = hasRole(binding.value) ? "" : "none";
      },
    });

    // Directiva v-permission: solo muestra el elemento si el usuario tiene el permiso
    app.directive("permission", {
      beforeMount(el: HTMLElement, binding: any) {
        if (!hasPermission(binding.value)) {
          el.style.display = "none";
        }
      },
      updated(el: HTMLElement, binding: any) {
        el.style.display = hasPermission(binding.value) ? "" : "none";
      },
    });
  },
};
