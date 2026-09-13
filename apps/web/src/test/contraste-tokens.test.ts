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
 * S1b scope ONLY: today there is a single palette (Tecno-Analítico), so this
 * file checks that each listed token exists with its shipped literal value —
 * no theme, no ratio math yet. Phase 6 (S3, `.dark` = Tinta cálida) and
 * Phase 7 (S4, `:root` = Clínico frío) extend these same assertions with the
 * per-theme WCAG ratio checks from `palette-measurements.md`; a half-applied
 * palette will fail this file once both halves exist.
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
});
