```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:4e9d31a04c0099c6555387b6db7a1743492ec7dcd7b4f6c1067ee6a733cf5445
verdict: pass
blockers: 0
critical_findings: 0
requirements: 14/14
scenarios: 29/29
test_command: pnpm web test
test_exit_code: 0
test_output_hash: sha256:12fc23312b6c8363c7faff64e81449a7ac04cdb60e21c3941d278d21f4a9146c
build_command: pnpm web build
build_exit_code: 0
build_output_hash: sha256:b73bbc056217624ec7e0f80ae9dc6468d35c1aad116b4875531e02fd445fd188
```

## Verification Report

**Change**: web-theme-switch
**Version**: chain tip `feat/tema-selector-sidebar-e2e` @ `52201440` (16 PRs, tracker `feat/web-theme-switch` still = `main`)
**Mode**: Strict TDD — RE-VERIFY after remediation

### Previous run

The first verify (evidence `sha256:cbed449f68692518287e40367375ce071486a5ed252d8e3f0bb049da225dbb88`, commit `eed2ee5a`) returned **FAIL** with a single CRITICAL: PR #650 CI was RED on the Playwright `movil` (360px) project. `apps/web/e2e/tema.e2e.ts` navigated to the dashboard and queried the Sidebar-footer radios, which are desktop-only by WT-06 and absent from the DOM subtree at mobile width. Diagnosis was a **test-authoring scope defect**, not a product/spec violation. Everything else in that run (unit tests, typecheck, lint, build, `escritorio` Playwright project, all 27/29 COMPLIANT + 2/29 acceptable PARTIAL spec scenarios) already passed.

### What changed since

Commit `52201440` (PR #650) rewrote `apps/web/e2e/tema.e2e.ts` to navigate to `/configuracion` and scope every radio lookup to the Perfil `Apariencia` `SeccionConfig` (`seccionApariencia()` locator, filtered by its heading), instead of using the Sidebar shortcut. This section renders at every viewport (unlike the sidebar footer, which WT-06 scopes to desktop), so the same three specs now run and pass identically across `movil`, `tablet`, and `escritorio`.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 58 |
| Tasks complete | 58 |
| Tasks incomplete | 0 |

Unchanged from the previous run — no task-list edits accompanied this fix; PR #650 is a delivered-but-corrected task-11 artifact (the e2e test file itself), not a new task.

### Build & Tests Execution — re-run in full this pass

**Build**: PASS
```text
$ pnpm web build
tsr generate && tsc -b && vite build
✓ built in 265ms  (exit 0)
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
  Duration  19.35s   (exit 0)
```

**Playwright (all projects — movil, tablet, escritorio — from `apps/web`)**: PASS — 99 passed, 69 skipped (pre-existing, unrelated breakpoint-scoped specs), 0 failed
```text
$ FORCE_COLOR=0 pnpm exec playwright test
  99 passed (14.6s)
  69 skipped
tema.e2e.ts — movil:      ✓ WT-03/WT-04 (reload, no-flash)  ✓ WT-02 (live OS)  ✓ WT-05 (cross-tab)
tema.e2e.ts — tablet:     ✓ WT-03/WT-04 (reload, no-flash)  ✓ WT-02 (live OS)  ✓ WT-05 (cross-tab)
tema.e2e.ts — escritorio: ✓ WT-03/WT-04 (reload, no-flash)  ✓ WT-02 (live OS)  ✓ WT-05 (cross-tab)
dark-chrome.e2e.ts — tablet/escritorio: ✓ color-scheme dark  ✓ native <select> dark face
light-chrome.e2e.ts — tablet/escritorio: ✓ color-scheme light  ✓ native <select> Clínico frío face
```
Exit code: 0. This is the CRITICAL-closing evidence: all three viewport projects (`movil`, `tablet`, `escritorio`) now run and pass `tema.e2e.ts`'s three specs — 9/9 theme e2e runs green, where the previous run only exercised `escritorio` (37 passed) and left `movil`/`tablet` unrun locally (and RED in CI).

**Coverage**: Not run — no coverage flag configured in this project's `test` script; not required by `openspec/config.yaml`. ➖ Not available.

**CI status on PR #650 (chain tip, `gh pr checks 650`, reproduced by this verify)**: **CLEAN**. All required checks pass: `E2E (Playwright, web)` pass (1m33s), `Typecheck & unit tests (web)` pass (3m15s), `SAST (Semgrep)` pass, `Security (audit + secrets)` pass, `Commitlint` pass, `CodeQL` pass ×2, `Validate openspec change artifacts` pass, `CI success` pass. Zero open CodeQL alerts. No failing or skipped-but-required job. This closes the previous CRITICAL: the CI red the first verify reported no longer reproduces — the `movil` project's three specs that were failing now pass on both the CI-run PR #650 and this local re-run.

### WT-02/WT-04/WT-05 runtime-scenario re-check (targeted, per instruction #1)

Read `apps/web/e2e/tema.e2e.ts` in full (post-fix). Confirmed all three runtime scenarios are still proven, and now proven identically on every viewport project (no longer `escritorio`-only):

| Scenario | Test | Evidence |
|---|---|---|
| WT-04 — no flash of wrong theme on reload, class present at `DOMContentLoaded` | `elegir Oscuro persiste tras el reload...` (lines 44–77) | `page.reload({ waitUntil: 'domcontentloaded' })` then reads `documentElement.classList`, `colorScheme`, and asserts `#root` has zero children at that instant (lines 62–70) — same assertion shape as the prior pass, now run on movil/tablet/escritorio |
| WT-02 — live OS change updates system-mode theme without reload | `bajo preferencia system, un cambio de OS en vivo...` (lines 79–97) | `page.emulateMedia({colorScheme})` toggled light→dark→light, asserting the `dark` class follows live, no navigation in between |
| WT-05 — cross-tab: change in one tab reaches the other via storage | `cross-tab: cambiar el tema en una pestaña...` (lines 99–121) | two real `page.newPage()` instances sharing `context` storage; change on page A asserted to reach page B's `html` class and its own radio `checked` state |

The locator change (`seccionApariencia()`, scoped by the `Apariencia` heading, `.check({force:true})` on the underlying `sr-only` radio) is a **test-authoring fix only** — it does not touch `lib/tema.ts`, `lib/controlador-tema.ts`, `lib/use-preferencia-tema.ts`, or `components/SelectorTema.tsx`. `git diff main...feat/tema-selector-sidebar-e2e -- apps/web/src` confirms zero production changes landed after the previous verify; only the e2e spec file changed. No new spec risk introduced.

### Spec Compliance Matrix — unchanged from previous run

Re-confirmed by this run's execution (no spec text changed, no requirement/scenario count changed: 14/14 requirements, 29/29 scenarios — recount matches: `web-theme/spec.md` 9 req/18 scenarios + `web-app/spec.md` 5 req/11 scenarios = 14/29).

**`web-theme` (WT-01..WT-09)**: 17/18 COMPLIANT, 1/18 PARTIAL (WT-08 salience — measured/documented via `palette-measurements.md`, not runtime-asserted; unchanged, low risk).

**`web-app` (DCR-04..07, WCFG-02)**: 10/11 COMPLIANT, 1/11 PARTIAL (DCR-07 layout-invariance — inferred from D1's class-only-toggle architecture and the absence of structural failures across `dark-chrome`/`light-chrome` specs; unchanged, low risk).

**Combined**: 27/29 COMPLIANT, 2/29 PARTIAL, 0/29 UNTESTED/FAILING — identical ratio to the previous run; the fix did not change scenario coverage, it restored coverage that was already claimed but unverified on two of three viewports.

### Correctness (Static Evidence) — unchanged
| Requirement | Status | Notes |
|---|---|---|
| WT-01..WT-09 | ✅ Implemented | `lib/tema.ts`, `lib/controlador-tema.ts`, `lib/use-preferencia-tema.ts`, `components/SelectorTema.tsx` — no changes since previous verify |
| DCR-04..07 | ✅ Implemented | `index.css` `:root`/`.dark` blocks match design.md's Token Table |
| WCFG-02 | ✅ Implemented | `PerfilPanel.tsx` four-block order; `Apariencia` description string present |

### Coherence (Design) — unchanged

All 10 design decisions (D1–D10) hold as recorded in the previous report; the e2e fix does not touch any of them (it only changes which locator the *test* uses to reach the already-existing `Apariencia` `SelectorTema` instance).

### TDD Compliance
| Check | Result | Details |
|---|---|---|
| TDD Evidence reported | ✅ | Unchanged; `apply-progress` (Engram #1238) documents RED/GREEN per task |
| All tasks have tests | ✅ | 58/58 tasks |
| RED confirmed (tests exist) | ✅ | All named test files exist in the working tree, including the corrected `tema.e2e.ts` |
| GREEN confirmed (tests pass) | ✅ | 2109/2109 unit/component tests pass; 99/99 non-skipped Playwright specs pass across all 3 projects |
| Triangulation adequate | ✅ | Unchanged from previous run |
| Safety Net for modified files | ✅ | Full local suite (`pnpm web test`) + full Playwright suite re-run green after the PR #650 fix, not just the touched spec file |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|---|---|---|---|
| Unit | ~2050 | ~145 | Vitest |
| Integration/Component | ~59 | ~10 | Vitest + Testing Library |
| E2E | 9 theme-specific specs × 3 viewport projects run = 9 passing theme runs (of 168 total collected, 99 run, 69 skipped) | 3 theme files | Playwright |
| **Total** | **2109 unit/component + 99 e2e passed (0 failed, 69 skipped-by-design)** | | |

### Assertion Quality
✅ All assertions verify real behavior — no tautologies found; the corrected `tema.e2e.ts` adds a documented rationale comment for `.check({force:true})` (sr-only radios shadow each other's hit-target) rather than weakening an assertion. No ghost-loop or smoke-test-only patterns.

### Quality Metrics
**Linter**: ✅ No errors (`pnpm web lint`, exit 0)
**Type Checker**: ✅ No errors (`pnpm web typecheck`, exit 0)

### Issues Found

**CRITICAL**: None. The previous CRITICAL (PR #650 CI red on `movil` Playwright project) is resolved: `apps/web/e2e/tema.e2e.ts` now reaches the theme toggle through the viewport-independent `Apariencia` section instead of the desktop-only Sidebar shortcut. Verified both locally (all 3 Playwright projects green, 99/99 non-skipped passed) and on CI (`gh pr checks 650` clean, all required checks pass, 0 open CodeQL alerts).

**WARNING** (carried over, unchanged, both still acceptable low-risk gaps):
1. WT-08's "Ahorro stays most salient in both themes" scenario has no runtime/unit assertion — backed only by `palette-measurements.md`'s salience data and DESIGN.md's prose.
2. DCR-07's "switching theme does not change layout structure" scenario has no dedicated DOM-structure-diff test; the claim rests on D1's class-only-toggle architecture plus the absence of structural failures in `dark-chrome`/`light-chrome` specs.
3. `openspec/specs/web-dashboard-shell/spec.md` line 197 still lists "Dark mode." under Non-Goals, and the live `openspec/specs/web-app/spec.md` WCFG-02 still describes the pre-change three-block Perfil layout. Both are expected staging artifacts that `sdd-archive`'s delta application resolves — flagged again so archive does not skip the `web-dashboard-shell` manual edit.

**SUGGESTION** (carried over, unchanged):
1. Mobile-width users reach the theme toggle only via Configuración → Perfil → Apariencia (no Sidebar shortcut below the desktop breakpoint) — matches WT-06's explicit "(desktop)" scoping; worth a one-line callout in release notes.
2. The mobile e2e gap the previous run flagged as a follow-up ("add a Playwright `movil`-project test for the Apariencia flow") is now moot — PR #650 made `tema.e2e.ts` itself run and pass on `movil`. No further action needed here.

### Verdict
**PASS** — every command this re-verify ran (`pnpm web test`, `typecheck`, `lint`, `build`, `playwright test` all 3 projects) passed cleanly (2109/2109 unit/component tests, 0 type/lint errors, build OK, 99/99 non-skipped Playwright specs across movil/tablet/escritorio, 0 failed), PR #650 CI is confirmed CLEAN on all required checks including the previously-red `movil` E2E job, and all 16 chain PRs (#635–#650) are CLEAN. 27/29 spec scenarios are directly test-compliant with 2/29 acceptable PARTIAL (documented, low-risk, unchanged from the prior run). The chain is **ready to merge** and this change is **ready for `sdd-archive`**, subject to the two archive-time follow-ups already on record: the `web-dashboard-shell` "Dark mode." Non-Goal bullet, and the live `web-app` spec's pre-change WCFG-02 description (both resolved by the delta-spec application archive performs, not by further verify work).
