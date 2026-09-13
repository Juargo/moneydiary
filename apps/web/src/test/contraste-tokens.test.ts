import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

/**
 * contraste-tokens.test.ts — existence/literal guard for the design tokens
 * declared in `index.css` (`web-theme-switch`, D1/D3). Same discipline as
 * `zona-bar-sources.test.ts`: read the source as plain text (never import
 * CSS as a module under test), resolve the path from `import.meta.url`.
 *
 * S1b/S2 scope was existence/literal only — a single palette
 * (Tecno-Analítico), no theme, no ratio math. Phase 6 (S3, `.dark` = Tinta
 * cálida, below) adds the dark half: every token re-declared inside `.dark`
 * plus a curated set of the measured pairs' WCAG ratios
 * (`palette-measurements.md`). Phase 7 (S4, `:root` = Clínico frío) closes
 * the light half; a half-applied palette fails this file once both halves
 * exist.
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

// Tokens migrados por D1 (buckets, semáforo, ingreso, warning, etc.) — hoy
// declarados en `@theme` con el único valor vigente (Tecno-Analítico). D1
// los deja en `@theme`; el revert de `:root`/`@theme inline` fue descartado
// en design.md, así que este test NO asume una selector específico.
const TOKENS_EXISTENTES: Record<string, string> = {
  'color-necesidades': '#77a7e5',
  'color-gustos': '#bb6c90',
  'color-ahorro': '#47dab4',
  'color-exceso': '#e88a8a',
  'color-sin-categoria': '#686663',
  'color-ingreso': '#0c2a1d',
  'color-ingreso-foreground': '#4ade80',
  'color-vinculo-activo': '#0c2a1d',
  'color-vinculo-activo-foreground': '#4ade80',
  'color-semaforo-verde': '#0c2a1d',
  'color-semaforo-verde-foreground': '#4ade80',
  'color-semaforo-amarillo': '#2a2109',
  'color-semaforo-amarillo-foreground': '#fbbf24',
  'color-semaforo-rojo': '#2c1017',
  'color-semaforo-rojo-foreground': '#fb7185',
  'color-semaforo-verde-band': '#34d399',
  'color-semaforo-amarillo-band': '#fbbf24',
  'color-semaforo-rojo-band': '#fb7185',
  'color-warning': '#241d0b',
  'color-warning-border': '#8a701e',
  'color-warning-foreground': '#fbbf24',
  'color-warning-accent': '#2e2510',
  'color-exito-foreground': '#4ade80',
  'color-cargo-foreground': '#fb7185',
};

// Tokens de S1b (D3), consumidos desde PR4 vía `claseEtiquetaPie`/
// `CLASE_SEPARADOR_PIE` (`lib/pie-colors.ts`) — la etiqueta sobre la tajada y
// el separador de bordes. Mismos números que los literales-hex retirados en
// PR4, para que declarar el token no cambiara nada visualmente en su
// momento.
const TOKENS_NUEVOS_PIE: Record<string, string> = {
  'color-pie-etiqueta-necesidades': '#1a1c1c',
  'color-pie-etiqueta-gustos': '#1a1c1c',
  'color-pie-etiqueta-ahorro': '#1a1c1c',
  'color-pie-etiqueta-sin-categoria': '#e8e6e1',
  'color-pie-separador': '#0d0f15',
};

// Token de S2 (D6, DCR-06) — texto de error separado del fill/border de
// `--destructive`. Valor de hoy (Tecno-Analítico) idéntico al literal ya
// vigente en `--color-semaforo-rojo-foreground`/`--color-cargo-foreground`;
// S3/S4 lo reemplazan por los valores medidos de cada tema
// (`palette-measurements.md`).
const TOKENS_NUEVOS_ERROR: Record<string, string> = {
  'color-error-foreground': '#fb7185',
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

// WCAG 2.2 relative-luminance contrast (sRGB), used only by the curated AA
// checks below — `dark-chrome.e2e.ts` owns the "actually painted" half.
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

// Curated, not exhaustive (review-budget scoped): the literal-value checks
// above already guard every hex; these five re-check the pairs
// `palette-measurements.md` flagged as adjusted or the tightest margin in
// the whole dark set — general text (foreground/background), the
// product-owner's destructive pick, and the three Sin categoría-linked
// values that were hand-nudged to clear AA (fill vs card, its own light
// label, and the one bucket the focus ring's on-fill tone actually passes).
const PARES_AA_DARK: ReadonlyArray<{
  etiqueta: string;
  primerPlano: string;
  fondo: string;
  minimo: number;
}> = [
  {
    etiqueta: 'foreground vs background',
    primerPlano: '#d5d0c6',
    fondo: '#1a1917',
    minimo: 4.5,
  },
  {
    etiqueta: 'white sobre destructive (#be4e43, decisión PO)',
    primerPlano: '#ffffff',
    fondo: '#be4e43',
    minimo: 4.5,
  },
  {
    etiqueta: 'sin-categoria vs card (fill de bucket, ancla ajustada)',
    primerPlano: '#696c63',
    fondo: '#22211e',
    minimo: 3,
  },
  {
    etiqueta: 'pie-etiqueta-sin-categoria (etiqueta clara) vs su fill',
    primerPlano: '#f0eee9',
    fondo: '#696c63',
    minimo: 4.5,
  },
  {
    etiqueta:
      'ring vs sin-categoria (indicador de foco sobre el fill, el único bucket que pasa)',
    primerPlano: '#8fcdd2',
    fondo: '#696c63',
    minimo: 3,
  },
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

describe.each(PARES_AA_DARK)(
  '$etiqueta (Tinta cálida)',
  ({ primerPlano, fondo, minimo }) => {
    it(`cumple el piso WCAG 2.2 AA (>= ${minimo}:1)`, () => {
      expect(contraste(primerPlano, fondo)).toBeGreaterThanOrEqual(minimo);
    });
  },
);
