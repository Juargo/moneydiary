/**
 * Resolución pura del tema (web-theme-switch, ADR-043 D4/D5). Sin efectos
 * secundarios de red ni de storage real: `leerPreferencia` recibe el storage
 * inyectado y `aplicarTema` recibe el `Document` inyectado, para que tanto
 * `lib/controlador-tema.ts` como el script inline de `index.html` (parity
 * probada en `prepaint-tema.test.ts`) compartan exactamente la misma lógica.
 */

export type PreferenciaTema = 'light' | 'dark' | 'system';
export type TemaResuelto = 'light' | 'dark';

export const CLAVE_PREFERENCIA_TEMA = 'moneydiary:tema';

/**
 * Palanca de emergencia (D5). Mientras no sea `null`, `resolverTema` la
 * devuelve SIEMPRE, sin importar la preferencia guardada ni el OS. Se usó
 * durante S6 para dejar el tema visible forzado a Tinta cálida mientras el
 * selector aún no existía. Desde S7b (PR11) queda en `null`: el selector es
 * real y `resolverTema` respeta la preferencia guardada (o el OS bajo
 * `system`). Para un rollback de emergencia, volver a poner `'dark'` acá Y
 * `forzado = 'dark'` en el script de `index.html` (deben moverse juntos).
 */
export const TEMA_FORZADO: TemaResuelto | null = null;

// `<meta name="theme-color">` por tema (Token Table, design.md). Deben
// coincidir con el script inline de `index.html` — cambiarlos ahí también.
const THEME_COLOR: Record<TemaResuelto, string> = {
  light: '#EDF0F5',
  dark: '#1A1917',
};

/**
 * Lee la preferencia guardada. Cualquier fallo de acceso (modo privado,
 * storage deshabilitado) o un valor no reconocido caen a `'light'` — default
 * de producto (decisión del owner, 2026-09-13; enmienda WT-02/WT-03 de
 * ADR-043, que documentaban `'system'` como default). Una elección explícita
 * guardada (`'light'`/`'dark'`/`'system'`) se sigue respetando tal cual.
 */
export function leerPreferencia(
  storage: Pick<Storage, 'getItem'> | null,
): PreferenciaTema {
  if (storage == null) {
    return 'light';
  }
  try {
    const valor = storage.getItem(CLAVE_PREFERENCIA_TEMA);
    if (valor === 'light' || valor === 'dark' || valor === 'system') {
      return valor;
    }
    return 'light';
  } catch {
    return 'light';
  }
}

/**
 * Resuelve la preferencia (más el estado del OS bajo `system`) al tema
 * efectivo. `TEMA_FORZADO` gana sobre cualquier entrada mientras no sea
 * `null` — así ningún camino (script, controlador, cambio de OS, evento
 * `storage` cross-tab) puede filtrar `light` mientras el tema siga forzado.
 */
export function resolverTema(
  preferencia: PreferenciaTema,
  osOscuro: boolean,
): TemaResuelto {
  if (TEMA_FORZADO != null) {
    return TEMA_FORZADO;
  }
  if (preferencia === 'system') {
    return osOscuro ? 'dark' : 'light';
  }
  return preferencia;
}

/**
 * Aplica el tema resuelto al DOM: clase `dark` en `<html>`, `color-scheme`
 * inline y el `content` del `<meta name="theme-color">`. Solo el enum
 * resuelto llega acá — el valor crudo de `localStorage` nunca toca el DOM.
 */
export function aplicarTema(doc: Document, tema: TemaResuelto): void {
  const raiz = doc.documentElement;
  raiz.classList.toggle('dark', tema === 'dark');
  raiz.style.colorScheme = tema;
  const meta = doc.querySelector('meta[name="theme-color"]');
  if (meta != null) {
    meta.setAttribute('content', THEME_COLOR[tema]);
  }
}
