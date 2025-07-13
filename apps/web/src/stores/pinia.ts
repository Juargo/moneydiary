import { createPinia, setActivePinia } from "pinia";

// Crear instancia de Pinia
export const pinia = createPinia();

// Inicializar Pinia de manera explícita al cargar este módulo
if (typeof window !== "undefined") {
  // En el cliente, establecemos explícitamente la instancia activa
  setActivePinia(pinia);

  // También mantenemos una referencia global para acceso en cualquier contexto
  window.__pinia = pinia;
} else {
  // En SSR también establecemos la instancia activa
  setActivePinia(pinia);
}

// Función para obtener Pinia (funciona en cliente y SSR)
export function getActivePinia() {
  if (typeof window === "undefined") {
    // En SSR aseguramos que la instancia esté activa antes de devolverla
    setActivePinia(pinia);
    return pinia;
  }

  // En cliente, si por alguna razón no hay una instancia activa, la configuramos
  if (!window.__pinia) {
    setActivePinia(pinia);
    window.__pinia = pinia;
  }

  return window.__pinia;
}

// Para uso explícito en componentes Astro o contextos donde Pinia no esté disponible
export function initPinia() {
  setActivePinia(pinia);
  return pinia;
}

// Asegurar que TypeScript conozca la propiedad __pinia en window
declare global {
  interface Window {
    __pinia?: typeof pinia;
  }
}
