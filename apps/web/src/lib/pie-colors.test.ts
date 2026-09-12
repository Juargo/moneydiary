import { describe, expect, it } from 'vitest';
import {
  PIE_LABEL_FILL,
  PIE_LABEL_FILL_LIGHT,
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
