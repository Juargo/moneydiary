/**
 * Controlador de tema (web-theme-switch, ADR-043 D4). External store,
 * consumido por `use-preferencia-tema.ts` vía `useSyncExternalStore`. Toda
 * dependencia del entorno (`storage`, `matchMedia`, `documento`, `ventana`)
 * llega inyectada — es la única forma de probar `iniciar()` (listeners de
 * `matchMedia`/`storage`) en jsdom sin depender de los globales reales, y de
 * simular un storage que lanza (WT-03) o un `matchMedia` ausente.
 *
 * Nota (PR9b, split de PR9): este módulo cubre solo el núcleo del
 * controlador — lectura/escritura de preferencia, aplicación al DOM y
 * suscripción. `iniciar()` (los listeners de `matchMedia`/`storage` que
 * conectan cambios externos) llega en PR9c, sin tocar la firma de `entorno`
 * definida acá.
 */
import {
  CLAVE_PREFERENCIA_TEMA,
  aplicarTema,
  leerPreferencia,
  resolverTema,
  type PreferenciaTema,
  type TemaResuelto,
} from './tema';

export interface EstadoTema {
  readonly preferencia: PreferenciaTema;
  readonly temaResuelto: TemaResuelto;
}

export interface ControladorTema {
  /** Referencia estable entre llamadas mientras el estado no cambie —
   * requisito de `useSyncExternalStore` para no re-renderizar sin fin. */
  obtenerEstado(): EstadoTema;
  cambiarPreferencia(preferencia: PreferenciaTema): void;
  suscribir(listener: () => void): () => void;
}

export function crearControladorTema(entorno: {
  storage: Storage | null;
  matchMedia?: Window['matchMedia'];
  documento: Document;
  ventana: Window;
}): ControladorTema {
  const { storage, matchMedia, documento } = entorno;
  const listeners = new Set<() => void>();

  function osPrefiereOscuro(): boolean {
    return (
      matchMedia != null && matchMedia('(prefers-color-scheme: dark)').matches
    );
  }

  function calcularEstado(preferencia: PreferenciaTema): EstadoTema {
    return {
      preferencia,
      temaResuelto: resolverTema(preferencia, osPrefiereOscuro()),
    };
  }

  let estado = calcularEstado(leerPreferencia(storage));

  function aplicar(): void {
    aplicarTema(documento, estado.temaResuelto);
  }

  function notificar(): void {
    listeners.forEach((listener) => listener());
  }

  // Sincroniza el DOM con el estado inicial ya calculado. El script inline
  // de `index.html` ya lo aplicó antes de que este módulo cargue (WT-04);
  // repetirlo acá es idempotente y cubre cualquier consumidor que construya
  // un controlador sin pasar por ese script (tests, por ejemplo).
  aplicar();

  return {
    obtenerEstado() {
      return estado;
    },

    cambiarPreferencia(preferencia) {
      estado = calcularEstado(preferencia);
      try {
        storage?.setItem(CLAVE_PREFERENCIA_TEMA, preferencia);
      } catch {
        // WT-03: una escritura fallida (ej. modo privado) no debe impedir
        // aplicar el tema — solo se pierde la persistencia entre reloads.
      }
      aplicar();
      notificar();
    },

    suscribir(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}
