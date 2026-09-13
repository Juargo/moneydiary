import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

/**
 * contraste-tokens.test.ts — existence/literal guard for the design tokens
 * declared in `index.css` (`web-theme-switch`, D1/D3), PLUS the full
 * measured WCAG 2.2 AA contrast table for both themes (WT-07). Same
 * discipline as `zona-bar-sources.test.ts`: read the source as plain text
 * (never import CSS as a module under test), resolve the path from
 * `import.meta.url`.
 *
 * S1b/S2 scope was existence/literal only. Phase 6 (S3, `.dark` = Tinta
 * cálida) added the dark half of the token dicts plus a curated 5-pair
 * table. Phase 7 (S4, `:root` = Clínico frío) synced the `@theme`/`:root`
 * values to the light default. THIS PR (the dedicated contrast-test PR,
 * position 9 of the chain) closes the deferred gap: `TOKENS_LIGHT_SHADCN`
 * below mirrors `TOKENS_DARK_SHADCN`, and the curated 5-pair table is
 * replaced by every pair `palette-measurements.md` measured, run against
 * BOTH themes' actual resolved values (`PARES_TEXTO`/`PARES_NO_TEXTO`, see
 * the resolver helpers below).
 *
 * Comments in `index.css` narrate hex values in prose (docblock tables like
 * "--color-necesidades    #77a7e5   7.95:1") — stripping `/* ... *\/` blocks
 * before matching keeps those from being mistaken for a real declaration.
 */
const THIS_DIR = dirname(fileURLToPath(import.meta.url));
const INDEX_CSS_PATH = resolve(THIS_DIR, '../index.css');

function leerIndexCssSinComentarios(): string {
  const crudo = readFileSync(INDEX_CSS_PATH, 'utf-8');
  return crudo.replace(/\/\*[\s\S]*?\*\//g, '');
}

function valorDeclarado(css: string, token: string): string | undefined {
  const patron = new RegExp(`--${token}:\\s*(#[0-9a-fA-F]{3,8})\\s*;`);
  return css.match(patron)?.[1];
}

// `valorDeclarado` finds the FIRST match in the file, so a var declared in
// both `:root` and `.dark` needs its search scoped here, or it would
// silently read the light value.
function bloqueDark(css: string): string {
  const match = css.match(/\.dark\s*\{([\s\S]*?)\n\}/);
  if (!match) {
    throw new Error('No se encontró el bloque .dark en index.css');
  }
  return match[1];
}

// Tokens migrados por D1, declarados en `@theme` con el valor LIGHT
// (Clínico frío) por defecto desde S4 (`.dark` los reescribe, ver
// `TOKENS_DARK_CUSTOM`). El revert de `:root`/`@theme inline` fue
// descartado en design.md, así que este test NO asume un selector específico.
const TOKENS_EXISTENTES: Record<string, string> = {
  'color-necesidades': '#4369a2',
  'color-gustos': '#782c5c',
  'color-ahorro': '#049a78',
  'color-exceso': '#c2410c',
  'color-sin-categoria': '#2b2e32',
  'color-ingreso': '#dcfce7',
  'color-ingreso-foreground': '#0f6b4a',
  'color-vinculo-activo': '#dcfce7',
  'color-vinculo-activo-foreground': '#0f6b4a',
  'color-semaforo-verde': '#dcfce7',
  'color-semaforo-verde-foreground': '#0f6b4a',
  'color-semaforo-amarillo': '#f3e4c0',
  'color-semaforo-amarillo-foreground': '#8a5000',
  'color-semaforo-rojo': '#f8dce3',
  'color-semaforo-rojo-foreground': '#b4143c',
  'color-semaforo-verde-band': '#0f6b4a',
  'color-semaforo-amarillo-band': '#8a5000',
  'color-semaforo-rojo-band': '#b4143c',
  'color-warning': '#f5e7c4',
  'color-warning-border': '#b5760a',
  'color-warning-foreground': '#8a5000',
  'color-warning-accent': '#eedba8',
  'color-exito-foreground': '#0f6b4a',
  'color-cargo-foreground': '#b4143c',
};

// Tokens de D3, consumidos vía `claseEtiquetaPie`/`CLASE_SEPARADOR_PIE`
// (`lib/pie-colors.ts`) — la etiqueta sobre la tajada y el separador de
// bordes. Valores LIGHT (Clínico frío) desde S4.
const TOKENS_NUEVOS_PIE: Record<string, string> = {
  'color-pie-etiqueta-necesidades': '#ffffff',
  'color-pie-etiqueta-gustos': '#ffffff',
  'color-pie-etiqueta-ahorro': '#0f1f1a',
  'color-pie-etiqueta-sin-categoria': '#ffffff',
  'color-pie-separador': '#fafbfd',
};

// Token de D6/DCR-06 — texto de error separado del fill/border de
// `--destructive`. Valor LIGHT (Clínico frío) desde S4; `.dark` carga Tinta
// cálida en `TOKENS_DARK_CUSTOM`.
const TOKENS_NUEVOS_ERROR: Record<string, string> = {
  'color-error-foreground': '#b4143c',
};

// S4→PR7b (D1) — shadcn raw vars inside `:root`, Clínico frío values.
// Mirrors `TOKENS_DARK_SHADCN` below. Resolved via the same
// `valorDeclarado(css, token)` used by `TOKENS_EXISTENTES` above — `:root`
// physically precedes `.dark` (D1's CSS-ordering invariant), so the first
// match IS the light value.
const TOKENS_LIGHT_SHADCN: Record<string, string> = {
  background: '#edf0f5',
  foreground: '#2a2f3a',
  card: '#f9fafc',
  'card-foreground': '#2a2f3a',
  popover: '#f9fafc',
  'popover-foreground': '#2a2f3a',
  muted: '#e3e7ee',
  'muted-foreground': '#5a6270',
  accent: '#dce1ea',
  'accent-foreground': '#2a2f3a',
  primary: '#1d5fa8',
  'primary-foreground': '#ffffff',
  secondary: '#4f4a6b',
  'secondary-foreground': '#ffffff',
  destructive: '#c1121f',
  border: '#b6becc',
  input: '#7c8798',
  ring: '#1d5fa8',
};

// S3 (D1, D7, DCR-07) — shadcn raw vars inside `.dark`, Tinta cálida values.
// `destructive` is the PO's low-chroma pick (`#be4e43`), not `#e11d48`.
const TOKENS_DARK_SHADCN: Record<string, string> = {
  background: '#1a1917',
  foreground: '#d5d0c6',
  card: '#22211e',
  'card-foreground': '#d5d0c6',
  popover: '#22211e',
  'popover-foreground': '#d5d0c6',
  muted: '#2a2825',
  'muted-foreground': '#9a9488',
  accent: '#302e2a',
  'accent-foreground': '#d5d0c6',
  primary: '#6fb8be',
  'primary-foreground': '#1a1917',
  secondary: '#b0a893',
  'secondary-foreground': '#1a1917',
  destructive: '#be4e43',
  border: '#3f3b34',
  input: '#7a7362',
  ring: '#8fcdd2',
};

// S3 — custom `--color-*` tokens inside `.dark`, re-declared literally even
// where unchanged from `@theme` (the block is self-contained, no aliasing).
// `sin-categoria`/`exceso` DO change value (adjusted anchors).
const TOKENS_DARK_CUSTOM: Record<string, string> = {
  'color-necesidades': '#77a7e5',
  'color-gustos': '#bb6c90',
  'color-ahorro': '#47dab4',
  'color-sin-categoria': '#696c63',
  'color-exceso': '#bf9350',
  'color-pie-etiqueta-necesidades': '#1a1c1c',
  'color-pie-etiqueta-gustos': '#1a1c1c',
  'color-pie-etiqueta-ahorro': '#1a1c1c',
  'color-pie-etiqueta-sin-categoria': '#f0eee9',
  'color-pie-separador': '#100f0d',
  'color-ingreso': '#202a1e',
  'color-ingreso-foreground': '#7fb77e',
  'color-vinculo-activo': '#202a1e',
  'color-vinculo-activo-foreground': '#7fb77e',
  'color-semaforo-verde': '#202a1e',
  'color-semaforo-verde-foreground': '#7fb77e',
  'color-semaforo-verde-band': '#7fb77e',
  'color-semaforo-amarillo': '#2b2313',
  'color-semaforo-amarillo-foreground': '#d9a44c',
  'color-semaforo-amarillo-band': '#d9a44c',
  'color-semaforo-rojo': '#2b1f1d',
  'color-semaforo-rojo-foreground': '#d97a72',
  'color-semaforo-rojo-band': '#d97a72',
  'color-warning': '#2b2210',
  'color-warning-border': '#8a6a2e',
  'color-warning-foreground': '#d9a44c',
  'color-warning-accent': '#332813',
  'color-exito-foreground': '#7fb77e',
  'color-cargo-foreground': '#d97a72',
  'color-error-foreground': '#d97a72',
};

// WCAG 2.2 relative-luminance contrast (sRGB), used by the ratio checks
// below — `dark-chrome.e2e.ts`/`light-chrome.e2e.ts` own the "actually
// painted" half.
function componenteLineal(canal: number): number {
  const c = canal / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

function luminanciaRelativa(hex: string): number {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (
    0.2126 * componenteLineal(r) +
    0.7152 * componenteLineal(g) +
    0.0722 * componenteLineal(b)
  );
}

function contraste(hexA: string, hexB: string): number {
  const [claro, oscuro] = [luminanciaRelativa(hexA), luminanciaRelativa(hexB)]
    .sort((a, b) => b - a)
    .map((l) => l + 0.05);
  return claro / oscuro;
}

// Alpha-composite `hexFg` at `opacidad` (0-1) over `hexFondo` — used for the
// `bg-destructive/10` Tailwind utility, which never resolves to a flat hex.
function componer(hexFg: string, opacidad: number, hexFondo: string): string {
  const canal = (hex: string, inicio: number) =>
    parseInt(hex.slice(inicio, inicio + 2), 16);
  const mezclar = (fg: number, fondo: number) =>
    Math.round(fg * opacidad + fondo * (1 - opacidad))
      .toString(16)
      .padStart(2, '0');
  const r = mezclar(canal(hexFg, 1), canal(hexFondo, 1));
  const g = mezclar(canal(hexFg, 3), canal(hexFondo, 3));
  const b = mezclar(canal(hexFg, 5), canal(hexFondo, 5));
  return `#${r}${g}${b}`;
}

// Per-theme token resolver (WT-07): `valorDeclarado(css, token)` finds the
// LIGHT value (`:root`/`@theme` precede `.dark` in source order, D1); the
// dark resolver scopes to `bloqueDark(css)` and falls back to the light
// value only when a token is not re-declared there (none are today, but the
// fallback keeps this table correct if that ever changes).
type Proveedor = string | ((resolver: (token: string) => string) => string);

function crearResolutor(
  css: string,
  tema: 'light' | 'dark',
): (token: string) => string {
  const claro = (token: string): string => {
    const valor = valorDeclarado(css, token);
    if (!valor) {
      throw new Error(`Token --${token} no declarado en :root/@theme`);
    }
    return valor;
  };
  if (tema === 'light') {
    return claro;
  }
  return (token: string) =>
    valorDeclarado(bloqueDark(css), token) ?? claro(token);
}

// `Proveedor` values starting with `#` are literals (e.g. shadcn's hardcoded
// `text-white`); anything else is a token name resolved per theme.
function resolverColor(
  resolver: (token: string) => string,
  valor: Proveedor,
): string {
  if (typeof valor === 'function') {
    return valor(resolver);
  }
  return valor.startsWith('#') ? valor : resolver(valor);
}

// Full measured set from `palette-measurements.md`, both themes (WT-07).
// Excluded on purpose: decorative `border` (no floor, §"Remaining WARN"#6),
// light `input` vs `muted` (informational, §"Remaining WARN"#7), and the
// dark Sin categoría fill vs the selected-month `ingreso` tint (2.85:1 —
// mitigated by the mini-pie card ring added in PR6, §"Mini-pie fills").
const PARES_TEXTO: ReadonlyArray<readonly [string, Proveedor, Proveedor]> = [
  ['foreground/background', 'foreground', 'background'],
  ['foreground/card', 'foreground', 'card'],
  ['card-foreground/card', 'card-foreground', 'card'],
  ['popover-foreground/popover', 'popover-foreground', 'popover'],
  ['muted-foreground/card', 'muted-foreground', 'card'],
  ['muted-foreground/muted', 'muted-foreground', 'muted'],
  ['muted-foreground/background', 'muted-foreground', 'background'],
  ['accent-foreground/accent', 'accent-foreground', 'accent'],
  ['primary-foreground/primary', 'primary-foreground', 'primary'],
  ['secondary-foreground/secondary', 'secondary-foreground', 'secondary'],
  ['#ffffff literal/destructive (shadcn text-white)', '#ffffff', 'destructive'],
  ['ingreso-foreground/ingreso', 'color-ingreso-foreground', 'color-ingreso'],
  [
    'vinculo-activo-foreground/vinculo-activo',
    'color-vinculo-activo-foreground',
    'color-vinculo-activo',
  ],
  [
    'semaforo-verde-foreground/semaforo-verde',
    'color-semaforo-verde-foreground',
    'color-semaforo-verde',
  ],
  [
    'semaforo-amarillo-foreground/semaforo-amarillo',
    'color-semaforo-amarillo-foreground',
    'color-semaforo-amarillo',
  ],
  [
    'semaforo-rojo-foreground/semaforo-rojo',
    'color-semaforo-rojo-foreground',
    'color-semaforo-rojo',
  ],
  ['warning-foreground/warning', 'color-warning-foreground', 'color-warning'],
  ['warning-foreground/card', 'color-warning-foreground', 'card'],
  [
    'warning-foreground/warning-accent',
    'color-warning-foreground',
    'color-warning-accent',
  ],
  ['exito-foreground/card', 'color-exito-foreground', 'card'],
  ['exito-foreground/background', 'color-exito-foreground', 'background'],
  ['cargo-foreground/card', 'color-cargo-foreground', 'card'],
  ['cargo-foreground/background', 'color-cargo-foreground', 'background'],
  ['error-foreground/card', 'color-error-foreground', 'card'],
  ['error-foreground/background', 'color-error-foreground', 'background'],
  [
    'error-foreground/bg-destructive\\/10 sobre card (composite)',
    'color-error-foreground',
    (r) => componer(r('destructive'), 0.1, r('card')),
  ],
  [
    'pie-etiqueta-necesidades/necesidades (fill)',
    'color-pie-etiqueta-necesidades',
    'color-necesidades',
  ],
  [
    'pie-etiqueta-gustos/gustos (fill)',
    'color-pie-etiqueta-gustos',
    'color-gustos',
  ],
  [
    'pie-etiqueta-ahorro/ahorro (fill)',
    'color-pie-etiqueta-ahorro',
    'color-ahorro',
  ],
  [
    'pie-etiqueta-sin-categoria/sin-categoria (fill)',
    'color-pie-etiqueta-sin-categoria',
    'color-sin-categoria',
  ],
];

const PARES_NO_TEXTO: ReadonlyArray<readonly [string, Proveedor, Proveedor]> = [
  ['input/card', 'input', 'card'],
  ['input/background', 'input', 'background'],
  ['ring/card', 'ring', 'card'],
  ['ring/background', 'ring', 'background'],
  ['destructive/card (invalid-input border)', 'destructive', 'card'],
  [
    'destructive/background (invalid-input border)',
    'destructive',
    'background',
  ],
  ['semaforo-verde-band/card', 'color-semaforo-verde-band', 'card'],
  ['semaforo-verde-band/background', 'color-semaforo-verde-band', 'background'],
  ['semaforo-amarillo-band/card', 'color-semaforo-amarillo-band', 'card'],
  [
    'semaforo-amarillo-band/background',
    'color-semaforo-amarillo-band',
    'background',
  ],
  ['semaforo-rojo-band/card', 'color-semaforo-rojo-band', 'card'],
  ['semaforo-rojo-band/background', 'color-semaforo-rojo-band', 'background'],
  ['warning-border/background', 'color-warning-border', 'background'],
  ['warning-border/warning', 'color-warning-border', 'color-warning'],
  ['exceso/card', 'color-exceso', 'card'],
  ['exceso/background', 'color-exceso', 'background'],
  ['necesidades (fill)/card', 'color-necesidades', 'card'],
  ['necesidades (fill)/background', 'color-necesidades', 'background'],
  ['gustos (fill)/card', 'color-gustos', 'card'],
  ['gustos (fill)/background', 'color-gustos', 'background'],
  ['ahorro (fill)/card', 'color-ahorro', 'card'],
  ['ahorro (fill)/background', 'color-ahorro', 'background'],
  ['sin-categoria (fill)/card', 'color-sin-categoria', 'card'],
  ['sin-categoria (fill)/background', 'color-sin-categoria', 'background'],
  [
    'pie-separador/necesidades (fill)',
    'color-pie-separador',
    'color-necesidades',
  ],
  ['pie-separador/gustos (fill)', 'color-pie-separador', 'color-gustos'],
  ['pie-separador/ahorro (fill)', 'color-pie-separador', 'color-ahorro'],
  [
    'pie-separador/sin-categoria (fill)',
    'color-pie-separador',
    'color-sin-categoria',
  ],
];

describe('contraste-tokens', () => {
  const css = leerIndexCssSinComentarios();

  describe.each(Object.entries(TOKENS_EXISTENTES))(
    'token existente --%s',
    (token, esperado) => {
      it(`declara ${esperado}`, () => {
        expect(valorDeclarado(css, token)).toBe(esperado);
      });
    },
  );

  describe.each(Object.entries(TOKENS_NUEVOS_PIE))(
    'token nuevo de pie --%s',
    (token, esperado) => {
      it(`declara ${esperado} (S1b, D3)`, () => {
        expect(valorDeclarado(css, token)).toBe(esperado);
      });
    },
  );

  describe.each(Object.entries(TOKENS_NUEVOS_ERROR))(
    'token nuevo de error --%s',
    (token, esperado) => {
      it(`declara ${esperado} (S2, D6)`, () => {
        expect(valorDeclarado(css, token)).toBe(esperado);
      });
    },
  );

  it('declara color-scheme: light dentro de :root (D2)', () => {
    expect(css).toMatch(/color-scheme:\s*light;/);
  });

  describe.each(Object.entries(TOKENS_LIGHT_SHADCN))(
    'token shadcn --%s en :root',
    (token, esperado) => {
      it(`declara ${esperado} (S4→PR7b, D1, Clínico frío)`, () => {
        expect(valorDeclarado(css, token)).toBe(esperado);
      });
    },
  );

  it('declara color-scheme: dark dentro de .dark (D2)', () => {
    expect(bloqueDark(css)).toMatch(/color-scheme:\s*dark;/);
  });

  describe.each(Object.entries(TOKENS_DARK_SHADCN))(
    'token shadcn --%s en .dark',
    (token, esperado) => {
      it(`declara ${esperado} (S3, D1/D7, Tinta cálida)`, () => {
        expect(valorDeclarado(bloqueDark(css), token)).toBe(esperado);
      });
    },
  );

  describe.each(Object.entries(TOKENS_DARK_CUSTOM))(
    'token --%s en .dark',
    (token, esperado) => {
      it(`declara ${esperado} (S3, Tinta cálida)`, () => {
        expect(valorDeclarado(bloqueDark(css), token)).toBe(esperado);
      });
    },
  );
});

describe.each(['light', 'dark'] as const)(
  'WCAG 2.2 AA — texto (%s, >=4.5:1)',
  (tema) => {
    const resolver = crearResolutor(leerIndexCssSinComentarios(), tema);

    it.each(PARES_TEXTO)('%s', (_etiqueta, fg, bg) => {
      const ratio = contraste(
        resolverColor(resolver, fg),
        resolverColor(resolver, bg),
      );
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });
  },
);

describe.each(['light', 'dark'] as const)(
  'WCAG 2.2 AA — no-texto (%s, >=3:1)',
  (tema) => {
    const resolver = crearResolutor(leerIndexCssSinComentarios(), tema);

    it.each(PARES_NO_TEXTO)('%s', (_etiqueta, fg, bg) => {
      const ratio = contraste(
        resolverColor(resolver, fg),
        resolverColor(resolver, bg),
      );
      expect(ratio).toBeGreaterThanOrEqual(3);
    });
  },
);
