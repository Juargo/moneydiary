# Tasks: Web Theme Switch (Clínico frío / Tinta cálida)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | PR1 ~90-180 · PR2 ~250-380 · PR3 ~190-350 · PR4a 315 (measured) · PR4b ~300-350 · PR5 ~150-350 · PR6 ~200-300 (measured 399/400) · PR7 ~150-250 (measured 399/400) · PR7b ~250-400 (owner-approved insertion, pays contrast-coverage debt) · PR8 ~80-150 · PR9 ~200-300 · PR10 ~150-250 · PR11 ~200-300 |
| 400-line budget risk | Low — every upper bound in the plan is ≤400; the former S1 (previously flagged ~450-600) is now four PRs, each with margin below 400 |
| Chained PRs recommended | Yes |
| Suggested split | Tracker → PR1(S1a) → PR2(S1b) → PR3(S1c) → PR4a(S1d-a) → PR4b(S1d-b) → PR5(S2) → PR6(S3) → PR7(S4) → PR7b(contrast coverage) → PR8(S5) → PR9(S6) → PR10(S7a) → PR11(S7b) — 13 PRs total |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Low

**Split rationale (decided now, not deferred):** the original S1 bundled ADR docs, an `index.css` token move, two rewritten `lib/` modules, and five consumer components in one PR (~450-600 lines). `apps/web/src/index.css`, `bucket-colors.ts` and `pie-colors.ts` carry unusually heavy literate doc comments (see their current content), so the token-move and class-helper diffs run larger than a bare code change would suggest. Splitting along natural revert boundaries — docs, token declarations, class helpers, consumers — keeps every resulting PR's upper-bound estimate comfortably under 400 without touching any other slice's scope. S2 through S7b were already ≤400 in the prior forecast (max ~350) and stay single PRs; every other slice's upper bound is re-checked below and none exceeds 400.

**PR7b insertion (owner-approved, mid-chain):** PR6 and PR7 each landed at 399/400 lines and had to defer their `.dark`/`:root` shadcn-var + curated AA-table coverage to keep under budget (see Phase 6/7 deviation notes below). The owner inserted a dedicated PR right after PR7 to pay that coverage debt: `TOKENS_LIGHT_SHADCN` (mirrors `TOKENS_DARK_SHADCN`) plus the full measured WCAG table for both themes, replacing the curated 5-pair table. Chain grew from 12 to 13 PRs.

**Chain diagram:**
```
main
 └─ feat/web-theme-switch (tracker, draft, no-merge until all children land)
     └─ PR1  feat/tema-adr-docs                  (base: tracker)   S1a
         └─ PR2  feat/tema-tokens-inertes         (base: PR1)      S1b
             └─ PR3  feat/tema-clase-helpers      (base: PR2)      S1c
                 └─ PR4a feat/tema-consumidores-clases (base: PR3) S1d-a
                  └─ PR4b feat/tema-retira-hex        (base: PR4a) S1d-b
                     └─ PR5  feat/tema-error-foreground (base: PR4b) S2
                         └─ PR6  feat/tema-dark-tinta-calida (base: PR5) S3
                             └─ PR7  feat/tema-light-clinico-frio (base: PR6) S4
                                 └─ PR7b test/tema-contraste-completo (base: PR7) contrast coverage 📍
                                     └─ PR8  docs/tema-design-rewrite (base: PR7b) S5
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
| 4a (S1d-a) | 5 consumer components switch to class helpers; hex exports still present | PR4a (#638) | `pnpm web test -- DistribucionPie MiniDistribucionPie LeyendaGasto CategoriasPanel ResumenAnual` | Playwright computed style: Ahorro wedge `fill` rgb(71, 218, 180), separator `stroke` rgb(13, 15, 21) | Revert PR4a branch; consumers revert to hex/inline `style` |
| 4b (S1d-b) | Retire the unused hex exports and the docstrings/tests that named them (closes WT-09) | PR4b | `pnpm web test -- bucket-colors pie-colors contraste-tokens` | `rg` proves zero importers of the retired exports in `apps/web/src` + `apps/web/e2e` | Revert PR4b branch; hex exports return, unused |
| 5 (S2) | Split error text from `--destructive` fill | PR5 | `pnpm web test -- error-foreground` | Manual `pnpm web dev`: a form validation error still reads legibly | Revert PR5 branch; `text-destructive` usages restored |
| 6 (S3) | `.dark` becomes Tinta cálida | PR6 | `pnpm web test -- contraste-tokens` | `pnpm --filter @moneydiary/web exec playwright test e2e/dark-chrome.e2e.ts` | Revert PR6 branch; `:root` (old Tecno) still governs since class stays static |
| 7 (S4) | `:root` becomes Clínico frío (unreachable) | PR7 | `pnpm web test -- contraste-tokens` | `pnpm --filter @moneydiary/web exec playwright test e2e/light-chrome.e2e.ts` | Revert PR7 branch; static `.dark` class still forces dark |
| 7b | Pay PR6/PR7's deferred contrast-coverage debt: light shadcn `:root` dict + full measured WCAG table, both themes | PR7b | `pnpm exec vitest run src/test/contraste-tokens.test.ts` | N/A — pure data-driven unit test, no DOM/runtime surface changes | Revert PR7b branch; token dicts/ratio table return to PR7's curated-dark-only state |
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

- [x] 3.1 [RED] Rewrite `apps/web/src/lib/bucket-colors.test.ts` and `pie-colors.test.ts` for `claseRellenoBucket`/`claseFondoBucket`/`claseEtiquetaPie`/`CLASE_SEPARADOR_PIE`.
- [x] 3.2 [GREEN] Rewrite `apps/web/src/lib/bucket-colors.ts` and `pie-colors.ts` to return class names, not hex; fix the stale docstring claiming the view-model consumes them [WT-09].
- [x] 3.3 [REFACTOR] `pnpm web test -- bucket-colors pie-colors`; `pnpm web lint`.

  **Deviation from 3.1/3.2's wording (recorded here and in the PR3 body):**
  "rewrite ... to return class names" reads as replacing the hex exports.
  That would break `DistribucionPie`/`MiniDistribucionPie`/`LeyendaGasto`/
  `CategoriasPanel`/`ResumenAnual`, which still import `COLOR_BUCKET`/
  `colorEtiquetaPie`/`PIE_WEDGE_STROKE` — those five consumers move to the
  new class helpers only in PR4 (Phase 4), per this file's own Suggested
  Work Units row for unit 3 ("PR3 alone leaves unused exports, not a broken
  build") and per `index.css`'s S1b comment ("PR4 wires the five ...
  consumers"). Followed that plan instead of the literal task wording: ADDED
  `claseRellenoBucket`/`claseFondoBucket` (`bucket-colors.ts`) and
  `claseEtiquetaPie`/`CLASE_SEPARADOR_PIE` (`pie-colors.ts`) alongside the
  existing hex exports, which are untouched in behavior and stay until PR4
  retires them. `bucket-colors.test.ts` did not exist before this PR — it
  is a new file, not a rewrite of one.

  The WT-09 stale-docstring fix from 3.2 IS done as originally worded:
  `bucket-colors.ts`'s module docstring claimed this module "also feeds the
  pure `resumen-view-model`" — verified false (`resumen-view-model.ts` only
  mentions `lib/bucket-colors` in a comment explaining that presentation,
  not domain, resolves color; it has no import of `lib/` at all, by design).
  Corrected to state the real reason the hex stays literal for now (still
  read directly by the five presentation consumers until PR4).

## Phase 4: S1d — Consumers switch to class helpers (PR4a `feat/tema-consumidores-clases` #638, base PR3; PR4b `feat/tema-retira-hex`, base PR4a)

- [x] 4.1 [GREEN] (PR4a) Update `DistribucionPie.tsx`, `MiniDistribucionPie.tsx`, `LeyendaGasto.tsx`, `CategoriasPanel.tsx`, `ResumenAnual.tsx` to consume class helpers instead of hex/inline `style`; update their tests to assert classes, not hex.
- [x] 4.2 [REFACTOR] (PR4b) `pnpm web lint` and `pnpm web typecheck`; confirm no runtime file imports the removed hex constants (closes the WT-09 import check for the whole S1 chain).

  **`ResumenAnual.tsx` needed no code change:** it never imports
  `bucket-colors`/`pie-colors` directly — its mini-pie color comes from
  `MiniDistribucionPie` (already switched). Its own test
  (`ResumenAnual.test.tsx`) DID assert `mini-pie-slice`'s hex `fill`
  attribute directly and was updated to assert the resolved class instead.

  **`COLOR_BUCKET`/`COLOR_EXCESO`/`colorEtiquetaPie`/`PIE_LABEL_FILL`/
  `PIE_LABEL_FILL_LIGHT`/`PIE_WEDGE_STROKE` removed** from
  `bucket-colors.ts`/`pie-colors.ts` this PR (confirmed via `rg` across
  `apps/web/src` + `apps/web/e2e` — zero remaining importers before
  deletion), closing WT-09 for the whole S1 chain. Docstrings in both
  modules, `index.css`, and `contraste-tokens.test.ts` updated to stop
  naming the retired exports. `CategoriasPanel.tsx`'s bucket swatch (no
  prior color test) gained a `data-testid="bucket-swatch"` and one new
  class-assertion test, mirroring `LeyendaGasto`'s existing dot coverage —
  the swap from inline `style` to a class had no test guarding it before.

  **Split into PR4a + PR4b (maintainer decision, 2026-09-12):** the first
  delivery of this phase measured 661 changed lines against PR3, over the
  400-line budget. It was re-sliced along the natural revert boundary the
  original "no cohesive split" note missed: switching consumers does not
  require removing the exports in the same PR, because the exports can stay
  unused for one PR without breaking the build (WT-09 closes in PR4b, and
  `main` never sees the intermediate state under the feature-branch chain).
  - **PR4a** (#638, 315 lines): the five consumers and their tests; hex
    exports still present. Verified in isolation: 1871 tests, typecheck,
    lint green.
  - **PR4b** (`feat/tema-retira-hex`, ~309 code lines + this note): removes
    the six hex exports, their tests, and the docstrings in
    `bucket-colors.ts`, `pie-colors.ts`, `index.css` and
    `contraste-tokens.test.ts` that named them.
  The native attempt ledger was reset by the maintainer for this re-slice.

## Phase 5: S2 — error-foreground split [D6][DCR-06] (PR5 `feat/tema-error-foreground`, base PR4b)

- [x] 5.1 Add `--color-error-foreground` to `apps/web/src/index.css` (today's Tecno value `#fb7185`, per design's temporary marker).
- [x] 5.2 [RED] Extend `contraste-tokens.test.ts` with the `error-foreground` pair (fails until 5.1).
- [x] 5.3 [GREEN] Confirm 5.2 passes.
- [x] 5.4 Grep `text-destructive` under `apps/web/src` (34 usages, 19 files) and `apps/web/src/components/BucketDetalleMesPage.tsx:156` (`text-red-600`); replace all with `text-error-foreground`; keep `--destructive` fill/border usages untouched.
- [x] 5.5 [GREEN] Update every test asserting `text-destructive`/`text-red-600` class output in the touched 19+1 files to `text-error-foreground`.
- [x] 5.6 [REFACTOR] `pnpm web test`, `pnpm web lint`; re-run `contraste-tokens.test.ts`.

  **TDD order note:** followed the inverted order the orchestrator specified
  instead of 5.1-before-5.2's literal wording: wrote the failing
  `contraste-tokens.test.ts` expectation FIRST (RED — `undefined` !== `#fb7185`),
  then added the token (GREEN). Same for 5.4/5.5: flipped the two existing
  class assertions (`Error.test.tsx`, `EditarCategoria.test.tsx`) to expect
  `text-error-foreground` FIRST (RED — both failed against the still-unmigrated
  components), then did the 34+1 usage migration (GREEN). Only two test files
  asserted the class directly; the other 32 migrated usages had no dedicated
  class-assertion test to flip. `rg` confirmed the 34+1 count and, post-migration,
  that the only two remaining `text-destructive`/`text-red-600` string matches
  under `apps/web/src` are explanatory prose comments (`index.css`'s new
  token docstring; `PerfilPanel.tsx`'s note about a PRIOR, unrelated raw-hex
  migration) — not live usages.

## Phase 6: S3 — `.dark` = Tinta cálida [D2][D7][DCR-07] (PR6 `feat/tema-dark-tinta-calida`, base PR5)

- [x] 6.1 Add `.dark {}` block to `apps/web/src/index.css` with all Tinta cálida measured values (Token Table); `color-scheme: dark` inside `.dark` only.
- [x] 6.2 Statically add `class="dark"` to `<html>` in `apps/web/index.html` (script lands in Phase 9).
- [x] 6.3 [RED] Update `apps/web/e2e/dark-chrome.e2e.ts` to expect card `rgb(34, 33, 30)` and Tinta cálida `color-scheme`.
- [x] 6.4 [GREEN] Confirm 6.3 passes against 6.1/6.2.
- [x] 6.5 [RED] Extend `contraste-tokens.test.ts` with the dark half of every measured pair (fails until 6.1).
- [x] 6.6 [GREEN] Confirm 6.5 passes.
- [x] 6.7 Remove `dark:` variants from `apps/web/src/components/ui/button.tsx` and `badge.tsx`; keep the `@custom-variant dark` declaration [D7].
- [x] 6.8 Wrap the `ResumenAnual` mini-pie in `rounded-full bg-card p-0.5` (flagged item d); update its test/snapshot for the ring.
- [x] 6.9 [REFACTOR] `pnpm web test`, axe both `button`/`badge` variants now that `.dark` is live.

  **Deviations (budget-scoped, this PR only):** 6.5/6.6's "every measured
  pair" kept as existence/literal checks for all 48 dark tokens (18 shadcn +
  30 custom, scoped to `.dark {}` via a new `bloqueDark()` helper) plus a
  curated 5-pair `contraste()` AA table (general text, the PO's `#be4e43`
  destructive, and the three Sin categoría-linked adjusted anchors) instead
  of re-deriving every row of `palette-measurements.md` — that would have
  cost ~150 more lines for no new failure-mode coverage. The curation pass
  itself caught a bug: the first draft paired the focus ring against Ahorro
  (1.01:1 FAIL) instead of Sin categoría (3.01:1, the actual passing case).
  6.9's axe check reuses existing `vitest-axe` coverage on components that
  already render `Button`/`Badge` (no dedicated file existed to extend);
  full `pnpm web test` (1938/1938) is the regression proof.
  Bonus: `lib/bucket-colors.ts` had the same stale "(S6/S7)" fixed in
  `index.css` — corrected both to "(S3/S4)".

## Phase 7: S4 — `:root` = Clínico frío (unreachable) [D1][DCR-04][DCR-05] (PR7 `feat/tema-light-clinico-frio`, base PR6)

- [x] 7.1 Replace `:root`/`@theme` defaults in `apps/web/src/index.css` with Clínico frío measured values; `color-scheme: light` in `:root`.
- [x] 7.2 Rewrite the `index.css` docstring that claims "dark is the ONLY theme."
- [x] 7.3 [RED] Create `apps/web/e2e/light-chrome.e2e.ts` (mirrors `dark-chrome.e2e.ts`): removes `.dark` in-page, expects `color-scheme: light`, select face `rgb(249, 250, 252)`.
- [x] 7.4 [GREEN] Confirm 7.3 passes against 7.1.
- [x] 7.5 [RED] Extend `contraste-tokens.test.ts` with the light half of every measured pair (fails until 7.1). Completed in PR7b (`test/tema-contraste-completo`, base PR7): `TOKENS_LIGHT_SHADCN` mirrors `TOKENS_DARK_SHADCN`, and `PARES_TEXTO`/`PARES_NO_TEXTO` replace the curated 5-pair table with every measured pair, run against both themes.
- [x] 7.6 [GREEN] Confirm 7.5 passes; both themes now covered — a half-applied palette fails this file. Completed in PR7b: 214/214 tests green (116 ratio assertions, 58 per theme).
- [x] 7.7 [REFACTOR] `pnpm web test`, `pnpm web typecheck`. Completed in PR7b.

## Phase 7b: Contrast-coverage debt payoff (PR7b `test/tema-contraste-completo`, base PR7)

Owner-approved insertion (position 9 of 13) closing the gap 6.5/6.6 and 7.5-7.7
deferred for budget. See tasks above for the closed items; this phase also
fixed a stale `index.css` comment (`select, option` note) that still
attributed `color-scheme: dark` to `:root`.

## Phase 8: S5 — Docs [D9] (PR8 `docs/tema-design-rewrite`, base PR7b)

- [x] 8.1 Rewrite `DESIGN.md`: title, both identities, token table, jade-vs-ingreso-green adjacency rule (flagged item b), CVD floor-band note.

## Phase 9: S6 — Runtime store + pre-paint, forced dark [D4][D5][WT-03][WT-04] (PR9 `feat/tema-runtime-prepaint`, base PR8)

**Re-slice in progress (owner-approved, position renumbered 12-15 of 16):** PR9a `feat/tema-runtime-modulo` (#645, base PR8) delivered `lib/tema.ts`. PR9b `feat/tema-controlador-nucleo` (#646, base PR9a) delivers the controller core (`obtenerEstado`/`cambiarPreferencia`/`suscribir`, no `iniciar()`) — 304 lines, green standalone. PR9c (controller listeners, `iniciar()`) and PR9d (hook + `main.tsx`/`index.html` wiring + `prepaint-tema.test.ts`) remain `[ ]`, both base-chained after PR9b.

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
