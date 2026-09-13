/**
 * Pie-chart contrast colors — DELIBERATELY theme-immune literals, not
 * `--foreground`/`--card` design-system tokens.
 *
 * `COLOR_BUCKET` (`lib/bucket-colors.ts`) is a permanent literal-hex bucket
 * fill palette that does NOT follow the app's identity (see that module's
 * docstring). A token-based label or stroke would move while those fills
 * stayed put, silently reintroducing the exact WCAG contrast failures these
 * constants exist to fix (WDS-07). On top of that, no surface token can even
 * DESCRIBE the stroke's backdrop: `MiniDistribucionPie` renders inside a
 * `ResumenAnual` cell that is `bg-card` normally and `bg-ingreso` when its
 * month is selected. A `stroke-card` class was tried once and reverted for
 * precisely that reason.
 *
 * Do NOT "DRY" these back into `fill-foreground`/`stroke-card` classes.
 *
 * "Theme-immune" means UNBOUND FROM THE TOKENS, not "never needs to change".
 * Both constants below ARE measured against `COLOR_BUCKET`, and `COLOR_BUCKET`
 * DOES move — it was re-tinted for the Brote palette on 2026-09-12 (fills
 * chosen for their psychological meaning: Necesidades=structure,
 * Deseos=pleasure, Ahorro=growth/most salient — see `bucket-colors.ts`).
 * `PIE_LABEL_FILL`/`PIE_LABEL_FILL_LIGHT` and `PIE_WEDGE_STROKE` must be
 * RE-MEASURED, and `colorEtiquetaPie` re-checked, every time `COLOR_BUCKET`
 * changes — do not assume either survives a future identity or palette
 * change untouched. Rolling a palette back means reverting `index.css`,
 * `bucket-colors.ts`, and this file TOGETHER; a half-revert ships a visible
 * contrast regression, and the specs below assert the literal rather than
 * its contrast, so CI stays green on a half-revert.
 */

/**
 * Dark on-surface label fill. Brote re-tint (2026-09-12) against the current
 * `COLOR_BUCKET`: 6.88:1 (Necesidades), 4.61:1 (Deseos), 9.75:1 (Ahorro) —
 * all clear WCAG 2.2 AA large-text (3:1). Sin categoría's new fill (#686663)
 * is too dark for this tone (2.99:1) — see `PIE_LABEL_FILL_LIGHT` and
 * `colorEtiquetaPie` below.
 */
export const PIE_LABEL_FILL = '#1a1c1c';

/**
 * Light on-surface label fill, added with the Brote re-tint (2026-09-12) for
 * the one bucket the dark tone above no longer covers: Sin categoría's mid
 * grey fill (#686663) clears WCAG 2.2 AA against this light tone at 4.59:1,
 * not against `PIE_LABEL_FILL` (2.99:1, fails). Not used by any other bucket
 * today — see `colorEtiquetaPie`.
 */
export const PIE_LABEL_FILL_LIGHT = '#e8e6e1';

/**
 * Resolves the on-wedge `%` label fill for a bucket key. Necesidades/Deseos/
 * Ahorro (and any unrecognized key) get the dark label; Sin categoría gets
 * the light one — the one bucket in the Brote palette whose fill is too dark
 * for the dark label (see the two constants above). Mirrors
 * `construirOpcionesBucket` in `bucket-colors.ts`: one function, one place to
 * fix if a future palette change moves which bucket needs which label.
 */
export function colorEtiquetaPie(bucket: string): string {
  return bucket === 'SinCategoria' ? PIE_LABEL_FILL_LIGHT : PIE_LABEL_FILL;
}

/**
 * Wedge separator stroke between adjacent bucket slices (WCAG 1.4.11).
 *
 * Was `#ffffff` under the light "Serene Finance" identity, then moved to this
 * dark neutral for the Tecno-Analítico restyle (2026-09-02) — see git history
 * for those numbers. #0d0f15 sits between `--background` (#090a0f) and
 * `--card` (#11131a), so it vanishes into every surface a pie can currently
 * sit on — 1.03:1 on card, 1.03:1 on background, 1.24:1 on the selected-month
 * `ingreso` tint — regardless of what the fills above it are. It is a
 * literal, not `var(--card)`, for the reasons in the module docstring above:
 * it must NOT follow a surface it cannot predict.
 *
 * Brote re-tint (2026-09-12) re-measured the OTHER side of this pair —
 * separation from the new `COLOR_BUCKET` fills:
 *   - Necesidades (#77A7E5): 7.70:1
 *   - Deseos      (#BB6C90): 5.16:1
 *   - Ahorro      (#47DAB4): 10.91:1
 *   - SinCategoria(#686663): 3.35:1
 * All clear WCAG 1.4.11's 3:1 non-text floor.
 */
export const PIE_WEDGE_STROKE = '#0d0f15';

/**
 * Token-backed replacements for `colorEtiquetaPie`/`PIE_WEDGE_STROKE` above
 * (D3, `web-theme-switch`): they resolve to `fill-pie-etiqueta-*`/
 * `stroke-pie-separador` classes pointing at the `--color-pie-etiqueta-*`/
 * `--color-pie-separador` tokens in `index.css`, so the on-wedge label and
 * separator flip with the theme once it exists (S6/S7), instead of staying
 * pinned to today's dark-only values. The three constants above stay as-is
 * for their current consumers until `web-theme-switch` PR4 rewires them;
 * both pairs coexist deliberately in the meantime.
 *
 * Static full literal per branch, same reason as `claseRellenoBucket` in
 * `lib/bucket-colors.ts`: Tailwind 4 only emits utilities it can find as a
 * complete string in source.
 */
const CLASE_ETIQUETA_PIE: Record<string, string> = {
  Necesidades: 'fill-pie-etiqueta-necesidades',
  Deseos: 'fill-pie-etiqueta-gustos',
  Ahorro: 'fill-pie-etiqueta-ahorro',
  SinCategoria: 'fill-pie-etiqueta-sin-categoria',
};

/**
 * Mirrors `colorEtiquetaPie`'s fallback: an unrecognized bucket key gets the
 * same dark-label family the three spend buckets use (Necesidades/Deseos/
 * Ahorro all resolve to the identical token value today — see `index.css` —
 * so any of the three is an equivalent fallback; Necesidades is picked for
 * consistency with `BUCKETS_5030`'s canonical order).
 */
export function claseEtiquetaPie(bucket: string): string {
  return CLASE_ETIQUETA_PIE[bucket] ?? 'fill-pie-etiqueta-necesidades';
}

/** Token-backed replacement for `PIE_WEDGE_STROKE` above — see the block comment. */
export const CLASE_SEPARADOR_PIE = 'stroke-pie-separador';
