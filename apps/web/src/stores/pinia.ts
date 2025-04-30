import { createPinia } from "pinia";

// Crear instancia de Pinia
export const pinia = createPinia();

// Función para obtener Pinia (solo en cliente)
export function getActivePinia() {
  if (typeof window === "undefined") {
    return null;
  }
  return pinia;
}
