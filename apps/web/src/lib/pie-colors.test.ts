import { describe, expect, it } from 'vitest';
import {
  CLASE_SEPARADOR_PIE,
  PIE_LABEL_FILL,
  PIE_LABEL_FILL_LIGHT,
  claseEtiquetaPie,
  colorEtiquetaPie,
} from './pie-colors';

// Brote re-tint (2026-09-12): Sin categoría's new fill (#686663) is too dark
// for the shared dark on-wedge label (2.99:1) — the label choice is now
// per-bucket instead of a single constant. `colorEtiquetaPie` is the single
// place that decides it, mirroring `construirOpcionesBucket` in
// `bucket-colors.ts`.
describe('colorEtiquetaPie', () => {
  it('returns the dark label fill for Necesidades, Deseos, and Ahorro', () => {
    expect(colorEtiquetaPie('Necesidades')).toBe(PIE_LABEL_FILL);
    expect(colorEtiquetaPie('Deseos')).toBe(PIE_LABEL_FILL);
    expect(colorEtiquetaPie('Ahorro')).toBe(PIE_LABEL_FILL);
  });

  it('returns the light label fill for SinCategoria (its fill is too dark for the dark label)', () => {
    expect(colorEtiquetaPie('SinCategoria')).toBe(PIE_LABEL_FILL_LIGHT);
  });

  it('defaults to the dark label fill for an unknown bucket key', () => {
    expect(colorEtiquetaPie('OtroBucket')).toBe(PIE_LABEL_FILL);
  });
});

// D3 (design.md, web-theme-switch): the token-backed class helpers land
// alongside `colorEtiquetaPie`/`PIE_*` above (kept for existing consumers
// until PR4 rewires them) — same fallback shape, different literal.
describe('claseEtiquetaPie', () => {
  it('returns the token-backed label fill class for each known bucket', () => {
    expect(claseEtiquetaPie('Necesidades')).toBe(
      'fill-pie-etiqueta-necesidades',
    );
    expect(claseEtiquetaPie('Deseos')).toBe('fill-pie-etiqueta-gustos');
    expect(claseEtiquetaPie('Ahorro')).toBe('fill-pie-etiqueta-ahorro');
    expect(claseEtiquetaPie('SinCategoria')).toBe(
      'fill-pie-etiqueta-sin-categoria',
    );
  });

  it('defaults to the Necesidades label class for an unknown bucket key', () => {
    expect(claseEtiquetaPie('OtroBucket')).toBe(
      'fill-pie-etiqueta-necesidades',
    );
  });
});

describe('CLASE_SEPARADOR_PIE', () => {
  it('is the static stroke class for the wedge separator token', () => {
    expect(CLASE_SEPARADOR_PIE).toBe('stroke-pie-separador');
  });
});
