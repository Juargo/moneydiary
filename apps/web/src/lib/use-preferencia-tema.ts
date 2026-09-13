/**
 * Punto de consumo React del controlador de tema (web-theme-switch, ADR-043
 * D4). `controladorTema` es la única instancia global de producción —
 * `main.tsx` la usa directamente para `iniciar()` los listeners de
 * `matchMedia`/`storage`, y `usePreferenciaTema` la consume por defecto sin
 * necesitar un `<Provider>` montado (SelectorTema, en Configuración → Perfil
 * y en el Sidebar, funciona en cualquier ruta sin wrapping extra). Los tests
 * de componentes que necesiten un controlador propio pueden inyectar un fake
 * vía `<ContextoControladorTema.Provider value={...}>`.
 */
import { createContext, useContext, useSyncExternalStore } from 'react';
import {
  crearControladorTema,
  type ControladorTema,
  type EstadoTema,
} from './controlador-tema';
import type { PreferenciaTema } from './tema';

function obtenerStorage(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    // WT-03: navegación privada u otro bloqueo de storage — sin storage, el
    // controlador cae a `system` y no persiste, pero no lanza.
    return null;
  }
}

function obtenerMatchMedia(): Window['matchMedia'] | undefined {
  if (
    typeof window === 'undefined' ||
    typeof window.matchMedia !== 'function'
  ) {
    return undefined;
  }
  return window.matchMedia.bind(window);
}

export const controladorTema: ControladorTema = crearControladorTema({
  storage: obtenerStorage(),
  matchMedia: obtenerMatchMedia(),
  documento: document,
  ventana: window,
});

export const ContextoControladorTema =
  createContext<ControladorTema>(controladorTema);

export function usePreferenciaTema(): EstadoTema & {
  cambiarPreferencia(preferencia: PreferenciaTema): void;
} {
  const controlador = useContext(ContextoControladorTema);
  const estado = useSyncExternalStore(
    controlador.suscribir,
    controlador.obtenerEstado,
    controlador.obtenerEstado,
  );
  return { ...estado, cambiarPreferencia: controlador.cambiarPreferencia };
}
