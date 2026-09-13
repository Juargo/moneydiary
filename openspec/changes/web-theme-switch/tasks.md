# Tasks: Web Theme Switch (Clínico frío / Tinta cálida)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | PR1 ~90-180 · PR2 ~250-380 · PR3 ~190-350 · PR4 ~125-350 · PR5 ~150-350 · PR6 ~200-300 · PR7 ~150-250 · PR8 ~80-150 · PR9 ~200-300 · PR10 ~150-250 · PR11 ~200-300 |
| 400-line budget risk | Low — every upper bound in the plan is ≤380; the former S1 (previously flagged ~450-600) is now four PRs, each with margin below 400 |
| Chained PRs recommended | Yes |
| Suggested split | Tracker → PR1(S1a) → PR2(S1b) → PR3(S1c) → PR4(S1d) → PR5(S2) → PR6(S3) → PR7(S4) → PR8(S5) → PR9(S6) → PR10(S7a) → PR11(S7b) |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Low

**Split rationale (decided now, not deferred):** the original S1 bundled ADR docs, an `index.css` token move, two rewritten `lib/` modules, and five consumer components in one PR (~450-600 lines). `apps/web/src/index.css`, `bucket-colors.ts` and `pie-colors.ts` carry unusually heavy literate doc comments (see their current content), so the token-move and class-helper diffs run larger than a bare code change would suggest. Splitting along natural revert boundaries — docs, token declarations, class helpers, consumers — keeps every resulting PR's upper-bound estimate comfortably under 400 without touching any other slice's scope. S2 through S7b were already ≤400 in the prior forecast (max ~350) and stay single PRs; every other slice's upper bound is re-checked below and none exceeds 400.

**Chain diagram:**
```
main
 └─ feat/web-theme-switch (tracker, draft, no-merge until all children land)
     └─ PR1  feat/tema-adr-docs                  (base: tracker)   S1a
         └─ PR2  feat/tema-tokens-inertes         (base: PR1)      S1b
             └─ PR3  feat/tema-clase-helpers      (base: PR2)      S1c
                 └─ PR4  feat/tema-consumidores-clases (base: PR3) S1d
                     └─ PR5  feat/tema-error-foreground (base: PR4) S2
                         └─ PR6  feat/tema-dark-tinta-calida (base: PR5) S3
                             └─ PR7  feat/tema-light-clinico-frio (base: PR6) S4
                                 └─ PR8  docs/tema-design-rewrite (base: PR7) S5
                                     └─ PR9  feat/tema-runtime-prepaint (base: PR8) S6
                                         └─ PR10 feat/tema-selector-perfil (base: PR9) S7a
                                             └─ PR11 feat/tema-selector-sidebar-e2e (base: PR10) S7b
```
Only `feat/web-theme-switch` merges to `main`. Retarget/rebase any child that shows a prior slice's diff.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 (S1a) | ADR-043 + doc index rows, no code | PR1 | N/A — docs-only | N/A — docs-only | Revert PR1 branch |
| 2 (S1b) | Move theme-adjacent tokens from `@theme` into `:root` with today's (Tecno) values, add placeholder pie tokens; no visual change | PR2 | `pnpm web test -- contraste-tokens` | `pnpm web typecheck` — confirm no consumer regresses | Revert PR2 branch; tokens return to `@theme`, no behavior change |
| 3 (S1c) | `bucket-colors.ts`/`pie-colors.ts` return class names instead of hex | PR3 | `pnpm web test -- bucket-colors pie-colors` | N/A — pure functions, no DOM; confirm via `pnpm web lint` | Revert PR3 branch; consumers still import PR3 exports until PR4, so PR3 alone leaves unused exports, not a broken build |
| 4 (S1d) | 5 consumer components switch to class helpers, no runtime file left importing hex constants | PR4 | `pnpm web test -- DistribucionPie MiniDistribucionPie LeyendaGasto CategoriasPanel ResumenAnual` | Manual `pnpm web dev`: pies/legend render identical colors (still Tecno values) | Revert PR4 branch; consumers revert to hex/inline `style` |
| 5 (S2) | Split error text from `--destructive` fill | PR5 | `pnpm web test -- error-foreground` | Manual `pnpm web dev`: a form validation error still reads legibly | Revert PR5 branch; `text-destructive` usages restored |
| 6 (S3) | `.dark` becomes Tinta cálida | PR6 | `pnpm web test -- contraste-tokens` | `pnpm --filter @moneydiary/web exec playwright test e2e/dark-chrome.e2e.ts` | Revert PR6 branch; `:root` (old Tecno) still governs since class stays static |
| 7 (S4) | `:root` becomes Clínico frío (unreachable) | PR7 | `pnpm web test -- contraste-tokens` | `pnpm --filter @moneydiary/web exec playwright test e2e/light-chrome.e2e.ts` | Revert PR7 branch; static `.dark` class still forces dark |
| 8 (S5) | Docs parity | PR8 | N/A — docs | N/A — docs-only | Revert PR8 branch |
| 9 (S6) | Runtime store + pre-paint script, forced dark | PR9 | `pnpm web test -- tema controlador-tema prepaint-tema` | Manual reload with devtools open: class present before `#root` paints | Revert PR9 branch; `index.html` reverts to static `class="dark"` |
| 10 (S7a) | `SelectorTema` + Apariencia block (inert, forced dark) | PR10 | `pnpm web test -- SelectorTema PerfilPanel` | Manual keyboard-only click-through of Apariencia radios | Revert PR10 branch; `PerfilPanel` reverts to 3 `SeccionConfig` blocks |
| 11 (S7b) | Unlock switch, sidebar shortcut, e2e | PR11 | `pnpm web test -- Sidebar _authenticated` | `pnpm --filter @moneydiary/web exec playwright test e2e/tema.e2e.ts e2e/dark-chrome.e2e.ts e2e/light-chrome.e2e.ts` | Revert PR11 branch, or one-line hotfix `TEMA_FORZADO`/`forzado` back to `'dark'` |

## Phase 1: S1a — ADR-043 + doc index rows [records D1-D10] (PR1 `feat/tema-adr-docs`)

- [x] 1.1 Create `docs/adr/ADR-043-tema-claro-oscuro-web.md` recording D1-D10, `:root`/`.dark`, tri-state + system default, localStorage-only.
- [x] 1.2 Add ADR-043 row to `docs/adr/README.md` and the ADR summary row to `CLAUDE.md`.

## Phase 2: S1b — Inert token migration to `:root` [D1] (PR2 `feat/tema-tokens-inertes`, base PR1)

- [x] 2.1 In `apps/web/src/index.css`, declare the new `pie-etiqueta-*`/`pie-separador` tokens with literal today's (Tecno) values [D1]. Deviation from this task's original wording: D1 (design.md, confirmed by the committed ADR-043) keeps the existing `--color-{necesidades,...}`/`ingreso`/`semaforo-*`/`warning-*`/`exito-foreground`/`cargo-foreground` tokens in `@theme` rather than moving them into `:root` — "move every token into `:root` behind `@theme inline`" is D1's explicitly rejected alternative. No existing token was moved or changed; only the 5 new pie tokens were added, alongside the others in `@theme`.
- [x] 2.2 [RED] Write `apps/web/src/test/contraste-tokens.test.ts`: parses `index.css`, asserts every listed token (existing + the 5 new pie ones) exists with today's literal value (existence/literal check only, selector-agnostic per the D1 correction above — the AA-ratio assertions for both themes land per-theme in Phase 6/7).
- [x] 2.3 [GREEN] Confirm 2.2 passes against 2.1.
- [x] 2.4 [REFACTOR] `pnpm web typecheck`; `pnpm web test -- contraste-tokens`.

## Phase 3: S1c — `bucket-colors`/`pie-colors` class helpers [D3][WT-09] (PR3 `feat/tema-clase-helpers`, base PR2)

- [ ] 3.1 [RED] Rewrite `apps/web/src/lib/bucket-colors.test.ts` and `pie-colors.test.ts` for `claseRellenoBucket`/`claseFondoBucket`/`claseEtiquetaPie`/`CLASE_SEPARADOR_PIE`.
- [ ] 3.2 [GREEN] Rewrite `apps/web/src/lib/bucket-colors.ts` and `pie-colors.ts` to return class names, not hex; fix the stale docstring claiming the view-model consumes them [WT-09].
- [ ] 3.3 [REFACTOR] `pnpm web test -- bucket-colors pie-colors`; `pnpm web lint`.

## Phase 4: S1d — Consumers switch to class helpers (PR4 `feat/tema-consumidores-clases`, base PR3)

- [ ] 4.1 [GREEN] Update `DistribucionPie.tsx`, `MiniDistribucionPie.tsx`, `LeyendaGasto.tsx`, `CategoriasPanel.tsx`, `ResumenAnual.tsx` to consume class helpers instead of hex/inline `style`; update their tests to assert classes, not hex.
- [ ] 4.2 [REFACTOR] `pnpm web lint` and `pnpm web typecheck`; confirm no runtime file imports the removed hex constants (closes the WT-09 import check for the whole S1 chain).

## Phase 5: S2 — error-foreground split [D6][DCR-06] (PR5 `feat/tema-error-foreground`, base PR4)

- [ ] 5.1 Add `--color-error-foreground` to `apps/web/src/index.css` (today's Tecno value `#fb7185`, per design's temporary marker).
- [ ] 5.2 [RED] Extend `contraste-tokens.test.ts` with the `error-foreground` pair (fails until 5.1).
- [ ] 5.3 [GREEN] Confirm 5.2 passes.
- [ ] 5.4 Grep `text-destructive` under `apps/web/src` (34 usages, 19 files) and `apps/web/src/components/BucketDetalleMesPage.tsx:156` (`text-red-600`); replace all with `text-error-foreground`; keep `--destructive` fill/border usages untouched.
- [ ] 5.5 [GREEN] Update every test asserting `text-destructive`/`text-red-600` class output in the touched 19+1 files to `text-error-foreground`.
- [ ] 5.6 [REFACTOR] `pnpm web test`, `pnpm web lint`; re-run `contraste-tokens.test.ts`.

## Phase 6: S3 — `.dark` = Tinta cálida [D2][D7][DCR-07] (PR6 `feat/tema-dark-tinta-calida`, base PR5)

- [ ] 6.1 Add `.dark {}` block to `apps/web/src/index.css` with all Tinta cálida measured values (Token Table); `color-scheme: dark` inside `.dark` only.
- [ ] 6.2 Statically add `class="dark"` to `<html>` in `apps/web/index.html` (script lands in Phase 9).
- [ ] 6.3 [RED] Update `apps/web/e2e/dark-chrome.e2e.ts` to expect card `rgb(34, 33, 30)` and Tinta cálida `color-scheme`.
- [ ] 6.4 [GREEN] Confirm 6.3 passes against 6.1/6.2.
- [ ] 6.5 [RED] Extend `contraste-tokens.test.ts` with the dark half of every measured pair (fails until 6.1).
- [ ] 6.6 [GREEN] Confirm 6.5 passes.
- [ ] 6.7 Remove `dark:` variants from `apps/web/src/components/ui/button.tsx` and `badge.tsx`; keep the `@custom-variant dark` declaration [D7].
- [ ] 6.8 Wrap the `ResumenAnual` mini-pie in `rounded-full bg-card p-0.5` (flagged item d); update its test/snapshot for the ring.
- [ ] 6.9 [REFACTOR] `pnpm web test`, axe both `button`/`badge` variants now that `.dark` is live.

## Phase 7: S4 — `:root` = Clínico frío (unreachable) [D1][DCR-04][DCR-05] (PR7 `feat/tema-light-clinico-frio`, base PR6)

- [ ] 7.1 Replace `:root`/`@theme` defaults in `apps/web/src/index.css` with Clínico frío measured values; `color-scheme: light` in `:root`.
- [ ] 7.2 Rewrite the `index.css` docstring that claims "dark is the ONLY theme."
- [ ] 7.3 [RED] Create `apps/web/e2e/light-chrome.e2e.ts` (mirrors `dark-chrome.e2e.ts`): removes `.dark` in-page, expects `color-scheme: light`, select face `rgb(249, 250, 252)`.
- [ ] 7.4 [GREEN] Confirm 7.3 passes against 7.1.
- [ ] 7.5 [RED] Extend `contraste-tokens.test.ts` with the light half of every measured pair (fails until 7.1).
- [ ] 7.6 [GREEN] Confirm 7.5 passes; both themes now covered — a half-applied palette fails this file.
- [ ] 7.7 [REFACTOR] `pnpm web test`, `pnpm web typecheck`.

## Phase 8: S5 — Docs [D9] (PR8 `docs/tema-design-rewrite`, base PR7)

- [ ] 8.1 Rewrite `DESIGN.md`: title, both identities, token table, jade-vs-ingreso-green adjacency rule (flagged item b), CVD floor-band note.

## Phase 9: S6 — Runtime store + pre-paint, forced dark [D4][D5][WT-03][WT-04] (PR9 `feat/tema-runtime-prepaint`, base PR8)

- [ ] 9.1 [RED] Write `apps/web/src/lib/tema.test.ts`: `leerPreferencia` (throwing/invalid storage → `system`), `resolverTema`, `TEMA_FORZADO='dark'` override.
- [ ] 9.2 [GREEN] Create `apps/web/src/lib/tema.ts` per the design interfaces.
- [ ] 9.3 [RED] Write `apps/web/src/lib/controlador-tema.test.ts`: OS follow only under `system`, `storage` events, failing write still applies theme, injected fakes.
- [ ] 9.4 [GREEN] Create `apps/web/src/lib/controlador-tema.ts` (`crearControladorTema`).
- [ ] 9.5 [GREEN] Create `apps/web/src/lib/use-preferencia-tema.ts`; wire `controladorTema.iniciar()` in `apps/web/src/main.tsx`.
- [ ] 9.6 Replace the static `class="dark"` in `apps/web/index.html` with the inline pre-paint `<script>` (forzado `'dark'`) + `theme-color` meta.
- [ ] 9.7 [RED] Write `apps/web/src/lib/prepaint-tema.test.ts`: extracts the script from `index.html`, runs it via `new Function` against stubbed globals, compares with `resolverTema`.
- [ ] 9.8 [GREEN] Confirm 9.7 passes; fix any drift between script and module.
- [ ] 9.9 [REFACTOR] `pnpm web test`, `pnpm web typecheck`.

## Phase 10: S7a — `SelectorTema` + Apariencia (inert, forced dark) [WT-01][WT-06][WCFG-02][D8][D9] (PR10 `feat/tema-selector-perfil`, base PR9)

- [ ] 10.0 **Manual QA gate (before continuing to S7b):** run `pnpm web dev`, confirm dark Sin categoría bucket fill `#696C63` reads distinctly against the card and the ingreso-tint cell (tightest measured margins, `palette-measurements.md`).
- [ ] 10.1 [RED] Write `apps/web/src/components/SelectorTema.test.tsx`: radio roles/names, arrow-key navigation via `user-event`, per-instance `useId()` name, `vitest-axe` on both variants.
- [ ] 10.2 [GREEN] Create `apps/web/src/components/SelectorTema.tsx` (native `fieldset`/radios; `compacto` variant, 32px icon radios).
- [ ] 10.3 [RED] Update `PerfilPanel.test.tsx` for the new block order: `Editar perfil` → `Cuenta de Google` → `Apariencia` → `Sesión`; `Guardar cambios` stays scoped to `Editar perfil`.
- [ ] 10.4 [GREEN] Add the `Apariencia` `SeccionConfig` to `apps/web/src/components/configuracion/perfil/PerfilPanel.tsx` with description "Se aplica al instante en este dispositivo." and the full `SelectorTema`.
- [ ] 10.5 [REFACTOR] `pnpm web test -- PerfilPanel SelectorTema`, `pnpm web lint`.

## Phase 11: S7b — Unlock, sidebar shortcut, e2e [WT-02][WT-03][WT-04][WT-05][WT-06][D10] (PR11 `feat/tema-selector-sidebar-e2e`, base PR10)

- [ ] 11.1 Set `TEMA_FORZADO = null` in `apps/web/src/lib/tema.ts` and `forzado = null` in the `index.html` inline script; re-run `prepaint-tema.test.ts` parity.
- [ ] 11.2 [RED] Update `apps/web/src/routes/_authenticated.tsx` test coverage for the `sidebarFooter` slot rendering the compact `SelectorTema` alongside `ApiVersionBadge`/logout.
- [ ] 11.3 [GREEN] Inject the compact `SelectorTema` via the existing `sidebarFooter` slot in `_authenticated.tsx`; `Sidebar.tsx` untouched [D10].
- [ ] 11.4 [RED] Write a sync test: changing theme via one `SelectorTema` instance updates the other's checked state (Perfil ↔ Sidebar) [WT-06].
- [ ] 11.5 [GREEN] Confirm 11.4 passes via the shared `usePreferenciaTema` store.
- [ ] 11.6 [RED] Update `dark-chrome.e2e.ts`/`light-chrome.e2e.ts` to use `page.emulateMedia({colorScheme})` instead of a static class, now that the toggle is live.
- [ ] 11.7 [RED] Create `apps/web/e2e/tema.e2e.ts`: reload restores the stored choice with the class present at `DOMContentLoaded` while `#root` is empty; `emulateMedia` live follow under `system`; two pages cross-tab sync via `storage`.
- [ ] 11.8 [GREEN] Confirm 11.6/11.7 pass end-to-end.
- [ ] 11.9 [REFACTOR] Full suite: `pnpm web test`, `pnpm web typecheck`, `pnpm web lint`, `pnpm --filter @moneydiary/web exec playwright test`.
