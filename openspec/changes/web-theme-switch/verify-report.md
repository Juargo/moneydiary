```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:cbed449f68692518287e40367375ce071486a5ed252d8e3f0bb049da225dbb88
verdict: fail
blockers: 1
critical_findings: 1
requirements: 14/14
scenarios: 29/29
test_command: pnpm web test
test_exit_code: 0
test_output_hash: sha256:f392e6cf6f4f462492cbed43eabd4a14fb9ad0baa0e8d284d093547adb47b4e5
build_command: pnpm web build
build_exit_code: 0
build_output_hash: sha256:14c94e51e1eca8912a36a18be1a0f38ad9b3efe251e0c92faebf914575d438ca
```

## Verification Report

**Change**: web-theme-switch
**Version**: chain tip `feat/tema-selector-sidebar-e2e` @ `eed2ee5a` (16 PRs, tracker `feat/web-theme-switch` still = `main`)
**Mode**: Strict TDD

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 58 |
| Tasks complete | 58 |
| Tasks incomplete | 0 |

All 11 phases (S1a..S7b, split into 13 delivered PR slices, some further split per
recorded maintainer decisions: PR4→PR4a/PR4b, S6→PR9a-d) are checked `[x]` in
`tasks.md`, with every deviation from literal task wording recorded inline
(Phase 3, 4, 5, 6, 9 deviation notes) and judged below.

### Build & Tests Execution

**Build**: PASS
```text
$ pnpm web build
tsr generate && tsc -b && vite build
✓ built in 253ms  (exit 0)
```

**Typecheck**: PASS
```text
$ pnpm web typecheck
tsr generate && tsc -b   (exit 0, no output = no errors)
```

**Lint**: PASS
```text
$ pnpm web lint
eslint .   (exit 0, no output = no errors)
```

**Tests**: PASS — 2109/2109
```text
$ pnpm web test
Test Files  149 passed (149)
     Tests  2109 passed (2109)
  Duration  18.91s   (exit 0)
```

**Playwright (`--project=escritorio`, apps/web)**: PASS — 37 passed, 19 skipped (pre-existing, unrelated breakpoint-scoped specs), 0 failed
```text
$ pnpm exec playwright test --project=escritorio
  37 passed (8.9s)
  19 skipped
tema.e2e.ts:26  ✓ elegir Oscuro persiste tras el reload ... (WT-03/WT-04)
tema.e2e.ts:57  ✓ bajo preferencia system, un cambio de OS en vivo ... (WT-02)
tema.e2e.ts:75  ✓ cross-tab: cambiar el tema en una pestaña actualiza la otra (WT-05)
dark-chrome.e2e.ts:49  ✓ el elemento raíz declara color-scheme: dark
dark-chrome.e2e.ts:63  ✓ los <select> nativos pintan su propia cara oscura
light-chrome.e2e.ts:15 ✓ con OS claro y sin preferencia guardada, color-scheme: light
light-chrome.e2e.ts:40 ✓ los <select> nativos pintan la cara Clínico frío
```

**Coverage**: Not run — no coverage flag configured in this project's `test` script; not required by `openspec/config.yaml`. ➖ Not available.

**CI status on PR #650 (chain tip, reported by the orchestrator, not reproduced by this verify's commanded scope)**: RED — "E2E (Playwright, web)" job, project `movil` (360px) only. Three failing specs in `apps/web/e2e/tema.e2e.ts` (lines 26, 57, 75): they navigate to `RUTA_HOME` (dashboard) and then look up `getByRole('radio', {name: 'Oscuro'|'Sistema'})`; at mobile width only the Sidebar-footer compact `SelectorTema` shortcut exists in the DOM subtree these tests reach, and that shortcut is desktop-only by requirement (WT-06: "a compact shortcut in the Sidebar footer (**desktop**)" — mobile reaches the toggle only via Configuración → Perfil → Apariencia, per the same requirement and per `design.md`'s Slice Plan / `_authenticated.tsx` wiring). `escritorio` and `tablet` Playwright projects pass; CodeQL reports 0 open alerts.

This is a **test-authoring defect, not a product/spec defect**: `tema.e2e.ts` was written and verified against the `escritorio` project only (see PR11's apply-progress note and this verify's own escritorio run, both green); it was never exercised against `movil`, where the DOM path to the toggle differs by design. No requirement in `web-theme` or `web-app` promises a Sidebar-shortcut at mobile width — WT-06 explicitly scopes it to desktop, and WCFG-02 is what carries the toggle at any width via Configuración. Recorded as CRITICAL below because it leaves CI red on the tip PR, which blocks merge under this repo's branch-protection policy, regardless of the underlying cause being test-scope rather than behavior.

### Spec Compliance Matrix — `web-theme` (WT-01..WT-09)

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| WT-01 | User selects an explicit theme | `tema.test.ts` (resolverTema explicit) + `controlador-tema.test.ts` (cambiarPreferencia) + `SelectorTema.test.tsx` | ✅ COMPLIANT |
| WT-01 | User selects system | `tema.test.ts` / `controlador-tema.test.ts` system-resume cases | ✅ COMPLIANT |
| WT-02 | First visit follows the OS | `tema.test.ts` (`leerPreferencia`→`system` default) + `prepaint-tema.test.ts` parity | ✅ COMPLIANT |
| WT-02 | Live OS change updates system mode | `controlador-tema.test.ts` (matchMedia `change` listener, system-only) + `e2e/tema.e2e.ts:57` (`emulateMedia` live, escritorio: PASS) | ✅ COMPLIANT |
| WT-02 | OS change ignored under explicit choice | `controlador-tema.test.ts` (explicit pref + OS change → unchanged) | ✅ COMPLIANT |
| WT-03 | Preference survives a reload | `e2e/tema.e2e.ts:26` (escritorio: PASS) | ✅ COMPLIANT |
| WT-03 | Storage throws on read or write | `tema.test.ts` (`leerPreferencia` throwing storage → `system`) + `controlador-tema.test.ts` (failing write still applies theme) | ✅ COMPLIANT |
| WT-03 | Invalid stored value falls back to system | `tema.test.ts` (`leerPreferencia` invalid value → `system`) | ✅ COMPLIANT |
| WT-04 | No flash of the wrong theme on reload | `prepaint-tema.test.ts` (script/module parity) + `e2e/tema.e2e.ts:26` (class present at `DOMContentLoaded`, `#root` empty) | ✅ COMPLIANT |
| WT-05 | Second tab picks up the change | `e2e/tema.e2e.ts:75` (two `page.newPage()`, shared `storage`, escritorio: PASS) + `controlador-tema.test.ts` (storage-event listener, matching key and `null`) | ✅ COMPLIANT |
| WT-06 | Perfil control is keyboard-operable | `SelectorTema.test.tsx` (arrow-key nav via `user-event`, accessible name/state) + `PerfilPanel.test.tsx` | ✅ COMPLIANT |
| WT-06 | Sidebar shortcut is keyboard-operable | `SelectorTema.test.tsx` (compacto variant) + `app-shell-layout.test.tsx` (real route tree, `sidebarFooter`) | ✅ COMPLIANT |
| WT-06 | The two surfaces stay in sync | `SelectorTema.test.tsx` (two instances, same fake controller, click on one syncs the other) | ✅ COMPLIANT |
| WT-07 | Text/non-text pairings meet AA per theme | `contraste-tokens.test.ts` `describe.each(['light','dark'])` × `PARES_TEXTO`/`PARES_NO_TEXTO` (116 ratio assertions, both themes) | ✅ COMPLIANT |
| WT-07 | Pie label and focus indicator legible per theme | `contraste-tokens.test.ts` (pie-etiqueta-*, pie-separador pairs, both themes) + design.md flagged-item resolution (focus outline-ring / thickened separator) | ✅ COMPLIANT |
| WT-08 | Same bucket recognizable across themes | `bucket-colors.test.ts` (class helpers map same bucket→same hue family) + Token Table review (necesidades/gustos/ahorro/sin-categoria pairs share hue family light↔dark) | ✅ COMPLIANT |
| WT-08 | Ahorro stays most salient in both themes | `palette-measurements.md` salience data + DESIGN.md identity description ("Ahorro... el bucket más saliente"); no dedicated runtime assertion, static/measurement evidence only | ⚠️ PARTIAL |
| WT-09 | No color import in the view-model | `rg` on `src/domain/resumen-view-model.ts` imports: only `formatear-monto`, `porcentaje`, `../api/types` — no `bucket-colors`/`pie-colors`/theme hook | ✅ COMPLIANT |

**Compliance summary**: 17/18 WT scenarios COMPLIANT, 1/18 PARTIAL (WT-08 salience — measured/documented, not runtime-asserted).

### Spec Compliance Matrix — `web-app` (DCR-04..07, WCFG-02)

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| DCR-04 | App shell background resolves to Clínico frío | `contraste-tokens.test.ts` (`:root` `--background: #edf0f5` literal check) + `light-chrome.e2e.ts` | ✅ COMPLIANT |
| DCR-05 | Primary-styled elements pick up Clínico frío primary | `contraste-tokens.test.ts` (`--primary: #1d5fa8`) | ✅ COMPLIANT |
| DCR-06 | Documented pairings meet AA in both themes | `contraste-tokens.test.ts` full `PARES_TEXTO`/`PARES_NO_TEXTO` matrix, both themes (PR7b closed the deferred coverage) | ✅ COMPLIANT |
| DCR-07 | Dark mode renders Tinta cálida | `dark-chrome.e2e.ts` (card `rgb(34,33,30)` = `#22211E`) + `contraste-tokens.test.ts` `.dark` block | ✅ COMPLIANT |
| DCR-07 | Switching theme does not change layout structure | No dedicated DOM-structure-diff test found; inferred from D1 (class-only toggle, no conditional rendering) and zero structural changes across `dark-chrome`/`light-chrome` specs (same selectors, only computed style differs) | ⚠️ PARTIAL |
| WCFG-02 | Shared heading precedes panel heading | `PerfilPanel.test.tsx` (pre-existing, unaffected by this change) | ✅ COMPLIANT |
| WCFG-02 | Categorías tab is a real Link | `PerfilPanel.test.tsx` (pre-existing) | ✅ COMPLIANT |
| WCFG-02 | Four blocks render in fixed order, Guardar cambios scoped to first | `PerfilPanel.test.tsx` (updated Phase 10: order Editar perfil → Cuenta de Google → Apariencia → Sesión) | ✅ COMPLIANT |
| WCFG-02 | Apariencia applies instantly, no Guardar cambios | `PerfilPanel.test.tsx` + `SelectorTema.test.tsx` (no submit handler, instant `cambiarPreferencia`) | ✅ COMPLIANT |
| WCFG-02 | Linked state renders green pill + Desvincular | `PerfilPanel.test.tsx` (pre-existing, unaffected) | ✅ COMPLIANT |
| WCFG-02 | Not-linked state renders neutral pill + Vincular | `PerfilPanel.test.tsx` (pre-existing, unaffected) | ✅ COMPLIANT |

**Compliance summary**: 10/11 DCR/WCFG scenarios COMPLIANT, 1/11 PARTIAL (DCR-07 structure-invariance — inferred, not directly asserted by a DOM-diff test).

**Combined**: 27/29 COMPLIANT, 2/29 PARTIAL, 0/29 UNTESTED/FAILING.

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| WT-01..WT-09 | ✅ Implemented | `lib/tema.ts`, `lib/controlador-tema.ts`, `lib/use-preferencia-tema.ts`, `components/SelectorTema.tsx` |
| DCR-04..07 | ✅ Implemented | `index.css` `:root`/`.dark` blocks match design.md's Token Table exactly (spot-checked `--background`, `--primary`, `--destructive`, bucket hues) |
| WCFG-02 | ✅ Implemented | `PerfilPanel.tsx` four-block order; `Apariencia` description string present |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1 (`@theme` tokens stay, light default; `.dark` override) | ✅ Yes | Confirmed in `index.css`; ADR-043 §D1 |
| D2 (`color-scheme` per theme + inline style) | ✅ Yes | Script and `aplicarTema` both set `documentElement.style.colorScheme` |
| D3 (pie labels/separator as CSS token classes, not a theme-param function) | ✅ Yes — **deviation from proposal, recorded in ADR-043** | `claseEtiquetaPie`/`CLASE_SEPARADOR_PIE`; acceptable, matches design.md and does not break any spec |
| D4 (external store, factory + context default, no provider) | ✅ Yes | `crearControladorTema`, `use-preferencia-tema.ts` |
| D5 (inline classic script, parity-tested) | ✅ Yes | `index.html` script + `prepaint-tema.test.ts` |
| D6 (`error-foreground` split from `--destructive`) | ✅ Yes | 34+1 `text-destructive`/`text-red-600` sites migrated; `rg` confirms zero live usages remain (only 2 explanatory comments) |
| D7 (drop `dark:` variants from button/badge) | ✅ Yes | Confirmed via Phase 6.7/6.9 axe re-check |
| D8 (native-radio `SelectorTema`, per-instance `useId`) | ✅ Yes | `SelectorTema.tsx` |
| D9 (Apariencia its own `SeccionConfig`, this order) | ✅ Yes | `PerfilPanel.tsx` order matches |
| D10 (Sidebar shortcut via existing `sidebarFooter` slot, `Sidebar.tsx` untouched) | ✅ Yes | `_authenticated.tsx` only; `git diff` confirms `Sidebar.tsx` not in the changed-file list |

**Recorded task-wording deviations judged**:
- Phase 3 (bucket/pie class helpers added alongside hex, not replacing them yet): **Acceptable** — matches the plan's own Suggested Work Units row and avoids breaking consumers mid-PR; closed by Phase 4b.
- Phase 4 split into PR4a/PR4b (661 lines → two PRs): **Acceptable** — pure line-budget re-slice along a natural revert boundary (WT-09 import-check still closes, in PR4b); no scope was dropped.
- Phase 5 TDD order flip (write failing token/class assertions before the token/migration, RED-first on the assertion side): **Acceptable** — still a valid RED→GREEN cycle, just anchored on the assertion rather than the production change; explicitly authorized by "the orchestrator specified".
- Phase 6 curated 5-pair AA table instead of the full matrix (budget-scoped): **Acceptable and closed** — PR7b explicitly pays this debt; verified above (`contraste-tokens.test.ts` now runs the full matrix both themes).
- Phase 7 full-matrix light coverage deferred to PR7b: **Acceptable and closed**, same evidence.
- Phase 9 split into PR9a-d (1065 lines → four PRs) and `TEMA_FORZADO` applied inside `resolverTema` rather than per-caller: **Acceptable** — pure re-slice, and centralizing the forced-override in one function is a **safer** implementation than the design's per-caller wording (single source of truth, cannot leak `light` on any path).

No design deviation found that breaks a spec requirement.

### TDD Compliance
| Check | Result | Details |
|---|---|---|
| TDD Evidence reported | ✅ | `apply-progress` (Engram #1238) documents RED/GREEN cycles per task; `tasks.md` phase notes cross-confirm |
| All tasks have tests | ✅ | 58/58 tasks; every `[RED]`/`[GREEN]` pair has a corresponding test file change in the diff |
| RED confirmed (tests exist) | ✅ | All named test files (`tema.test.ts`, `controlador-tema.test.ts`, `prepaint-tema.test.ts`, `contraste-tokens.test.ts`, `SelectorTema.test.tsx`, `bucket-colors.test.ts`, `pie-colors.test.ts`, `PerfilPanel.test.tsx`, `app-shell-layout.test.tsx`) exist in the diff and in the working tree |
| GREEN confirmed (tests pass) | ✅ | 2109/2109 pass on this run |
| Triangulation adequate | ✅ | `tema.test.ts`/`controlador-tema.test.ts` cover the full preference×OS matrix (light/dark/system × OS-light/dark, explicit vs system, throwing storage); `contraste-tokens.test.ts` covers 116 distinct pairs |
| Safety Net for modified files | ✅ | `apply-progress` reports full-suite green re-runs (1871, 1938, 2109 progressively) at each PR boundary, not just the touched files |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|---|---|---|---|
| Unit | ~2050 | ~145 | Vitest |
| Integration/Component | ~59 (SelectorTema, PerfilPanel, app-shell-layout, DistribucionPie, etc.) | ~10 | Vitest + Testing Library |
| E2E | 7 theme-specific (`tema.e2e.ts` ×3, `dark-chrome.e2e.ts` ×2, `light-chrome.e2e.ts` ×2) of 56 total in the suite | 3 theme files of ~20 e2e files | Playwright |
| **Total** | **2109 unit/component + 56 e2e (37 run under `--project=escritorio`, 19 pre-existing unrelated skips)** | | |

### Assertion Quality
✅ All assertions verify real behavior — no tautologies found (`rg "expect(true).toBe(true)"` empty); mock/assertion ratios spot-checked (`controlador-tema.test.ts`: 7 mocks / 27 assertions, well under the 2× threshold); no ghost-loop or smoke-test-only patterns observed in the theme-specific test files reviewed.

### Quality Metrics
**Linter**: ✅ No errors (`pnpm web lint`, exit 0)
**Type Checker**: ✅ No errors (`pnpm web typecheck`, exit 0)

### Issues Found

**CRITICAL**:
1. PR #650 (chain tip) CI is RED on the `movil` (360px) Playwright project: 3 failing specs in `apps/web/e2e/tema.e2e.ts` (lines 26/57/75) navigate to the dashboard and query the Sidebar-footer radios, which are desktop-only by WT-06 and are absent from the DOM subtree these tests reach at mobile width. Diagnosis: a **test-authoring scope defect** (the spec was written/verified only against `escritorio`), not a product or spec violation — no requirement promises a mobile Sidebar shortcut, and WCFG-02/WT-06 both name Configuración as the mobile path. This blocks merge under branch protection and must be fixed (navigate to `/configuracion`, scope locators to the Apariencia block, guard against strict-mode duplicate-role matches from the two on-screen selectors at desktop widths) before this change can be archived. Not fixed here per instructions (no code modification in verify).

**WARNING**:
1. WT-08's "Ahorro stays most salient in both themes" scenario has no runtime/unit assertion — it is backed only by `palette-measurements.md`'s salience data and DESIGN.md's prose. Low risk (values are measured, not guessed) but a `contraste-tokens.test.ts`-style chroma/contrast comparison would close the gap.
2. DCR-07's "switching theme does not change layout structure" scenario has no dedicated DOM-structure-diff test; the claim rests on D1's class-only-toggle architecture (no conditional rendering) plus the absence of any structural failure in `dark-chrome.e2e.ts`/`light-chrome.e2e.ts`. Acceptable given the architecture, but a `toMatchSnapshot` on structure-only (stripped of style) would make this scenario independently verifiable.
3. `openspec/specs/web-dashboard-shell/spec.md` line 197 still lists "Dark mode." under Non-Goals, and the live `openspec/specs/web-app/spec.md` WCFG-02 still describes the pre-change three-block Perfil layout. Both are expected staging artifacts — the change's own delta specs (`specs/web-theme/spec.md`, `specs/web-app/spec.md` in this change folder) are what supersede them, and archival is what applies the delta to the live specs. Flagged so `sdd-archive` does not skip the `web-dashboard-shell` manual edit (it lives outside this change's own delta and needs explicit attention at archive time).

**SUGGESTION**:
1. Mobile-width users reach the theme toggle only via Configuración → Perfil → Apariencia (no Sidebar shortcut below the desktop breakpoint) — this matches WT-06's explicit "(desktop)" scoping and is not a defect, just worth a one-line callout in the eventual PR/release notes so it isn't rediscovered as a "missing feature."
2. Consider adding a Playwright `movil`-project smoke test for the Apariencia flow specifically (reached via Configuración) once the current CRITICAL fix lands, so mobile theme-switching has its own explicit e2e coverage rather than only unit/component coverage.

### Verdict
**FAIL** — every command this verify was scoped to run (`pnpm web test`, `typecheck`, `lint`, `build`, `playwright --project=escritorio`) passed cleanly (2109/2109 tests, 0 type/lint errors, build OK, 37/37 e2e escritorio), and 27/29 spec scenarios are directly test-compliant with 2/29 acceptable PARTIAL (documented, low-risk); however, the chain-tip PR (#650) carries a CRITICAL, merge-blocking CI failure on the `movil` Playwright project (test-scope defect in `tema.e2e.ts`, not a spec/product violation) that must be resolved before `sdd-archive`.
