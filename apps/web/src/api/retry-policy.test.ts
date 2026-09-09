import { describe, expect, it } from 'vitest';
import { TAGS_ERROR_PERMANENTE, esErrorPermanente } from './retry-policy';

// ingesta-pdf-password Slice 4 (Phase 18, design.md D-10): a protected-PDF
// 400 (`code: 'PDF_PROTEGIDO' | 'PDF_PASSWORD_INCORRECTA'`) rides the SAME
// `'invalid'` tag every other 400 already uses (client.ts, Phase 16/17's
// additive `code?` widening). This is a regression guard, not new behavior
// — `'invalid'` was already permanent before this change (client.error must
// never auto-retry a "wrong password" response: the user retries by typing,
// not by TanStack Query's retry machinery). If this test ever fails, that
// IS the finding — it means the widening in Phase 16 accidentally changed
// retry semantics for every other 'invalid' consumer too.
describe('retry-policy — ingesta-pdf-password Slice 4 (Phase 18)', () => {
  it("'invalid' sigue siendo un tag permanente después de que ApiError ganó 'code' opcional (PDF_PROTEGIDO/PDF_PASSWORD_INCORRECTA no deben auto-reintentarse)", () => {
    expect(TAGS_ERROR_PERMANENTE.has('invalid')).toBe(true);
  });

  it('esErrorPermanente sigue considerando permanente un ApiError "invalid" con code PDF_PROTEGIDO', () => {
    expect(
      esErrorPermanente({
        tag: 'invalid',
        message: 'El archivo PDF requiere una contraseña.',
        code: 'PDF_PROTEGIDO',
      }),
    ).toBe(true);
  });
});
