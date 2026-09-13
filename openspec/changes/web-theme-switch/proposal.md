# Proposal: Web Theme Switch (Clínico frío / Tinta cálida)

## Intent

`apps/web` has one hardcoded dark identity ("Tecno-Analítico"). Users cannot choose light or follow their OS. Add a light/dark/system switch backed by two measured identities. Theme is presentation, not domain data (ADR-024), so no API change.

## Scope

### In Scope
- Tri-state preference: light / dark / system. First visit = system; live OS changes followed while system.
- `localStorage` persistence, cross-tab sync, pre-paint script in `index.html` (no flash), `theme-color` meta.
- `:root` = Clínico frío, `.dark` = Tinta cálida (replaces Tecno-Analítico). Brote bucket palette in both (light: #4369A2 / #782C5C / #049A78 / #2B2E32; dark re-measured).
- Toggle: new `SeccionConfig` in `PerfilPanel.tsx` + compact shortcut in the `Sidebar.tsx` footer slot.
- Small dedicated theme hook/context (not Zustand).
- ADR-043; rewrite `DESIGN.md` and the `index.css` "dark is the ONLY theme" docstring.

### Out of Scope
- Cross-device sync, `User` column, API. Deferred debt — trigger: "user asks for cross-device theme sync".
- `apps/mobile`, `apps/landing`; a `BottomTabs` toggle (mobile width uses Configuración).
- Exact values for the 20+ gap tokens: DESIGN-phase output, not proposal content.

## Capabilities

### New Capabilities
- `web-theme`: preference model, system default and live follow, persistence, no-flash load, toggle surfaces, per-theme AA contrast.

### Modified Capabilities
- `web-app`: DCR-04/05/06 (light token values and pairings become Clínico frío, re-measured); DCR-07 ("dark unaffected" no longer holds); WCFG-02 (Perfil verbatim layout gains an appearance section).

## Approach

- `:root` + `.dark` class, reusing the declared `@custom-variant dark`. Theme-varying `@theme` tokens move to runtime blocks; fonts and `--radius` stay invariant.
- Bucket fills become CSS vars; pie label/stroke gets a theme parameter (`colorEtiquetaPie(bucket, theme)`). `resumen-view-model` stays color-free (ADR-024). No `apps/api` import (ADR-005/008).
- Tests: token-relative assertions; `light-chrome.e2e.ts` mirrors `dark-chrome.e2e.ts`; a11y per ADR-018.

**Rollout (chained PRs):** 1) inert token migration + hook + pre-paint script, forced dark; 2) `.dark` = Tinta cálida; 3) `:root` = Clínico frío + toggle + persistence; 4) theme-aware bucket/pie literals, focus re-derivation, `BucketDetalleMesPage.tsx:156`; 5) ADR, docs, test hardening.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `apps/web/src/index.css`, `index.html` | Modified | Token blocks, `color-scheme`, pre-paint script |
| `apps/web/src/lib/bucket-colors.ts`, `pie-colors.ts`, `components/DistribucionPie.tsx` | Modified | Per-theme colors and focus |
| `components/configuracion/perfil/PerfilPanel.tsx`, `app-shell/Sidebar.tsx` | Modified | Toggle surfaces |
| theme hook + toggle component | New | State and UI |
| `e2e/dark-chrome.e2e.ts`, `DESIGN.md`, `docs/adr/` | Modified/New | Tests, docs, ADR-043 |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Half-applied palette ships green (tests pin literals) | High | Light not user-selectable on `main` before slice 4; token-relative tests |
| Dormant shadcn `dark:` classes activate | Med | Treat `button`/`badge` as new UI; axe both themes |
| `dark-chrome.e2e.ts` pins `rgb(17, 19, 26)` | High | Update in slice 2 |
| `BucketDetalleMesPage.tsx:156` `text-red-600` | Med | Tokenize in slice 4 |
| DistribucionPie two-tone focus proof invalid | High | Re-derive per theme in design |

## Rollback Plan

Client-only, no schema or API. Revert the offending slice PR. Slice 1 is visually inert. Emergency: force `.dark` in the pre-paint script, restoring single-theme behavior. A leftover `localStorage` key is ignored.

## Dependencies

- Brote palette (PR #634, merged); design-phase contrast measurements.

## Success Criteria

- [ ] Light/dark/system selectable from both surfaces; first visit follows OS, including live changes.
- [ ] Reload restores the choice with no flash of the wrong theme.
- [ ] WCAG 2.2 AA in both themes: text ≥4.5:1, non-text ≥3:1.
- [ ] `pnpm web typecheck`, `test`, `lint` and both chrome e2e green.
- [ ] ADR-043 accepted; `DESIGN.md` documents both identities.
