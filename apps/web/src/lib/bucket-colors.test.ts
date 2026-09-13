import { describe, expect, it } from 'vitest';
import { claseFondoBucket, claseRellenoBucket } from './bucket-colors';

// D3 (design.md, web-theme-switch): pies/legend/categorías consume static
// Tailwind class names, never hex, so a fill/background flips with the theme
// automatically. Every branch below is a literal full class string — Tailwind
// 4 detects utilities by scanning source for complete class names, so no
// template literal or string concatenation is allowed here (constraint
// verified by `pnpm web build`'s emitted CSS, not by this unit test).
describe('claseRellenoBucket', () => {
  it('returns the SVG fill class for each known bucket', () => {
    expect(claseRellenoBucket('Necesidades')).toBe('fill-necesidades');
    expect(claseRellenoBucket('Deseos')).toBe('fill-gustos');
    expect(claseRellenoBucket('Ahorro')).toBe('fill-ahorro');
    expect(claseRellenoBucket('SinCategoria')).toBe('fill-sin-categoria');
  });

  it('falls back to fill-muted-foreground for an unknown bucket key', () => {
    expect(claseRellenoBucket('OtroBucket')).toBe('fill-muted-foreground');
  });
});

describe('claseFondoBucket', () => {
  it('returns the background class for each known bucket', () => {
    expect(claseFondoBucket('Necesidades')).toBe('bg-necesidades');
    expect(claseFondoBucket('Deseos')).toBe('bg-gustos');
    expect(claseFondoBucket('Ahorro')).toBe('bg-ahorro');
    expect(claseFondoBucket('SinCategoria')).toBe('bg-sin-categoria');
  });

  it('falls back to bg-muted-foreground for an unknown bucket key', () => {
    expect(claseFondoBucket('OtroBucket')).toBe('bg-muted-foreground');
  });
});
