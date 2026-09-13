/**
 * Controlador de tema (web-theme-switch, ADR-043 D4). External store,
 * consumido por `use-preferencia-tema.ts` vía `useSyncExternalStore`. Toda
 * dependencia del entorno (`storage`, `matchMedia`, `documento`, `ventana`)
 * llega inyectada — es la única forma de probar `iniciar()` (listeners de
 * `matchMedia`/`storage`) en jsdom sin depender de los globales reales, y de
 * simular un storage que lanza (WT-03) o un `matchMedia` ausente.
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
  /** Conecta los listeners de `matchMedia`/`storage`. Devuelve la función
   * de limpieza que los remueve a ambos. */
  iniciar(): () => void;
}

export function crearControladorTema(entorno: {
  storage: Storage | null;
  matchMedia?: Window['matchMedia'];
  documento: Document;
  ventana: Window;
}): ControladorTema {
  const { storage, matchMedia, documento, ventana } = entorno;
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

    iniciar() {
      const limpiezas: Array<() => void> = [];

      if (matchMedia != null) {
        const media = matchMedia('(prefers-color-scheme: dark)');
        const alCambiarOS = () => {
          // Solo re-resuelve bajo `system` (WT-02) — bajo una preferencia
          // explícita, un cambio de OS no debe tocar el tema aplicado.
          if (estado.preferencia !== 'system') {
            return;
          }
          estado = calcularEstado(estado.preferencia);
          aplicar();
          notificar();
        };
        media.addEventListener('change', alCambiarOS);
        limpiezas.push(() => media.removeEventListener('change', alCambiarOS));
      }

      const alCambiarStorage = (evento: StorageEvent) => {
        // `key === null` significa `storage.clear()` en otra pestaña; se
        // relee igual que cualquier cambio de la clave de tema (WT-05).
        if (evento.key !== null && evento.key !== CLAVE_PREFERENCIA_TEMA) {
          return;
        }
        estado = calcularEstado(leerPreferencia(storage));
        aplicar();
        notificar();
      };
      ventana.addEventListener('storage', alCambiarStorage);
      limpiezas.push(() =>
        ventana.removeEventListener('storage', alCambiarStorage),
      );

      return () => limpiezas.forEach((limpiar) => limpiar());
    },
  };
}
